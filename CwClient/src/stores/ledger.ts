import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { Ledger, LedgerCreate, LedgerUpdate, LedgerStats } from '@/types'
import { ledgerApi } from '@/services/api'
import { translate } from '@/i18n'
import { fetchInto, writeActions } from '@/stores/actions'

export const useLedgerStore = defineStore('ledger', () => {
  const items = ref<Ledger[]>([])
  const stats = ref<LedgerStats[]>([])
  const loading = ref(false)

  const fetchAll = fetchInto({
    list: items,
    loading,
    messageKey: 'app.stores.fetchLedgerFailed',
    run: (params?: { q?: string; type?: string; start_date?: string; end_date?: string }) =>
      ledgerApi.getAll(params),
  })

  const { create, update, remove } = writeActions<Ledger, LedgerCreate, LedgerUpdate>({
    list: items,
    api: ledgerApi,
    messageKeys: {
      create: 'app.stores.createLedgerFailed',
      update: 'app.stores.updateLedgerFailed',
      remove: 'app.stores.removeLedgerFailed',
    },
    // 全仓库唯一一处 `unshift`：账单按时间倒序，新记录要出现在最前面。
    // 其余 6 个 store 一律 `push` —— 这个差异是**故意保留**的，不是遗漏。
    insert: 'unshift',
  })

  /** 写进的是**另一个** ref（`stats`），所以不走 `fetchInto`，也不动 `loading`。 */
  async function fetchStats(range: string) {
    try {
      stats.value = await ledgerApi.getStats(range)
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.fetchLedgerStatsFailed'))
    }
  }

  return { items, stats, loading, fetchAll, create, update, remove, fetchStats }
})
