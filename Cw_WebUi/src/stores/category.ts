import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Category } from '@/types'
import { categoryApi } from '@/services/api'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])
  const selectedId = ref<number | null>(null)
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      categories.value = await categoryApi.getAll()
    } finally {
      loading.value = false
    }
  }

  async function create(name: string, description: string = '') {
    const newCategory = await categoryApi.create({ name, description })
    categories.value.push(newCategory)
    return newCategory
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
    select,
  }
})
