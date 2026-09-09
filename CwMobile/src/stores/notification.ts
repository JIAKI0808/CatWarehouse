import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMessage } from '@/composables/useMessage'
import type { Notification } from '@/types'
import { notificationApi } from '@/services/api'

export const useNotificationStore = defineStore('notification', () => {
  const items = ref<Notification[]>([])
  const loading = ref(false)

  const unreadCount = computed(() => items.value.filter(n => !n.is_read).length)

  async function fetchAll() {
    loading.value = true
    try {
      items.value = await notificationApi.getAll()
    } catch (e: any) {
      useMessage().error(e.message || '获取通知失败')
    } finally {
      loading.value = false
    }
  }

  async function markRead(id: number) {
    try {
      await notificationApi.markRead(id)
      const item = items.value.find(n => n.id === id)
      if (item) item.is_read = true
    } catch (e: any) {
      useMessage().error(e.message || '标记已读失败')
    }
  }

  async function check() {
    try {
      await notificationApi.check()
      await fetchAll()
    } catch (e: any) {
      useMessage().error(e.message || '检查通知失败')
    }
  }

  return { items, loading, unreadCount, fetchAll, markRead, check }
})
