import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import type { StockAlert } from '@/types'
import { alertApi } from '@/services/api'
import { translate } from '@/i18n'
import { fetchInto } from '@/stores/actions'

export const useAlertStore = defineStore('alert', () => {
  const alerts = ref<StockAlert[]>([])
  const threshold = ref(5)
  const loading = ref(false)

  const alertCount = computed(() => alerts.value.length)

  const fetchAlerts = fetchInto({
    list: alerts,
    loading,
    messageKey: 'app.stores.fetchAlertFailed',
    run: () => alertApi.getAlerts(threshold.value),
  })

  async function fetchConfig() {
    try {
      const config = await alertApi.getConfig()
      threshold.value = config.threshold
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.fetchAlertConfigFailed'))
    }
  }

  async function updateConfig(newThreshold: number) {
    try {
      await alertApi.updateConfig(newThreshold)
      threshold.value = newThreshold
      // 阈值变了，预警列表要按新阈值重取 —— 这一步是既有行为，不是冗余。
      await fetchAlerts()
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.updateAlertConfigFailed'))
    }
  }

  return { alerts, threshold, loading, alertCount, fetchAlerts, fetchConfig, updateConfig }
})
