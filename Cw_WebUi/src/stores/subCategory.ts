import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import type { SubCategory } from '@/types'
import { subCategoryApi } from '@/services/api'

export const useSubCategoryStore = defineStore('subCategory', () => {
  const subCategoriesByCategory = reactive<Record<number, SubCategory[]>>({})
  const selectedId = ref<number | null>(null)
  const loading = ref(false)

  function getSubCategories(categoryId: number): SubCategory[] {
    return subCategoriesByCategory[categoryId] ?? []
  }

  async function fetchByCategory(categoryId: number) {
    loading.value = true
    try {
      const categories = await subCategoryApi.getByCategory(categoryId)

      const categoriesWithQuantity = await Promise.all(
        categories.map(async (cat) => {
          const quantityData = await subCategoryApi.getQuantity(cat.id)
          return { ...cat, quantity: quantityData.quantity }
        })
      )

      subCategoriesByCategory[categoryId] = categoriesWithQuantity
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
    const list = subCategoriesByCategory[categoryId] ?? []
    list.push({ ...newSubCategory, quantity: 0 })
    subCategoriesByCategory[categoryId] = list
    return newSubCategory
  }

  function select(id: number | null) {
    selectedId.value = id
  }

  return {
    subCategoriesByCategory,
    selectedId,
    loading,
    getSubCategories,
    fetchByCategory,
    create,
    select,
  }
})
