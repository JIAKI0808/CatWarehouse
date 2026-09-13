<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { showToast, showConfirmDialog } from 'vant'
import { useCategoryStore } from '@/stores/category'
import { useSubCategoryStore } from '@/stores/subCategory'
import { useItemStore } from '@/stores/item'
import { useAlertStore } from '@/stores/alert'
import { useNotificationStore } from '@/stores/notification'
import { useServerConfigStore } from '@/stores/serverConfig'
import type { Item, SubCategory } from '@/types'
import CategoryManager from '@/components/CategoryManager.vue'
import NotificationSheet from '@/components/NotificationSheet.vue'
import DataActionsSheet from '@/components/DataActionsSheet.vue'
import ItemForm from '@/components/ItemForm.vue'
import CascaderPicker from '@/components/CascaderPicker.vue'

const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()
const itemStore = useItemStore()
const alertStore = useAlertStore()
const notificationStore = useNotificationStore()
const serverConfigStore = useServerConfigStore()

const showCatMgr = ref(false)
const showNotify = ref(false)
const showDataSheet = ref(false)
const showItemForm = ref(false)
const showPicker = ref(false)
const refreshing = ref(false)
const editingItem = ref<Item | null>(null)
const initialized = ref(false)

const selectedSub = computed<SubCategory | null>(() => {
  const lists = Object.values(subCategoryStore.subCategoriesByCategory)
  for (const list of lists) {
    const found = list.find((s) => s.id === subCategoryStore.selectedId)
    if (found) return found
  }
  return null
})

const pickerCategories = computed(() =>
  categoryStore.categories.map((c) => ({ text: c.name, value: c.id }))
)

function pickerSubsOf(catId: number) {
  return subCategoryStore
    .getSubCategories(catId)
    .map((s) => ({ text: s.name, value: s.id }))
}

async function openPicker() {
  await Promise.all(
    categoryStore.categories.map((c) => subCategoryStore.fetchByCategory(c.id))
  )
  showPicker.value = true
}

function onPickerConfirm(r: { categoryId: number; subId: number | null }) {
  if (r.subId === null) {
    showToast('请选择子分类')
    return
  }
  const sub = subCategoryStore
    .getSubCategories(r.categoryId)
    .find((s) => s.id === r.subId)
  if (sub) onSelectSub(sub)
}

async function onRefresh() {
  try {
    await categoryStore.fetchAll()
    if (selectedSub.value) {
      await itemStore.fetchBySubCategory(selectedSub.value.id)
    }
  } finally {
    refreshing.value = false
  }
}

const badgeCount = computed(() => {
  const unread = notificationStore.items.filter((n) => !n.is_read).length
  return unread + alertStore.alerts.length
})

onMounted(() => {
  initialized.value = true
  categoryStore.fetchAll()
  refreshNotifications()
  if (subCategoryStore.selectedId) {
    itemStore.fetchBySubCategory(subCategoryStore.selectedId)
  }
})

watch(
  () => serverConfigStore.config,
  () => {
    if (!initialized.value) return
    categoryStore.fetchAll()
    for (const catId of Object.keys(subCategoryStore.subCategoriesByCategory)) {
      subCategoryStore.fetchByCategory(Number(catId))
    }
    if (subCategoryStore.selectedId) {
      itemStore.fetchBySubCategory(subCategoryStore.selectedId)
    }
  },
  { deep: true }
)

function refreshNotifications() {
  alertStore.fetchAlerts()
  notificationStore.fetchAll()
}

function onSelectSub(sub: SubCategory) {
  subCategoryStore.select(sub.id)
  itemStore.fetchBySubCategory(sub.id)
}

function openAddItem() {
  if (!selectedSub.value) {
    showToast('请先在左上角选择子分类')
    return
  }
  editingItem.value = null
  showItemForm.value = true
}

function openEditItem(item: Item) {
  editingItem.value = item
  showItemForm.value = true
}

async function askDeleteItem(item: Item) {
  try {
    await showConfirmDialog({
      title: '删除物品',
      message: `确定要删除「${item.name}」吗？`,
      confirmButtonText: '删除',
      confirmButtonColor: '#ee0a24',
    })
  } catch {
    return
  }
  await itemStore.remove(item.id)
  refreshSubQuantity()
}

function refreshSubQuantity() {
  const catId = selectedSub.value?.category_id
  if (catId) subCategoryStore.fetchByCategory(catId)
}

async function handleSubmit(data: Record<string, unknown>) {
  const catId = selectedSub.value?.category_id
  if (editingItem.value) {
    await itemStore.update(editingItem.value.id, data)
  } else if (selectedSub.value) {
    await itemStore.create({
      sub_category_id: selectedSub.value.id,
      name: data.name as string,
      recorder: data.recorder as string,
      price: Number(data.price),
      description: data.description as string,
      expire_date: (data.expire_date as string) || null,
      is_expired: Boolean(data.is_expired),
    })
  }
  editingItem.value = null
  if (selectedSub.value) {
    await itemStore.fetchBySubCategory(selectedSub.value.id)
  }
  if (catId) subCategoryStore.fetchByCategory(catId)
}

function onChanged() {
  categoryStore.fetchAll()
  if (selectedSub.value) {
    itemStore.fetchBySubCategory(selectedSub.value.id)
  }
}

function formatDate(str: string | null): string {
  return str ? new Date(str).toLocaleDateString() : ''
}
</script>

<template>
  <div class="inv">
    <van-nav-bar>
      <template #left>
        <van-icon name="apps-o" size="20" @click="showCatMgr = true" />
      </template>
      <template #title>
        <div class="head-title" @click="openPicker">
          <span v-if="selectedSub" class="head-sub">{{ selectedSub.name }}</span>
          <span v-else class="head-hint">选择子分类</span>
          <van-icon name="arrow-down" size="12" color="var(--van-text-color-3)" />
        </div>
      </template>
      <template #right>
        <div class="head-right">
          <van-badge
            :content="badgeCount > 0 ? badgeCount : ''"
            :show-zero="false"
            max="99"
          >
            <van-icon name="bell" size="20" @click="showNotify = true" />
          </van-badge>
          <van-icon name="ellipsis" size="20" @click="showDataSheet = true" />
        </div>
      </template>
    </van-nav-bar>

    <div v-if="selectedSub" class="inv-info">
      <span class="info-name">{{ selectedSub.name }}</span>
      <span class="info-qty">
        库存 {{ selectedSub.quantity }} {{ selectedSub.unit }}
      </span>
    </div>

    <div class="inv-body">
      <van-empty
        v-if="!selectedSub"
        description="请选择子分类后查看物品"
      >
        <van-button type="primary" plain size="small" @click="showCatMgr = true">
          选择分类
        </van-button>
      </van-empty>

      <template v-else>
        <van-loading v-if="itemStore.loading" class="inv-loading" vertical>
          加载中
        </van-loading>
        <van-empty
          v-else-if="!itemStore.items.length"
          description="暂无物品，点击下方按钮新增"
        />
        <van-pull-refresh v-else v-model="refreshing" @refresh="onRefresh">
          <div class="inv-list">
            <van-swipe-cell v-for="item in itemStore.items" :key="item.id">
              <div class="inv-item" @click="openEditItem(item)">
            <div class="item-main">
              <div class="item-row1">
                <span class="item-name">{{ item.name }}</span>
                <van-tag v-if="item.is_expired" type="danger" class="item-tag">
                  已过期
                </van-tag>
              </div>
              <div class="item-meta">
                价格 ¥{{ item.price.toFixed(2) }} · 库存
                {{ item.quantity }} {{ item.unit || '' }}
              </div>
              <div v-if="item.expire_date" class="item-meta">
                过期 {{ formatDate(item.expire_date) }}
              </div>
              <div v-if="item.description" class="item-desc">
                {{ item.description }}
              </div>
              <div class="item-meta item-recorder">
                {{ item.recorder || '未记录录入人' }}
              </div>
            </div>
              </div>
              <template #right>
                <van-button
                  square
                  type="danger"
                  text="删除"
                  class="del-btn"
                  @click="askDeleteItem(item)"
                />
              </template>
            </van-swipe-cell>
          </div>
        </van-pull-refresh>
      </template>
    </div>

    <div class="inv-fab">
      <van-button
        round
        block
        type="primary"
        icon="plus"
        :disabled="!selectedSub"
        @click="openAddItem"
      >
        新增物品
      </van-button>
    </div>

    <CascaderPicker
      v-model:show="showPicker"
      title="选择分类"
      :categories="pickerCategories"
      :subs-of="pickerSubsOf"
      :initial-category-id="selectedSub?.category_id ?? undefined"
      :initial-sub-id="selectedSub?.id ?? undefined"
      @confirm="onPickerConfirm"
    />
    <CategoryManager v-model:visible="showCatMgr" @select="onSelectSub" />
    <NotificationSheet v-model:visible="showNotify" />
    <DataActionsSheet
      v-model:visible="showDataSheet"
      @changed="onChanged"
    />
    <ItemForm
      v-model:visible="showItemForm"
      :item="editingItem"
      @submit="handleSubmit"
    />
  </div>
</template>

<style scoped>
.inv {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.head-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.head-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 15px;
}

.head-hint {
  color: var(--van-text-color-2);
}

.inv-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 14px 4px;
  padding: 6px 10px;
  border-radius: 8px;
  background: var(--van-background-2);
  font-size: 13px;
}

.info-name {
  font-weight: 600;
}

.info-qty {
  color: var(--van-text-color-2);
}

.inv-body {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0 calc(var(--tabbar-height) + 64px);
}

.inv-loading {
  padding-top: 60px;
}

.inv-list {
  padding: 0 14px;
}

.inv-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  margin-bottom: 10px;
  background: var(--van-background-2);
  border-radius: 10px;
  cursor: pointer;
}

.item-main {
  flex: 1;
  min-width: 0;
}

.item-row1 {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.item-name {
  font-size: 15px;
  font-weight: 600;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.item-meta {
  color: var(--van-text-color-2);
  font-size: 12px;
  margin-top: 2px;
}

.item-desc {
  color: var(--van-text-color-2);
  font-size: 12px;
  margin-top: 2px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.del-btn {
  height: 100%;
}

.inv-fab {
  position: fixed;
  left: 14px;
  right: 14px;
  bottom: calc(50px + env(safe-area-inset-bottom) + 10px);
}
</style>
