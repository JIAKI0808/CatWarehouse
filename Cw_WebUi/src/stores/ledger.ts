import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { Ledger, LedgerCreate, LedgerUpdate, LedgerStats } from '@/types'
import { ledgerApi } from '@/services/api'

export const useLedgerStore = defineStore('ledger', () => {
  const items = ref<Ledger[]>([])
  const stats = ref<LedgerStats[]>([])
  const loading = ref(false)

  async function fetchAll(params?: { q?: string; type?: string; start_date?: string; end_date?: string }) {
    loading.value = true
    try {
      items.value = await ledgerApi.getAll(params)
    } catch (e: any) {
      useMessage().error(e.message || '获取账单失败')
    } finally {
      loading.value = false
    }
  }

  async function create(data: LedgerCreate) {
    try {
      const item = await ledgerApi.create(data)
      items.value.unshift(item)
      return item
    } catch (e: any) {
      useMessage().error(e.message || '创建账单失败')
    }
  }

  async function update(id: number, data: LedgerUpdate) {
    try {
      const item = await ledgerApi.update(id, data)
      const index = items.value.findIndex(i => i.id === id)
      if (index !== -1) items.value[index] = item
      return item
    } catch (e: any) {
      useMessage().error(e.message || '更新账单失败')
    }
  }

  async function remove(id: number) {
    try {
      await ledgerApi.delete(id)
      items.value = items.value.filter(i => i.id !== id)
    } catch (e: any) {
      useMessage().error(e.message || '删除账单失败')
    }
  }

  async function fetchStats(range: string) {
    try {
      stats.value = await ledgerApi.getStats(range)
    } catch (e: any) {
      useMessage().error(e.message || '获取统计失败')
    }
  }

  return { items, stats, loading, fetchAll, create, update, remove, fetchStats }
})
