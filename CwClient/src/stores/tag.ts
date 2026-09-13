import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { Tag, TagCreate, TagUpdate } from '@/types'
import { tagApi } from '@/services/api'
import { translate } from '@/i18n'
import { fetchInto, withMessage, writeActions } from '@/stores/actions'

export const useTagStore = defineStore('tag', () => {
  const tags = ref<Tag[]>([])
  const loading = ref(false)

  const fetchAll = fetchInto({
    list: tags,
    loading,
    messageKey: 'app.stores.fetchTagFailed',
    run: () => tagApi.getAll(),
  })

  const { create, update, remove } = writeActions<Tag, TagCreate, TagUpdate>({
    list: tags,
    api: tagApi,
    messageKeys: {
      create: 'app.stores.createTagFailed',
      update: 'app.stores.updateTagFailed',
      remove: 'app.stores.removeTagFailed',
    },
  })

  const addToItem = withMessage('app.stores.addItemTagFailed', (itemId: number, tagId: number) =>
    tagApi.addToItem(itemId, tagId)
  )

  const removeFromItem = withMessage('app.stores.removeItemTagFailed', (itemId: number, tagId: number) =>
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
      useMessage().error(e.message || translate('app.stores.fetchItemTagsFailed'))
      return []
    }
  }

  return { tags, loading, fetchAll, create, update, remove, addToItem, removeFromItem, getItemTags }
})
