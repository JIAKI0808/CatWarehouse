import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { useMessage } from 'naive-ui'
import type { SubCategory, SubCategoryUpdate } from '@/types'
import { subCategoryApi } from '@/services/api'
import { useUnitStore } from '@/stores/units'
import { translate } from '@/i18n'

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
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.fetchSubCategoryFailed'))
    } finally {
      loading.value = false
    }
  }

  async function create(
    categoryId: number,
    name: string,
    // 默认单位来自字典（`stores/units.ts`），不再写死 `'个'`；
    // 字典拿不到时 store 内部退回的仍是 `'个'`，行为与接入前一致。
    unit: string = useUnitStore().defaultUnit,
    description: string = '',
    notes: string = ''
  ) {
    try {
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
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.createSubCategoryFailed'))
    }
  }

  async function update(id: number, data: SubCategoryUpdate) {
    try {
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
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.updateSubCategoryFailed'))
    }
  }

  async function remove(categoryId: number, id: number) {
    try {
      await subCategoryApi.delete(id)
      const list = subCategoriesByCategory[categoryId]
      if (list) {
        subCategoriesByCategory[categoryId] = list.filter(s => s.id !== id)
      }
      if (selectedId.value === id) {
        selectedId.value = null
      }
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.removeSubCategoryFailed'))
    }
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
    remove,
    select,
  }
})
