import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import type { SubCategory, SubCategoryUpdate } from '@/types'
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

  async function update(id: number, data: SubCategoryUpdate) {
    const updated = await subCategoryApi.update(id, data)
    for (const catId of Object.keys(subCategoriesByCategory)) {
      const list = subCategoriesByCategory[Number(catId)]
      const index = list.findIndex(s => s.id === id)
      if (index !== -1) {
        list[index] = { ...list[index], ...updated }
        break
      }
    }
    return updated
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
    update,
    select,
  }
})
