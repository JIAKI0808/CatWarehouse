import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Category, CategoryCreate, CategoryUpdate } from '@/types'
import { categoryApi } from '@/services/api'
import { fetchInto, writeActions } from '@/stores/actions'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])
  const selectedId = ref<number | null>(null)
  const loading = ref(false)

  const fetchAll = fetchInto({
    list: categories,
    loading,
    message: '获取分类失败',
    run: () => categoryApi.getAll(),
  })

  const { create: writeCreate, update, remove } = writeActions<
    Category,
    CategoryCreate,
    CategoryUpdate
  >({
    list: categories,
    api: categoryApi,
    messages: { create: '创建分类失败', update: '更新分类失败', remove: '删除分类失败' },
    // 删除命中当前选中项时顺带清空选中（既有行为，陷阱 T3）。
    onRemoved: (id) => {
      if (selectedId.value === id) selectedId.value = null
    },
  })

  /**
   * 保持既有的**位置参数**签名（陷阱 T2）——调用方按位置传，不是传对象。
   * 原来的默认值逐字保留。
   */
  async function create(
    name: string,
    description: string = '',
    icon: string = 'FolderOutline',
    icon_color: string = '#f59e0b'
  ) {
    return writeCreate({ name, description, icon, icon_color })
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
