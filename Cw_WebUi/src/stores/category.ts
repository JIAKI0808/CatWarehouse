import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { Category, CategoryUpdate } from '@/types'
import { categoryApi } from '@/services/api'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])
  const selectedId = ref<number | null>(null)
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      categories.value = await categoryApi.getAll()
    } catch (e: any) {
      useMessage().error(e.message || '获取分类失败')
    } finally {
      loading.value = false
    }
  }

  async function create(name: string, description: string = '', icon: string = 'FolderOutline', icon_color: string = '#f59e0b') {
    try {
      const newCategory = await categoryApi.create({ name, description, icon, icon_color })
      categories.value.push(newCategory)
      return newCategory
    } catch (e: any) {
      useMessage().error(e.message || '创建分类失败')
    }
  }

  async function update(id: number, data: CategoryUpdate) {
    try {
      const updated = await categoryApi.update(id, data)
      const index = categories.value.findIndex(c => c.id === id)
      if (index !== -1) {
        categories.value[index] = updated
      }
      return updated
    } catch (e: any) {
      useMessage().error(e.message || '更新分类失败')
    }
  }

  async function remove(id: number) {
    try {
      await categoryApi.delete(id)
      categories.value = categories.value.filter(c => c.id !== id)
      if (selectedId.value === id) {
        selectedId.value = null
      }
    } catch (e: any) {
      useMessage().error(e.message || '删除分类失败')
    }
  }

  function select(id: number | null) {
    selectedId.value = id
  }

  return {
    categories,
    selectedId,
    loading,
    fetchAll,
    create,
    update,
    remove,
    select,
  }
})
