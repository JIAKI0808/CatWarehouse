/**
 * i18n 实例与语言偏好读写。
 *
 * ## 为什么语言偏好存在 localStorage，而不是只存在后端
 *
 * 后端有 `GET/PUT /api/i18n/preference`（见 `CwServer/api/i18n/`），但首屏渲染**不能**等它：
 * 服务端不可达是本应用的正常状态。所以 **localStorage 是首屏的真实来源**，
 * 后端那份用于「多设备保持一致」，由设置页在可连通时同步（见 P2b）。
 * 这也意味着**换设备不会自动带过语言**，除非后端可达 —— 这个取舍是刻意的。
 *
 * ## 为什么默认是 `zh-CN` 而不是 `navigator.language`
 *
 * 国际化之前，本应用的界面**硬编码中文**。默认跟随浏览器语言会让
 * 「本来一直看中文」的用户在升级后突然看到英文 —— 那是行为变化，不是改进。
 * 想换语言的用户去设置页显式选。默认值保持与升级前逐字一致。
 */
import { createI18n } from 'vue-i18n'

import enUS from './locales/en-US'
import zhCN from './locales/zh-CN'
import type { MessageSchema } from './locales/zh-CN'

export const SUPPORTED_LOCALES = ['zh-CN', 'en-US'] as const

export type AppLocale = (typeof SUPPORTED_LOCALES)[number]

/** 与国际化之前硬编码的中文一致，保证升级后默认观感不变。 */
export const DEFAULT_LOCALE: AppLocale = 'zh-CN'

const STORAGE_KEY = 'locale'

/** 语言包里的 `backend` 分区：后端的 `detail` 原文 → 本地化文本。 */
type BackendTable = { backend?: Record<string, string> }

export function isSupportedLocale(value: unknown): value is AppLocale {
  return typeof value === 'string' && (SUPPORTED_LOCALES as readonly string[]).includes(value)
}

/** 读 localStorage 里的偏好；读不到 / 不认识 / 被禁用，一律回默认语言。 */
export function readStoredLocale(): AppLocale {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return isSupportedLocale(saved) ? saved : DEFAULT_LOCALE
  } catch {
    // 隐私模式下 localStorage 可能直接抛异常 —— 语言不该因此让应用起不来
    return DEFAULT_LOCALE
  }
}

// 泛型顺序是 <Schema, Locales, Legacy>。第三个参数 `false` **必须显式给**：
// 默认是 `true`（legacy 模式），那时 `global.locale` 是一个普通字符串而不是 ref，
// 赋值不会触发重渲染 —— 界面切了语言但不刷新，且类型上也拿不到 `.value`。
export const i18n = createI18n<MessageSchema, AppLocale, false>({
  legacy: false,
  globalInjection: true,
  locale: readStoredLocale(),
  fallbackLocale: DEFAULT_LOCALE,
  messages: { 'zh-CN': zhCN, 'en-US': enUS },
})

/** 当前生效的 locale（永远是受支持的值，不会是任意字符串）。 */
export function currentLocale(): AppLocale {
  const value: string = i18n.global.locale.value
  return isSupportedLocale(value) ? value : DEFAULT_LOCALE
}

/**
 * 切换语言并落盘。返回**实际生效**的 locale（传了不支持的值得回默认）。
 *
 * 返回生效值而不是 void：调用方要把这个值同步给后端，
 * 同步的必须是「真的生效了」的那个，而不是自己请求的那个。
 */
export function setLocale(locale: string): AppLocale {
  const next = isSupportedLocale(locale) ? locale : DEFAULT_LOCALE
  i18n.global.locale.value = next
  try {
    localStorage.setItem(STORAGE_KEY, next)
  } catch {
    // 写不进去不影响本次会话 —— 只是下次启动会回到默认
  }
  return next
}

/**
 * 把后端返回的 `detail` 原文翻成当前语言。
 *
 * **查不到就原样返回原文，绝不返回空串** —— 后端新增端点时很容易漏进语言包，
 * 显示英文原文总比显示空白强（与后端 `locales/catalog.py::lookup` 同一取向）。
 */
export function translateBackendMessage(detail: string): string {
  const table = i18n.global.getLocaleMessage(currentLocale()) as BackendTable
  return table.backend?.[detail] ?? detail
}
