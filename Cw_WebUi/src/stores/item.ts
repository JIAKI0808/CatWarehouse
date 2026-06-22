import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Item, ItemCreate, ItemUpdate, ViewMode } from '@/types'
import { itemApi } from '@/services/api'

export const useItemStore = defineStore('item', () => {
  const items = ref<Item[]>([])
  const loading = ref(false)
  const viewMode = ref<ViewMode>('table')

  async function fetchBySubCategory(subCategoryId: number) {
    loading.value = true
    try {
      items.value = await itemApi.getBySubCategory(subCategoryId)
    } finally {
      loading.value = false
    }
  }

  async function create(data: ItemCreate) {
    const newItem = await itemApi.create(data)
    items.value.push(newItem)
    return newItem
  }

  async function update(id: number, data: ItemUpdate) {
    const updatedItem = await itemApi.update(id, data)
    const index = items.value.findIndex((item) => item.id === id)
    if (index !== -1) {
      items.value[index] = updatedItem
    }
    return updatedItem
  }

  async function remove(id: number) {
    await itemApi.delete(id)
    items.value = items.value.filter((item) => item.id !== id)
  }

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
