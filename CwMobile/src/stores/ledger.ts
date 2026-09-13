import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Ledger, LedgerCreate, LedgerUpdate, LedgerStats } from '@/types'
import { ledgerApi } from '@/services/api'
import { fetchInto, withMessage, writeActions } from '@/stores/actions'

export const useLedgerStore = defineStore('ledger', () => {
  const items = ref<Ledger[]>([])
  const stats = ref<LedgerStats[]>([])
  const loading = ref(false)

  const fetchAll = fetchInto({
    list: items,
    loading,
    message: '获取账单失败',
    run: (params?: { q?: string; type?: string; start_date?: string; end_date?: string }) =>
      ledgerApi.getAll(params),
  })

  const { create, update, remove } = writeActions<Ledger, LedgerCreate, LedgerUpdate>({
    list: items,
    api: ledgerApi,
    messages: { create: '创建账单失败', update: '更新账单失败', remove: '删除账单失败' },
    // 全仓库唯一一处 `unshift`：账单按时间倒序（陷阱 T1），不是笔误。
    insert: 'unshift',
  })

  /** 写的是 `stats` 而非 `items`，且不碰 `loading`（陷阱 T13）。 */
  const fetchStats = withMessage('获取统计失败', async (range: string) => {
    stats.value = await ledgerApi.getStats(range)
  })

  return { items, stats, loading, fetchAll, create, update, remove, fetchStats }
})
