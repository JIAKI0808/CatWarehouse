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
    messageKey: 'app.stores.fetchItemFailed',
    run: (subCategoryId: number) => itemApi.getBySubCategory(subCategoryId),
  })

  const { create, update, remove } = writeActions<Item, ItemCreate, ItemUpdate>({
    list: items,
    api: itemApi,
    messageKeys: {
      create: 'app.stores.createItemFailed',
      update: 'app.stores.updateItemFailed',
      remove: 'app.stores.removeItemFailed',
    },
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
