/**
 * 计价货币偏好（移动端）。
 *
 * 与 `Cw_WebUi/src/stores/currency.ts` **同构的一份** —— 移动端不参与网页端→客户端的镜像，
 * 是独立构建的应用，所以各自留一份（与两端语言包各存一份是同一个取舍）。
 *
 * ## 默认值就是现状（与 i18n 默认 zh-CN 同一个手法）
 *
 * 未配置 / 请求失败时用 `¥`，与后端 `CNY` 默认一致 ⇒ **界面逐字不变**。
 * 「接入货币能力」这件事本身**不产生任何可见变化**，只有用户显式改了货币才会变。
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
   * 保持默认符号即可。`symbol` 为空串时也回退 —— 空符号会让界面上只剩数字。
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
