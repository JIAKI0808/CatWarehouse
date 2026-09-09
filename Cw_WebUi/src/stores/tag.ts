import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { Tag, TagCreate, TagUpdate } from '@/types'
import { tagApi } from '@/services/api'

export const useTagStore = defineStore('tag', () => {
  const tags = ref<Tag[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      tags.value = await tagApi.getAll()
    } catch (e: any) {
      useMessage().error(e.message || '获取标签失败')
    } finally {
      loading.value = false
    }
  }

  async function create(data: TagCreate) {
    try {
      const item = await tagApi.create(data)
      tags.value.push(item)
      return item
    } catch (e: any) {
      useMessage().error(e.message || '创建标签失败')
    }
  }

  async function update(id: number, data: TagUpdate) {
    try {
      const item = await tagApi.update(id, data)
      const index = tags.value.findIndex(t => t.id === id)
      if (index !== -1) tags.value[index] = item
      return item
    } catch (e: any) {
      useMessage().error(e.message || '更新标签失败')
    }
  }

  async function remove(id: number) {
    try {
      await tagApi.delete(id)
      tags.value = tags.value.filter(t => t.id !== id)
    } catch (e: any) {
      useMessage().error(e.message || '删除标签失败')
    }
  }

  async function addToItem(itemId: number, tagId: number) {
    try {
      await tagApi.addToItem(itemId, tagId)
    } catch (e: any) {
      useMessage().error(e.message || '添加标签失败')
    }
  }

  async function removeFromItem(itemId: number, tagId: number) {
    try {
      await tagApi.removeFromItem(itemId, tagId)
    } catch (e: any) {
      useMessage().error(e.message || '移除标签失败')
    }
  }

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
