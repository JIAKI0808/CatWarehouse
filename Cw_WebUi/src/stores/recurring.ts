import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { RecurringBill, RecurringBillCreate, RecurringBillUpdate } from '@/types'
import { recurringApi } from '@/services/api'

export const useRecurringStore = defineStore('recurring', () => {
  const items = ref<RecurringBill[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      items.value = await recurringApi.getAll()
    } catch (e: any) {
      useMessage().error(e.message || '获取周期账单失败')
    } finally {
      loading.value = false
    }
  }

  async function create(data: RecurringBillCreate) {
    try {
      const item = await recurringApi.create(data)
      items.value.push(item)
      return item
    } catch (e: any) {
      useMessage().error(e.message || '创建周期账单失败')
    }
  }

  async function update(id: number, data: RecurringBillUpdate) {
    try {
      const item = await recurringApi.update(id, data)
      const index = items.value.findIndex(i => i.id === id)
      if (index !== -1) items.value[index] = item
      return item
    } catch (e: any) {
      useMessage().error(e.message || '更新周期账单失败')
    }
  }

  async function remove(id: number) {
    try {
      await recurringApi.delete(id)
      items.value = items.value.filter(i => i.id !== id)
    } catch (e: any) {
      useMessage().error(e.message || '删除周期账单失败')
    }
  }

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
