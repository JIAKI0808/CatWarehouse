import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Item, ItemCreate, ItemUpdate, ViewMode } from '@/types'
import { itemApi } from '@/services/api'
import { fetchInto, writeActions } from '@/stores/actions'

export const useItemStore = defineStore('item', () => {
  const items = ref<Item[]>([])
  const loading = ref(false)
  const viewMode = ref<ViewMode>('table')

  const fetchBySubCategory = fetchInto({
    list: items,
    loading,
    message: '获取物品失败',
    run: (subCategoryId: number) => itemApi.getBySubCategory(subCategoryId),
  })

  const { create, update, remove } = writeActions<Item, ItemCreate, ItemUpdate>({
    list: items,
    api: itemApi,
    messages: { create: '创建物品失败', update: '更新物品失败', remove: '删除物品失败' },
  })

  function setViewMode(mode: ViewMode) {
    viewMode.value = mode
  }

  function clearItems() {
    items.value = []
  }

  return {
    items,
    loading,
    viewMode,
    fetchBySubCategory,
    create,
    update,
    remove,
    setViewMode,
    clearItems,
  }
})
