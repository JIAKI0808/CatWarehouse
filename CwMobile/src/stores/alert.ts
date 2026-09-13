import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { StockAlert } from '@/types'
import { alertApi } from '@/services/api'
import { fetchInto, withMessage } from '@/stores/actions'

export const useAlertStore = defineStore('alert', () => {
  const alerts = ref<StockAlert[]>([])
  const threshold = ref(5)
  const loading = ref(false)

  const alertCount = computed(() => alerts.value.length)

  // `run` 在**调用时**读取 threshold.value，所以按新阈值重取时拿到的就是新值。
  const fetchAlerts = fetchInto({
    list: alerts,
    loading,
    message: '获取预警失败',
    run: () => alertApi.getAlerts(threshold.value),
  })

  /** 写的是 `threshold` 且不碰 `loading`（陷阱 T13）→ 只把重复的 catch 收起来。 */
  const fetchConfig = withMessage('获取配置失败', async () => {
    const config = await alertApi.getConfig()
    threshold.value = config.threshold
  })

  /**
   * 成功后立刻按新阈值重取预警列表（陷阱 T10）——这一步是既有行为，不是冗余；
   * 删掉它 threshold 与 alerts 就会不一致。
   */
  const updateConfig = withMessage('更新配置失败', async (newThreshold: number) => {
    await alertApi.updateConfig(newThreshold)
    threshold.value = newThreshold
    await fetchAlerts()
  })

  return { alerts, threshold, loading, alertCount, fetchAlerts, fetchConfig, updateConfig }
})
