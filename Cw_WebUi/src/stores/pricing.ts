import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import type { Pricing, PricingCreate, PricingUpdate } from '@/types'
import { pricingApi } from '@/services/api'

export const usePricingStore = defineStore('pricing', () => {
  const items = ref<Pricing[]>([])
  const loading = ref(false)

  async function fetchAll(params?: { sub_category_id?: number; q?: string }) {
    loading.value = true
    try {
      items.value = await pricingApi.getAll(params)
    } catch (e: any) {
      useMessage().error(e.message || '获取售价列表失败')
    } finally {
      loading.value = false
    }
  }

  async function create(data: PricingCreate) {
    try {
      const item = await pricingApi.create(data)
      items.value.push(item)
      return item
    } catch (e: any) {
      useMessage().error(e.message || '创建售价记录失败')
    }
  }

  async function update(id: number, data: PricingUpdate) {
    try {
      const item = await pricingApi.update(id, data)
      const index = items.value.findIndex(i => i.id === id)
      if (index !== -1) items.value[index] = item
      return item
    } catch (e: any) {
      useMessage().error(e.message || '更新售价记录失败')
    }
  }

  async function remove(id: number) {
    try {
      await pricingApi.delete(id)
      items.value = items.value.filter(i => i.id !== id)
    } catch (e: any) {
      useMessage().error(e.message || '删除售价记录失败')
    }
  }

  return { items, loading, fetchAll, create, update, remove }
})
