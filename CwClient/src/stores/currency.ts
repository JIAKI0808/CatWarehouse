/**
 * 计价货币偏好。
 *
 * ## 「通用化」环的第一个前端消费者
 *
 * 后端早就有 `GET /api/currencies`（8 种货币含符号）、模型有 `SpecificItem.currency` 列、
 * `currencyApi` 也早就定义好了 —— 但**没有任何界面用过**，UI 到处写死 `¥`。
 * 这个 store 就是那个「真实使用者」：把符号从后端取回来，让界面不再写死。
 *
 * ## 默认值就是现状（与 i18n 默认 zh-CN 同一个手法）
 *
 * 未配置 / 请求失败时用 `¥`，与后端 `CNY` 默认一致 ⇒ **界面逐字不变**。
 * 于是「接入货币能力」这件事本身**不产生任何可见变化**，
 * 只有用户显式改了货币才会变 —— 把风险压到零，也让行为验证有确定的基线。
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { currencyApi } from '@/services/api'

/** 与后端 `DEFAULT_CURRENCY = "CNY"` 的符号一致。 */
export const DEFAULT_SYMBOL = '¥'

export const useCurrencyStore = defineStore('currency', () => {
  const code = ref('CNY')
  const symbol = ref(DEFAULT_SYMBOL)

  /**
   * 拉一次偏好。
   *
   * **失败静默**：服务器不可达是本应用的正常状态（离线可用是既有设计），
   * 保持默认符号即可，不该因此弹错或让界面出问题。
   * `symbol` 为空串时也回退 —— 空符号会让界面上只剩数字，比一个默认符号更糟。
   */
  async function fetchPreference() {
    try {
      const pref = await currencyApi.getPreference()
      code.value = pref.code || 'CNY'
      symbol.value = pref.symbol || DEFAULT_SYMBOL
    } catch {
      // 保持默认
    }
  }

  return { code, symbol, fetchPreference }
})
