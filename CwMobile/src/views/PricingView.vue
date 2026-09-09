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

const store = usePricingStore()

const showManager = ref(false)
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
  return '全部售价'
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
    showToast(e.message || '获取分类失败')
  } finally {
    catLoading.value = false
  }
}

async function loadSubs(catId: number) {
  try {
    subsByCat.value[catId] = await pricingSubCategoryApi.getAll(catId)
  } catch (e: any) {
    showToast(e.message || '获取子分类失败')
  }
}

function openManager() {
  selectedCatId.value = null
  activeCatId.value = null
  selectedSubId.value = null
  store.fetchAll()
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

function openAddName() {
  editingCat.value = null
  editingSub.value = null
  nameKind.value = 'category'
  nameFormTitle.value = '新增售价分类'
  nameValue.value = ''
  showNameForm.value = true
}

function openAddSub(catId: number) {
  editingCat.value = null
  editingSub.value = null
  nameKind.value = 'sub'
  nameFormTitle.value = '新增售价子分类'
  nameValue.value = ''
  showNameForm.value = true
}

function openEditCat(cat: PricingCategory) {
  editingCat.value = cat
  nameKind.value = 'category'
  nameFormTitle.value = '编辑售价分类'
  nameValue.value = cat.name
  showNameForm.value = true
}

function openEditSub(sub: PricingSubCategory) {
  editingSub.value = sub
  nameKind.value = 'sub'
  nameFormTitle.value = '编辑售价子分类'
  nameValue.value = sub.name
  showNameForm.value = true
}

async function submitName() {
  const name = nameValue.value.trim()
  if (!name) {
    showToast('请输入名称')
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
      title: '删除售价分类',
      message: `确定删除「${cat.name}」及子分类吗？`,
      confirmButtonText: '删除',
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
      title: '删除售价子分类',
      message: `确定删除「${sub.name}」吗？`,
      confirmButtonText: '删除',
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
    showToast('请先选择售价子分类')
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
      title: '删除售价记录',
      message: `确定删除「${item.name}」吗？`,
      confirmButtonText: '删除',
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
    <div class="pv-head">
      <div class="pv-title">售价管理</div>
      <van-icon name="plus" class="plus" @click="handleAdd" />
    </div>

    <div class="ctx" @click="showManager = true">
      <span class="ctx-text">{{ contextLabel }}</span>
      <van-icon name="apps-o" size="16" color="#1989fa" />
    </div>

    <div class="search">
      <van-field
        v-model="searchQuery"
        clearable
        placeholder="搜索商品名/描述"
      />
    </div>

    <div class="list">
      <van-loading v-if="store.loading" class="tip" vertical>加载中</van-loading>
      <van-empty
        v-else-if="!store.items.length"
        description="暂无售价记录"
      />
      <van-cell-group v-else inset>
        <van-cell
          v-for="item in store.items"
          :key="item.id"
          clickable
          @click="handleEdit(item)"
        >
          <template #title>
            <div class="item-title">{{ item.name }}</div>
            <div class="item-sub">{{ item.sub_category_name || '-' }}</div>
            <div class="item-meta">
              成本 ¥{{ item.cost.toFixed(2) }} · 建议售价
              ¥{{ item.suggested_price.toFixed(2) }} · 折扣
              {{ item.discount }}
            </div>
            <div v-if="item.description" class="item-meta">
              {{ item.description }}
            </div>
            <div class="item-meta">
              记录日期 {{ fmtDate(item.record_date) }}
            </div>
          </template>
          <template #value>
            <div class="ops">
              <van-icon name="delete-o" @click.stop="askDelete(item)" />
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <PricingForm
      v-model:visible="showForm"
      :edit-data="editingItem"
      @submit="handleSubmit"
    />

    <van-popup
      :show="showManager"
      position="left"
      :style="{ width: '86%', height: '100%' }"
      @update:show="showManager = $event"
    >
      <div class="mgr">
        <van-nav-bar title="售价分类" left-arrow @click-left="showManager = false">
          <template #right>
            <van-icon name="plus" class="mgr-plus" @click="openAddName" />
          </template>
        </van-nav-bar>
        <div class="mgr-body">
          <van-cell title="全部售价" is-link @click="pickAll" />
          <van-loading v-if="catLoading" class="tip" />
          <van-empty
            v-else-if="!categories.length"
            description="暂无售价分类"
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
                  description="暂无子分类"
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
          left-text="取消"
          right-text="保存"
          @click-left="showNameForm = false"
          @click-right="submitName"
        />
        <van-cell-group inset class="name-body">
          <van-field
            v-model="nameValue"
            label="名称"
            placeholder="请输入名称"
          />
        </van-cell-group>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.pv {
  padding: 12px 0 90px;
}

.pv-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px;
}

.pv-title {
  font-size: 20px;
  font-weight: 700;
}

.plus {
  font-size: 22px;
  color: #1989fa;
  padding: 4px;
}

.ctx {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 14px 8px;
  padding: 10px 12px;
  background: #fff;
  border-radius: 10px;
}

html.dark .ctx {
  background: #1c1c1e;
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
  color: #969799;
  font-size: 12px;
  margin-top: 2px;
}

.ops {
  color: #c8c9cc;
  font-size: 18px;
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
  color: #969799;
  font-size: 16px;
}

.subs {
  padding-left: 12px;
  background: #fafafa;
}

html.dark .subs {
  background: #1c1c1e;
}

.active :deep(.van-cell__title) {
  color: #1989fa;
}

.nameform {
  padding-bottom: 8px;
}

.name-body {
  margin-top: 8px;
}
</style>
