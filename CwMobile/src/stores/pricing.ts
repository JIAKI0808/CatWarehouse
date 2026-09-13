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
    messageKey: 'app.stores.fetchPricingFailed',
    run: (params?: { sub_category_id?: number; q?: string }) => pricingApi.getAll(params),
  })

  const { create, update, remove } = writeActions<Pricing, PricingCreate, PricingUpdate>({
    list: items,
    api: pricingApi,
    messageKeys: {
      create: 'app.stores.createPricingFailed',
      update: 'app.stores.updatePricingFailed',
      remove: 'app.stores.removePricingFailed',
    },
  })

  return { items, loading, fetchAll, create, update, remove }
})
