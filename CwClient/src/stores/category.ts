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

  const write = writeActions<Category, CategoryCreate, CategoryUpdate>({
    list: categories,
    api: categoryApi,
    messages: { create: '创建分类失败', update: '更新分类失败', remove: '删除分类失败' },
    // 删除后顺手清掉选中项 —— 只有 category 有 selectedId，所以只有它需要这一钩子。
    onRemoved: (id) => {
      if (selectedId.value === id) selectedId.value = null
    },
  })

  /** 保留原来的**位置参数**签名（不是 `create(data)`），外部调用点因此一行不用改。 */
  async function create(
    name: string,
    description: string = '',
    icon: string = 'FolderOutline',
    icon_color: string = '#f59e0b'
  ) {
    return write.create({ name, description, icon, icon_color })
  }

  const update = write.update
  const remove = write.remove

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
