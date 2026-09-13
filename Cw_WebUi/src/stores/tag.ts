import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { Tag, TagCreate, TagUpdate } from '@/types'
import { tagApi } from '@/services/api'
import { fetchInto, withMessage, writeActions } from '@/stores/actions'

export const useTagStore = defineStore('tag', () => {
  const tags = ref<Tag[]>([])
  const loading = ref(false)

  const fetchAll = fetchInto({
    list: tags,
    loading,
    message: '获取标签失败',
    run: () => tagApi.getAll(),
  })

  const { create, update, remove } = writeActions<Tag, TagCreate, TagUpdate>({
    list: tags,
    api: tagApi,
    messages: { create: '创建标签失败', update: '更新标签失败', remove: '删除标签失败' },
  })

  const addToItem = withMessage('添加标签失败', (itemId: number, tagId: number) =>
    tagApi.addToItem(itemId, tagId)
  )

  const removeFromItem = withMessage('移除标签失败', (itemId: number, tagId: number) =>
    tagApi.removeFromItem(itemId, tagId)
  )

  /**
   * **不用 `withMessage`**：它失败时返回 `undefined`，而这里原实现返回的是 `[]`。
   * 换成装饰器会把失败时的返回值从 `[]` 变成 `undefined` —— 那是行为变化。
   */
  async function getItemTags(itemId: number) {
    try {
      return await tagApi.getItemTags(itemId)
    } catch (e: any) {
      useMessage().error(e.message || '获取物品标签失败')
      return []
    }
  }

  return { tags, loading, fetchAll, create, update, remove, addToItem, removeFromItem, getItemTags }
})
