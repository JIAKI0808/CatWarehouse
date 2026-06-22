import { defineStore } from 'pinia'
import { ref } from 'vue'
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
    } finally {
      loading.value = false
    }
  }

  async function create(name: string, description: string = '', icon: string = 'FolderOutline') {
    const newCategory = await categoryApi.create({ name, description, icon })
    categories.value.push(newCategory)
    return newCategory
  }

  async function update(id: number, data: CategoryUpdate) {
    const updated = await categoryApi.update(id, data)
    const index = categories.value.findIndex(c => c.id === id)
    if (index !== -1) {
      categories.value[index] = updated
    }
    return updated
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
    select,
  }
})
