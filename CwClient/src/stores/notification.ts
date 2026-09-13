import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import type { Notification } from '@/types'
import { notificationApi } from '@/services/api'
import { translate } from '@/i18n'
import { fetchInto } from '@/stores/actions'

export const useNotificationStore = defineStore('notification', () => {
  const items = ref<Notification[]>([])
  const loading = ref(false)

  const unreadCount = computed(() => items.value.filter(n => !n.is_read).length)

  const fetchAll = fetchInto({
    list: items,
    loading,
    messageKey: 'app.stores.fetchNotificationFailed',
    run: () => notificationApi.getAll(),
  })

  async function markRead(id: number) {
    try {
      await notificationApi.markRead(id)
      const item = items.value.find(n => n.id === id)
      if (item) item.is_read = true
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.markNotificationReadFailed'))
    }
  }

  async function check() {
    try {
      await notificationApi.check()
      await fetchAll()
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.checkNotificationFailed'))
    }
  }

  return { items, loading, unreadCount, fetchAll, markRead, check }
})
