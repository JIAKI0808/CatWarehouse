import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMessage } from '@/composables/useMessage'
import type { StockAlert } from '@/types'
import { alertApi } from '@/services/api'

export const useAlertStore = defineStore('alert', () => {
  const alerts = ref<StockAlert[]>([])
  const threshold = ref(5)
  const loading = ref(false)

  const alertCount = computed(() => alerts.value.length)

  async function fetchAlerts() {
    loading.value = true
    try {
      alerts.value = await alertApi.getAlerts(threshold.value)
    } catch (e: any) {
      useMessage().error(e.message || '获取预警失败')
    } finally {
      loading.value = false
    }
  }

  async function fetchConfig() {
    try {
      const config = await alertApi.getConfig()
      threshold.value = config.threshold
    } catch (e: any) {
      useMessage().error(e.message || '获取配置失败')
    }
  }

  async function updateConfig(newThreshold: number) {
    try {
      await alertApi.updateConfig(newThreshold)
      threshold.value = newThreshold
      await fetchAlerts()
    } catch (e: any) {
      useMessage().error(e.message || '更新配置失败')
    }
  }

  return { alerts, threshold, loading, alertCount, fetchAlerts, fetchConfig, updateConfig }
})
