import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from '@/composables/useMessage'
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
    } catch (e: any) {
      useMessage().error(e.message || '获取物品失败')
    } finally {
      loading.value = false
    }
  }

  async function create(data: ItemCreate) {
    try {
      const newItem = await itemApi.create(data)
      items.value.push(newItem)
      return newItem
    } catch (e: any) {
      useMessage().error(e.message || '创建物品失败')
    }
  }

  async function update(id: number, data: ItemUpdate) {
    try {
      const updatedItem = await itemApi.update(id, data)
      const index = items.value.findIndex((item) => item.id === id)
      if (index !== -1) {
        items.value[index] = updatedItem
      }
      return updatedItem
    } catch (e: any) {
      useMessage().error(e.message || '更新物品失败')
    }
  }

  async function remove(id: number) {
    try {
      await itemApi.delete(id)
      items.value = items.value.filter((item) => item.id !== id)
    } catch (e: any) {
      useMessage().error(e.message || '删除物品失败')
    }
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
