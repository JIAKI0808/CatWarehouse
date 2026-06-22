import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { SubCategory } from '@/types'
import { subCategoryApi } from '@/services/api'

export const useSubCategoryStore = defineStore('subCategory', () => {
  const subCategories = ref<SubCategory[]>([])
  const selectedId = ref<number | null>(null)
  const loading = ref(false)

  async function fetchByCategory(categoryId: number) {
    loading.value = true
    try {
      subCategories.value = await subCategoryApi.getByCategory(categoryId)
    } finally {
      loading.value = false
    }
  }

  async function create(
    categoryId: number,
    name: string,
    unit: string = '个',
    description: string = '',
    notes: string = ''
  ) {
    const newSubCategory = await subCategoryApi.create({
      category_id: categoryId,
      name,
      unit,
      description,
      notes,
    })
    subCategories.value.push(newSubCategory)
    return newSubCategory
  }

  function select(id: number | null) {
    selectedId.value = id
  }

  return {
    subCategories,
    selectedId,
    loading,
    fetchByCategory,
    create,
    select,
  }
})
