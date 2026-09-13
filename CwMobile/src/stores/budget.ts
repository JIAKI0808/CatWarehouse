import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Budget, BudgetCreate, BudgetUpdate } from '@/types'
import { budgetApi } from '@/services/api'
import { fetchInto, withMessage, writeActions } from '@/stores/actions'

export const useBudgetStore = defineStore('budget', () => {
  const items = ref<Budget[]>([])
  const summary = ref<Budget[]>([])
  const loading = ref(false)

  const fetchAll = fetchInto({
    list: items,
    loading,
    message: '获取预算失败',
    run: (month?: string) => budgetApi.getAll(month),
  })

  const { create, update, remove } = writeActions<Budget, BudgetCreate, BudgetUpdate>({
    list: items,
    api: budgetApi,
    messages: { create: '创建预算失败', update: '更新预算失败', remove: '删除预算失败' },
  })

  /**
   * 写的是**另一个** ref（`summary`）且**不碰** `loading`（陷阱 T13），所以不能套
   * `fetchInto` —— 只把重复的 catch 收进 `withMessage`。失败时不赋值，与既有实现一致。
   */
  const fetchSummary = withMessage('获取预算摘要失败', async (month: string) => {
    summary.value = await budgetApi.getSummary(month)
  })

  return { items, summary, loading, fetchAll, create, update, remove, fetchSummary }
})
