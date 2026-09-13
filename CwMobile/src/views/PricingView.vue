<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
import {
  usePricingStore,
} from '@/stores/pricing'
import {
  pricingCategoryApi,
  pricingSubCategoryApi,
} from '@/services/api'
import type {
  Pricing,
  PricingCreate,
  PricingUpdate,
  PricingCategory,
  PricingSubCategory,
} from '@/types'
import PricingForm from '@/components/PricingForm.vue'
import CascaderPicker from '@/components/CascaderPicker.vue'
import { useI18n } from 'vue-i18n'
import { useCurrencyStore } from '@/stores/currency'

const currencyStore = useCurrencyStore()
const { t } = useI18n()

const store = usePricingStore()

const showManager = ref(false)
const showPicker = ref(false)
const showForm = ref(false)
const editingItem = ref<Pricing | null>(null)
const searchQuery = ref('')

const categories = ref<PricingCategory[]>([])
const subsByCat = ref<Record<number, PricingSubCategory[]>>({})
const activeCatId = ref<number | null>(null)
const selectedCatId = ref<number | null>(null)
const selectedSubId = ref<number | null>(null)
const catLoading = ref(false)

const showNameForm = ref(false)
const nameKind = ref<'category' | 'sub'>('category')
const nameFormTitle = ref('')
const editingCat = ref<PricingCategory | null>(null)
const editingSub = ref<PricingSubCategory | null>(null)
const nameValue = ref('')

const selectedCatName = computed(() => {
  const cat = categories.value.find((c) => c.id === selectedCatId.value)
  return cat ? cat.name : ''
})

const selectedSubName = computed(() => {
  const list = selectedCatId.value ? (subsByCat.value[selectedCatId.value] ?? []) : []
  const sub = list.find((s) => s.id === selectedSubId.value)
  return sub ? sub.name : ''
})

const contextLabel = computed(() => {
  if (selectedSubId.value) return `${selectedCatName.value} / ${selectedSubName.value}`
  if (selectedCatId.value) return selectedCatName.value
  return t('app.pricing.allPricing')
})

const subListOfActive = computed(() => {
  const catId = activeCatId.value
  return catId === null ? [] : (subsByCat.value[catId] ?? [])
})

watch(searchQuery, (q) => {
  store.fetchAll(q ? { q } : {})
})

onMounted(() => {
  store.fetchAll()
  refreshCategories()
})

async function refreshCategories() {
  catLoading.value = true
  try {
    categories.value = await pricingCategoryApi.getAll()
  } catch (e: any) {
    showToast(e.message || t('app.stores.fetchCategoryFailed'))
  } finally {
    catLoading.value = false
  }
}

async function loadSubs(catId: number) {
  try {
    subsByCat.value[catId] = await pricingSubCategoryApi.getAll(catId)
  } catch (e: any) {
    showToast(e.message || t('app.stores.fetchSubCategoryFailed'))
  }
}

function openManager() {
  activeCatId.value = null
  refreshCategories()
  showManager.value = true
}

function toggleCat(catId: number) {
  activeCatId.value = catId
  if (!subsByCat.value[catId]) loadSubs(catId)
}

function pickSub(sub: PricingSubCategory) {
  selectedCatId.value = sub.category_id
  selectedSubId.value = sub.id
  showManager.value = false
  store.fetchAll({ sub_category_id: sub.id })
}

function pickAll() {
  selectedCatId.value = null
  selectedSubId.value = null
  activeCatId.value = null
  showManager.value = false
  store.fetchAll()
}

const pickerCategories = computed(() =>
  categories.value.map((c) => ({ text: c.name, value: c.id }))
)

function pickerSubsOf(catId: number) {
  return (subsByCat.value[catId] ?? []).map((s) => ({
    text: s.name,
    value: s.id,
  }))
}

async function openPicker() {
  if (!categories.value.length) await refreshCategories()
  await Promise.all(categories.value.map((c) => loadSubs(c.id)))
  showPicker.value = true
}

function onPickerConfirm(r: { categoryId: number; subId: number | null }) {
  if (r.subId === null) {
    showToast(t('app.pricing.pickSubCategory'))
    return
  }
  selectedCatId.value = r.categoryId
  selectedSubId.value = r.subId
  store.fetchAll({ sub_category_id: r.subId })
}

function clearFilter() {
  selectedCatId.value = null
  selectedSubId.value = null
  store.fetchAll()
}

function openAddName() {
  editingCat.value = null
  editingSub.value = null
  nameKind.value = 'category'
  nameFormTitle.value = t('app.pricing.addCategory')
  nameValue.value = ''
  showNameForm.value = true
}

function openAddSub(catId: number) {
  editingCat.value = null
  editingSub.value = null
  nameKind.value = 'sub'
  nameFormTitle.value = t('app.pricing.addSubCategory')
  nameValue.value = ''
  showNameForm.value = true
}

function openEditCat(cat: PricingCategory) {
  editingCat.value = cat
  nameKind.value = 'category'
  nameFormTitle.value = t('app.pricing.editCategory')
  nameValue.value = cat.name
  showNameForm.value = true
}

function openEditSub(sub: PricingSubCategory) {
  editingSub.value = sub
  nameKind.value = 'sub'
  nameFormTitle.value = t('app.pricing.editSubCategory')
  nameValue.value = sub.name
  showNameForm.value = true
}

async function submitName() {
  const name = nameValue.value.trim()
  if (!name) {
    showToast(t('app.common.inputName'))
    return
  }
  if (nameKind.value === 'category') {
    if (editingCat.value) {
      await pricingCategoryApi.update(editingCat.value.id, { name })
    } else {
      await pricingCategoryApi.create({ name })
    }
    await refreshCategories()
  } else if (editingSub.value) {
    const s = editingSub.value
    await pricingSubCategoryApi.update(s.id, { name })
    await loadSubs(s.category_id)
  } else if (activeCatId.value) {
    await pricingSubCategoryApi.create({ category_id: activeCatId.value, name })
    await loadSubs(activeCatId.value)
  }
  showNameForm.value = false
}

async function askDeleteCat(cat: PricingCategory) {
  try {
    await showConfirmDialog({
      title: t('app.pricing.deleteCategory'),
      message: t('app.pricing.deleteCategoryConfirm', { name: cat.name }),
      confirmButtonText: t('app.common.remove'),
      confirmButtonColor: '#ee0a24',
    })
  } catch {
    return
  }
  await pricingCategoryApi.delete(cat.id)
  delete subsByCat.value[cat.id]
  if (selectedCatId.value === cat.id) {
    selectedCatId.value = null
    selectedSubId.value = null
    store.fetchAll()
  }
  await refreshCategories()
}

async function askDeleteSub(sub: PricingSubCategory) {
  try {
    await showConfirmDialog({
      title: t('app.pricing.deleteSubCategory'),
      message: t('app.pricing.deleteSubCategoryConfirm', { name: sub.name }),
      confirmButtonText: t('app.common.remove'),
      confirmButtonColor: '#ee0a24',
    })
  } catch {
    return
  }
  await pricingSubCategoryApi.delete(sub.id)
  const list = subsByCat.value[sub.category_id]
  if (list) {
    subsByCat.value[sub.category_id] = list.filter((s) => s.id !== sub.id)
  }
  if (selectedSubId.value === sub.id) {
    selectedSubId.value = null
    store.fetchAll()
  }
}

function handleAdd() {
  if (!selectedSubId.value) {
    showToast(t('app.pricing.pickSubCategoryFirst'))
    return
  }
  editingItem.value = null
  showForm.value = true
}

function handleEdit(item: Pricing) {
  editingItem.value = item
  showForm.value = true
}

async function askDelete(item: Pricing) {
  try {
    await showConfirmDialog({
      title: t('app.pricing.deleteRecord'),
      message: t('app.pricing.deleteRecordConfirm', { name: item.name }),
      confirmButtonText: t('app.common.remove'),
      confirmButtonColor: '#ee0a24',
    })
  } catch {
    return
  }
  await store.remove(item.id)
}

async function handleSubmit(data: {
  name: string
  cost: number
  suggested_price: number
  discount: number
  description: string
  notes: string
}) {
  if (editingItem.value) {
    await store.update(
      editingItem.value.id,
      data as unknown as PricingUpdate
    )
  } else if (selectedSubId.value) {
    await store.create({
      sub_category_id: selectedSubId.value,
      ...data,
    } as unknown as PricingCreate)
  }
}

function fmtDate(s: string | null): string {
  return s ? new Date(s).toLocaleDateString() : '-'
}
</script>

<template>
  <div class="pv">
    <van-nav-bar :title="t('app.pricing.title')">
      <template #left>
        <van-icon name="apps-o" size="20" @click="openManager" />
      </template>
      <template #right>
        <van-icon name="plus" class="plus" @click="handleAdd" />
      </template>
    </van-nav-bar>

    <div class="page-body">
    <div class="ctx">
      <div class="ctx-main" @click="openPicker">
        <span class="ctx-text">{{ contextLabel }}</span>
        <van-icon name="arrow-down" size="14" color="var(--van-text-color-2)" />
      </div>
      <van-icon
        v-if="selectedSubId || selectedCatId"
        name="cross"
        size="16"
        color="var(--van-text-color-2)"
        @click="clearFilter"
      />
    </div>

    <div class="search">
      <van-field
        v-model="searchQuery"
        clearable
        :placeholder="t('app.pricing.searchPlaceholder')"
      />
    </div>

    <div class="list">
      <van-loading v-if="store.loading" class="tip" vertical>
        {{ t('app.common.loading') }}
      </van-loading>
      <van-empty
        v-else-if="!store.items.length"
        :description="t('app.pricing.noRecords')"
      />
      <div v-else class="pv-cards">
        <van-swipe-cell v-for="item in store.items" :key="item.id" class="pv-swipe">
          <van-cell clickable @click="handleEdit(item)">
            <template #title>
              <div class="item-title">{{ item.name }}</div>
              <div class="item-sub">{{ item.sub_category_name || '-' }}</div>
              <div class="item-meta">
                {{ t('app.pricing.costSuggestedPrice', {
                  symbol: currencyStore.symbol,
                  cost: item.cost.toFixed(2),
                  suggested: item.suggested_price.toFixed(2),
                  discount: item.discount,
                }) }}
              </div>
              <div v-if="item.description" class="item-meta">
                {{ item.description }}
              </div>
              <div class="item-meta">
                {{ t('app.pricing.recordedOn', { date: fmtDate(item.record_date) }) }}
              </div>
            </template>
          </van-cell>
          <template #right>
            <van-button
              square
              type="danger"
              :text="t('app.common.remove')"
              class="del-btn"
              @click="askDelete(item)"
            />
          </template>
        </van-swipe-cell>
      </div>
    </div>
    </div>

    <PricingForm
      v-model:visible="showForm"
      :edit-data="editingItem"
      @submit="handleSubmit"
    />

    <CascaderPicker
      v-model:show="showPicker"
      :title="t('app.pricing.pickCategory')"
      :categories="pickerCategories"
      :subs-of="pickerSubsOf"
      :initial-category-id="selectedCatId ?? undefined"
      :initial-sub-id="selectedSubId ?? undefined"
      @confirm="onPickerConfirm"
    />

    <van-popup
      :show="showManager"
      position="left"
      :style="{ width: '86%', height: '100%' }"
      @update:show="showManager = $event"
    >
      <div class="mgr">
        <van-nav-bar
          :title="t('app.pricing.categoryTitle')"
          left-arrow
          @click-left="showManager = false"
        >
          <template #right>
            <van-icon name="plus" class="mgr-plus" @click="openAddName" />
          </template>
        </van-nav-bar>
        <div class="mgr-body">
          <van-cell :title="t('app.pricing.allPricing')" is-link @click="pickAll" />
          <van-loading v-if="catLoading" class="tip" />
          <van-empty
            v-else-if="!categories.length"
            :description="t('app.pricing.noCategories')"
          />
          <van-cell-group v-else inset>
            <div v-for="cat in categories" :key="cat.id">
              <van-cell
                :title="cat.name"
                :class="{ active: selectedCatId === cat.id && !selectedSubId }"
                clickable
                @click="toggleCat(cat.id)"
              >
                <template #right-icon>
                  <span class="cat-ops" @click.stop>
                    <van-icon name="plus" @click.stop="openAddSub(cat.id)" />
                    <van-icon name="edit" @click.stop="openEditCat(cat)" />
                    <van-icon name="delete-o" @click.stop="askDeleteCat(cat)" />
                  </span>
                </template>
              </van-cell>
              <div v-if="activeCatId === cat.id" class="subs">
                <van-empty
                  v-if="!subListOfActive.length"
                  :description="t('app.pricing.noSubCategories')"
                />
                <van-cell
                  v-for="sub in subListOfActive"
                  :key="sub.id"
                  :title="sub.name"
                  :class="{ active: selectedSubId === sub.id }"
                  clickable
                  @click="pickSub(sub)"
                >
                  <template #right-icon>
                    <span class="sub-ops" @click.stop>
                      <van-icon name="edit" @click.stop="openEditSub(sub)" />
                      <van-icon name="delete-o" @click.stop="askDeleteSub(sub)" />
                    </span>
                  </template>
                </van-cell>
              </div>
            </div>
          </van-cell-group>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showNameForm" position="bottom" round>
      <div class="nameform">
        <van-nav-bar
          :title="nameFormTitle"
          :left-text="t('app.common.cancel')"
          :right-text="t('app.common.save')"
          @click-left="showNameForm = false"
          @click-right="submitName"
        />
        <van-cell-group inset class="name-body">
          <van-field
            v-model="nameValue"
            :label="t('app.common.name')"
            :placeholder="t('app.common.inputName')"
          />
        </van-cell-group>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.pv {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0 var(--tabbar-height);
}

.plus {
  font-size: 22px;
  color: var(--van-primary-color);
}

.ctx {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 14px 8px;
  padding: 10px 12px;
  background: var(--van-background-2);
  border-radius: 10px;
}

.ctx-main {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  cursor: pointer;
}

.ctx-text {
  flex: 1;
  font-size: 15px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.search {
  margin: 0 14px;
}

.list {
  margin-top: 10px;
}

.item-title {
  font-weight: 600;
}

.item-sub,
.item-meta {
  color: var(--van-text-color-2);
  font-size: 12px;
  margin-top: 2px;
}

.pv-cards {
  padding: 0 12px;
}

.pv-swipe {
  margin-bottom: 8px;
  border-radius: 10px;
  overflow: hidden;
}

.del-btn {
  height: 100%;
}

.tip {
  padding-top: 40px;
}

.mgr {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.mgr-plus {
  font-size: 20px;
}

.mgr-body {
  flex: 1;
  overflow-y: auto;
  padding-top: 8px;
}

.cat-ops,
.sub-ops {
  display: inline-flex;
  gap: 14px;
  color: var(--van-text-color-2);
  font-size: 16px;
}

.subs {
  padding-left: 12px;
  background: var(--van-background-2);
}

.active :deep(.van-cell__title) {
  color: var(--van-primary-color);
}

.nameform {
  padding-bottom: 8px;
}

.name-body {
  margin-top: 8px;
}
</style>
