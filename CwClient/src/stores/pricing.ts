import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Pricing, PricingCreate, PricingUpdate } from '@/types'
import { pricingApi } from '@/services/api'
import { fetchInto, writeActions } from '@/stores/actions'

export const usePricingStore = defineStore('pricing', () => {
  const items = ref<Pricing[]>([])
  const loading = ref(false)

  const fetchAll = fetchInto({
    list: items,
    loading,
    message: '获取售价列表失败',
    run: (params?: { sub_category_id?: number; q?: string }) =>
      pricingApi.getAll(params),
  })

  const { create, update, remove } = writeActions<Pricing, PricingCreate, PricingUpdate>({
    list: items,
    api: pricingApi,
    messages: {
      create: '创建售价记录失败',
      update: '更新售价记录失败',
      remove: '删除售价记录失败',
    },
  })

  return { items, loading, fetchAll, create, update, remove }
})
