import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { RecurringBill, RecurringBillCreate, RecurringBillUpdate } from '@/types'
import { recurringApi } from '@/services/api'
import { fetchInto, writeActions } from '@/stores/actions'

export const useRecurringStore = defineStore('recurring', () => {
  const items = ref<RecurringBill[]>([])
  const loading = ref(false)

  const fetchAll = fetchInto({
    list: items,
    loading,
    message: '获取周期账单失败',
    run: () => recurringApi.getAll(),
  })

  const { create, update, remove } = writeActions<
    RecurringBill,
    RecurringBillCreate,
    RecurringBillUpdate
  >({
    list: items,
    api: recurringApi,
    messages: {
      create: '创建周期账单失败',
      update: '更新周期账单失败',
      remove: '删除周期账单失败',
    },
  })

  /** **不用 `withMessage`**：它失败时返回 `undefined`，原实现返回的是 `0`。 */
  async function generate() {
    try {
      const result = await recurringApi.generate()
      return result.created
    } catch (e: any) {
      useMessage().error(e.message || '生成账单失败')
      return 0
    }
  }

  return { items, loading, fetchAll, create, update, remove, generate }
})
