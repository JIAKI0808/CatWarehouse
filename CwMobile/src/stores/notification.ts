import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification } from '@/types'
import { notificationApi } from '@/services/api'
import { fetchInto, withMessage } from '@/stores/actions'

export const useNotificationStore = defineStore('notification', () => {
  const items = ref<Notification[]>([])
  const loading = ref(false)

  const unreadCount = computed(() => items.value.filter(n => !n.is_read).length)

  const fetchAll = fetchInto({
    list: items,
    loading,
    message: '获取通知失败',
    run: () => notificationApi.getAll(),
  })

  /**
   * **就地改属性**（陷阱 T8）——`item.is_read = true`，不是替换数组元素，
   * 也不是重新取列表；因此不能套 `writeActions`。
   */
  const markRead = withMessage('标记已读失败', async (id: number) => {
    await notificationApi.markRead(id)
    const item = items.value.find(n => n.id === id)
    if (item) item.is_read = true
  })

  /**
   * 两步：先 `check()`，再 `await fetchAll()`（陷阱 T9）。
   * `fetchAll` 失败时自己会提示，不会冒泡到这里，所以不会重复弹两次。
   */
  const check = withMessage('检查通知失败', async () => {
    await notificationApi.check()
    await fetchAll()
  })

  return { items, loading, unreadCount, fetchAll, markRead, check }
})
