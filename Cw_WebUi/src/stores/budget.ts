import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { Budget, BudgetCreate, BudgetUpdate } from '@/types'
import { budgetApi } from '@/services/api'
import { translate } from '@/i18n'
import { fetchInto, writeActions } from '@/stores/actions'

export const useBudgetStore = defineStore('budget', () => {
  const items = ref<Budget[]>([])
  const summary = ref<Budget[]>([])
  const loading = ref(false)

  const fetchAll = fetchInto({
    list: items,
    loading,
    messageKey: 'app.stores.fetchBudgetFailed',
    run: (month?: string) => budgetApi.getAll(month),
  })

  const { create, update, remove } = writeActions<Budget, BudgetCreate, BudgetUpdate>({
    list: items,
    api: budgetApi,
    messageKeys: {
      create: 'app.stores.createBudgetFailed',
      update: 'app.stores.updateBudgetFailed',
      remove: 'app.stores.removeBudgetFailed',
    },
  })

  /** 写进的是**另一个** ref（`summary`），所以不走 `fetchInto`，也不动 `loading`。 */
  async function fetchSummary(month: string) {
    try {
      summary.value = await budgetApi.getSummary(month)
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.fetchBudgetSummaryFailed'))
    }
  }

  return { items, summary, loading, fetchAll, create, update, remove, fetchSummary }
})
