import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { RecurringBill, RecurringBillCreate, RecurringBillUpdate } from '@/types'
import { recurringApi } from '@/services/api'
import { translate } from '@/i18n'
import { fetchInto, writeActions } from '@/stores/actions'

export const useRecurringStore = defineStore('recurring', () => {
  const items = ref<RecurringBill[]>([])
  const loading = ref(false)

  const fetchAll = fetchInto({
    list: items,
    loading,
    messageKey: 'app.stores.fetchRecurringFailed',
    run: () => recurringApi.getAll(),
  })

  const { create, update, remove } = writeActions<
    RecurringBill,
    RecurringBillCreate,
    RecurringBillUpdate
  >({
    list: items,
    api: recurringApi,
    messageKeys: {
      create: 'app.stores.createRecurringFailed',
      update: 'app.stores.updateRecurringFailed',
      remove: 'app.stores.removeRecurringFailed',
    },
  })

  /** **不用 `withMessage`**：它失败时返回 `undefined`，原实现返回的是 `0`。 */
  async function generate() {
    try {
      const result = await recurringApi.generate()
      return result.created
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.generateRecurringFailed'))
      return 0
    }
  }

  return { items, loading, fetchAll, create, update, remove, generate }
})
