import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { useMessage } from '@/composables/useMessage'
import type { SubCategory, SubCategoryUpdate } from '@/types'
import { subCategoryApi } from '@/services/api'
import { withMessage } from '@/stores/actions'
import { translate } from '@/i18n'

export const useSubCategoryStore = defineStore('subCategory', () => {
  const subCategoriesByCategory = reactive<Record<number, SubCategory[]>>({})
  const selectedId = ref<number | null>(null)
  const loading = ref(false)

  function getSubCategories(categoryId: number): SubCategory[] {
    return subCategoriesByCategory[categoryId] ?? []
  }

  /**
   * 这个动作**故意保持手写**，不套 `fetchInto`：
   * 它写的是一张 `Record<number, SubCategory[]>` 键值表而不是列表 ref，并且要
   * `Promise.all` 逐个子分类再查一次 quantity 合并（陷阱 T5）。硬套适配器会变成
   * 「让所有调用方迁就抽象」，与「优先去重」相反。
   */
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

  const create = withMessage(
    'app.stores.createSubCategoryFailed',
    async (
      categoryId: number,
      name: string,
      unit: string = '个',
      description: string = '',
      notes: string = ''
    ) => {
      const newSubCategory = await subCategoryApi.create({
        category_id: categoryId,
        name,
        unit,
        description,
        notes,
      })
      const list = subCategoriesByCategory[categoryId] ?? []
      // 新条目强制补 `quantity: 0`（陷阱 T7）——后端新建子分类还没有量。
      list.push({ ...newSubCategory, quantity: 0 })
      // `reactive` 表里的数组要**重新赋值**才触发更新，就地 push 不够。
      subCategoriesByCategory[categoryId] = list
      return newSubCategory
    }
  )

  const update = withMessage(
    'app.stores.updateSubCategoryFailed',
    async (id: number, data: SubCategoryUpdate) => {
    const updated = await subCategoryApi.update(id, data)
    // 跨**所有**桶查找（陷阱 T6）：该子分类所属的桶不一定是当前选中的那个。
    // 找到一个就 break —— 与既有实现一致。
    for (const catId of Object.keys(subCategoriesByCategory)) {
      const list = subCategoriesByCategory[Number(catId)]
      if (!list) continue
      const index = list.findIndex(s => s.id === id)
      if (index !== -1) {
        // 合并而非替换：保留列表里已有、而响应未返回的字段。
        list[index] = { ...list[index], ...updated }
        break
      }
    }
    return updated
  })

  const remove = withMessage(
    'app.stores.removeSubCategoryFailed',
    async (categoryId: number, id: number) => {
    await subCategoryApi.delete(id)
    const list = subCategoriesByCategory[categoryId]
    if (list) {
      subCategoriesByCategory[categoryId] = list.filter(s => s.id !== id)
    }
    if (selectedId.value === id) {
      selectedId.value = null
    }
  })

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
