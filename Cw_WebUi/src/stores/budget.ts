import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { Budget, BudgetCreate, BudgetUpdate } from '@/types'
import { budgetApi } from '@/services/api'

export const useBudgetStore = defineStore('budget', () => {
  const items = ref<Budget[]>([])
  const summary = ref<Budget[]>([])
  const loading = ref(false)

  async function fetchAll(month?: string) {
    loading.value = true
    try {
      items.value = await budgetApi.getAll(month)
    } catch (e: any) {
      useMessage().error(e.message || '获取预算失败')
    } finally {
      loading.value = false
    }
  }

  async function create(data: BudgetCreate) {
    try {
      const item = await budgetApi.create(data)
      items.value.push(item)
      return item
    } catch (e: any) {
      useMessage().error(e.message || '创建预算失败')
    }
  }

  async function update(id: number, data: BudgetUpdate) {
    try {
      const item = await budgetApi.update(id, data)
      const index = items.value.findIndex(i => i.id === id)
      if (index !== -1) items.value[index] = item
      return item
    } catch (e: any) {
      useMessage().error(e.message || '更新预算失败')
    }
  }

  async function remove(id: number) {
    try {
      await budgetApi.delete(id)
      items.value = items.value.filter(i => i.id !== id)
    } catch (e: any) {
      useMessage().error(e.message || '删除预算失败')
    }
  }

  async function fetchSummary(month: string) {
    try {
      summary.value = await budgetApi.getSummary(month)
    } catch (e: any) {
      useMessage().error(e.message || '获取预算摘要失败')
    }
  }

  return { items, summary, loading, fetchAll, create, update, remove, fetchSummary }
})
