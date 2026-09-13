/**
 * i18n 实例与语言偏好读写（移动端）。
 *
 * 与网页端的 `Cw_WebUi/src/i18n.ts` 是**同构的一份**（同一个作者、同样的约定），
 * 但**不共享模块** —— 移动端是独立构建、独立发布的应用，不参与网页端→客户端的镜像。
 * 两端各自的取舍理由见 `src/locales/zh-CN.ts` 的说明。
 *
 * ## 为什么语言偏好存在 localStorage 而不是只存后端
 *
 * 后端有 `GET/PUT /api/i18n/preference`，但**首屏渲染不能等它** ——
 * 服务端不可达是本应用的正常状态。localStorage 是首屏的真实来源，
 * 后端那份用于「多设备保持一致」。
 *
 * ## 为什么默认 `zh-CN` 而不是 `navigator.language`
 *
 * 国际化之前界面**硬编码中文**。跟随浏览器/系统语言会让「本来一直看中文」的用户
 * 在升级后突然看到英文 —— 那是行为变化，不是改进。想换语言的用户去设置页显式选。
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

/**
 * 语言在**它自己那门语言里**的名字（endonym）。
 * 语言选择器是给看不懂当前界面语言的人用的，故这张表**不参与翻译**。
 */
export const LOCALE_LABELS: Record<AppLocale, string> = {
  'zh-CN': '简体中文',
  'en-US': 'English',
}

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
    // 隐私模式 / WebView 限制下 localStorage 可能直接抛异常 —— 语言不该因此让应用起不来
    return DEFAULT_LOCALE
  }
}

/**
 * 用户**是否显式选过**语言。与 `readStoredLocale()` 的区别：后者在没选过时会回默认值，
 * 看不出「没选过」。设置页要靠这个区分来决断「要不要采纳后端存的偏好」。
 */
export function hasStoredLocale(): boolean {
  try {
    return isSupportedLocale(localStorage.getItem(STORAGE_KEY))
  } catch {
    return false
  }
}

// 泛型顺序是 <Schema, Locales, Legacy>。第三个 `false` **必须显式给**：
// 默认是 `true`（legacy 模式），那时 `global.locale` 是普通字符串而不是 ref，
// 赋值不会触发重渲染，且类型上拿不到 `.value`。
export const i18n = createI18n<MessageSchema, AppLocale, false>({
  legacy: false,
  globalInjection: true,
  locale: readStoredLocale(),
  fallbackLocale: DEFAULT_LOCALE,
  messages: { 'zh-CN': zhCN, 'en-US': enUS },
})

/** 当前生效的 locale（永远是受支持的值）。 */
export function currentLocale(): AppLocale {
  const value: string = i18n.global.locale.value
  return isSupportedLocale(value) ? value : DEFAULT_LOCALE
}

/**
 * 切换语言并落盘。返回**实际生效**的 locale（传了不支持的值得回默认）。
 * 返回生效值而不是 void：调用方要把这个值同步给后端，同步的必须是「真的生效了」的那个。
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
 * 在**组件之外**（Pinia store、`services/api`）取译文。
 *
 * ⚠️ **不要在模板或 computed 里用它**：返回的是调用**当下**的字符串，**不是响应式的**。
 * 界面文案请用 `useI18n()` 的 `t`。本函数只用于「出错时取一条兜底消息」这种一次性读取。
 *
 * 反过来说，也正因为它**每次调用时**才查表，store 里的兜底文案才能跟着语言走 ——
 * 若在 store 创建时就把中文取成常量，切语言就失效了。
 */
export function translate(key: string, named?: Record<string, unknown>): string {
  return named ? i18n.global.t(key, named) : i18n.global.t(key)
}

/**
 * 把后端返回的 `detail` 原文翻成当前语言。
 * **查不到就原样返回原文，绝不返回空串** —— 后端新增端点时很容易漏进语言包。
 */
export function translateBackendMessage(detail: string): string {
  const table = i18n.global.getLocaleMessage(currentLocale()) as BackendTable
  return table.backend?.[detail] ?? detail
}
