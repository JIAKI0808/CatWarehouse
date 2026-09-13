import type {
  Category,
  CategoryCreate,
  CategoryUpdate,
  SubCategory,
  SubCategoryCreate,
  SubCategoryUpdate,
  Item,
  ItemCreate,
  ItemUpdate,
  SettingsResponse,
  SettingsUpdate,
  VersionResponse,
  TrendData,
  AnalyticsOverview,
  CategoryStat,
  MonthlyCompare,
  Ledger,
  LedgerCreate,
  LedgerUpdate,
  LedgerStats,
  Budget,
  BudgetCreate,
  BudgetUpdate,
  Notification,
  Tag,
  TagCreate,
  TagUpdate,
  StockAlert,
  RecurringBill,
  RecurringBillCreate,
  RecurringBillUpdate,
  Pricing,
  PricingCreate,
  PricingUpdate,
  PricingCategory,
  PricingCategoryCreate,
  PricingCategoryUpdate,
  PricingSubCategory,
  PricingSubCategoryCreate,
  PricingSubCategoryUpdate,
  LocaleListResponse,
  LocalePreference,
  MessagePackResponse,
  CurrencyPreference,
  CurrencyInfo,
} from '@/types'
import { useServerConfigStore } from '@/stores/serverConfig'
import { translate } from '@/i18n'

function getBaseUrl(): string {
  try {
    return useServerConfigStore().getBaseUrl()
  } catch {
    return 'http://localhost:11222'
  }
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${getBaseUrl()}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    let detail = translate('app.api.requestFailed', { status: response.status })
    try {
      const body = await response.json()
      if (body.detail) detail = body.detail
    } catch {}
    throw new Error(detail)
  }
  return response.json()
}

/** 一个资源的写操作三件套。`createWriteApi` 产出它，`stores/actions.ts` 消费它。 */
export interface WriteApi<T, C, U> {
  create: (data: C) => Promise<T>
  update: (id: number, data: U) => Promise<T>
  delete: (id: number) => Promise<unknown>
}

/**
 * 创建型·工厂：资源路径 → 标准写操作三件套。
 *
 * 下面 10 个资源的 create/update/delete 本来就是同一段实现换了路径，收敛到这里后
 * 各 api 对象只剩自己特有的读操作。方法名、URL、请求体、返回类型**逐字不变**。
 */
export function createWriteApi<T, C, U>(path: string): WriteApi<T, C, U> {
  return {
    create: (data: C) =>
      request<T>(path, { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: U) =>
      request<T>(`${path}/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id: number) => request(`${path}/${id}`, { method: 'DELETE' }),
  }
}

export const categoryApi = {
  getAll: () => request<Category[]>('/api/categories'),
  getById: (id: number) => request<Category>(`/api/categories/${id}`),
  ...createWriteApi<Category, CategoryCreate, CategoryUpdate>('/api/categories'),
}

export const subCategoryApi = {
  getByCategory: (categoryId: number) =>
    request<SubCategory[]>(
      `/api/sub-categories?category_id=${categoryId}`
    ),
  getById: (id: number) =>
    request<SubCategory>(`/api/sub-categories/${id}`),
  ...createWriteApi<SubCategory, SubCategoryCreate, SubCategoryUpdate>('/api/sub-categories'),
  getQuantity: (id: number) =>
    request<{ sub_category_id: number; quantity: number }>(
      `/api/sub-categories/${id}/quantity`
    ),
}

export const itemApi = {
  getBySubCategory: (subCategoryId: number, q?: string) => {
    const params = new URLSearchParams({ sub_category_id: String(subCategoryId) })
    if (q) params.set('q', q)
    return request<Item[]>(`/api/items?${params}`)
  },
  search: (q: string) =>
    request<Item[]>(`/api/items?q=${encodeURIComponent(q)}`),
  getById: (id: number) => request<Item>(`/api/items/${id}`),
  ...createWriteApi<Item, ItemCreate, ItemUpdate>('/api/items'),
}

export const settingsApi = {
  get: () => request<SettingsResponse>('/api/settings'),
  update: (data: SettingsUpdate) =>
    request<SettingsResponse>('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  getVersion: () => request<VersionResponse>('/api/settings/version'),
}

export interface ExportData {
  categories: Array<{
    name: string
    description: string
    icon: string
    icon_color: string
    sub_categories: Array<{
      name: string
      unit: string
      description: string
      notes: string
      items: Array<{
        name: string
        recorder: string
        price: number
        description: string
        expire_date: string | null
        is_expired: boolean
      }>
    }>
  }>
}

export interface ConflictItem {
  type: string
  name: string
  existing_id: number
  imported_data: Record<string, unknown>
}

export interface ImportResult {
  categories_created: number
  sub_categories_created: number
  items_created: number
}

export const exportApi = {
  getData: () => request<ExportData>('/api/export'),
}

export const importApi = {
  checkConflicts: (data: ExportData) =>
    request<{ has_conflicts: boolean; conflicts: ConflictItem[] }>(
      '/api/import/conflicts',
      { method: 'POST', body: JSON.stringify(data) }
    ),
  execute: (data: ExportData, skipConflicts: string[] = []) =>
    request<ImportResult>('/api/import/execute', {
      method: 'POST',
      body: JSON.stringify({ categories: data.categories, skip_conflicts: skipConflicts }),
    }),
}

export const connectionApi = {
  test: () => request<{ ok: boolean }>('/api/settings/test-connection'),
}

export const analyticsApi = {
  getTrend: (subCategoryId: number) =>
    request<TrendData>(`/api/analytics/trend?sub_category_id=${subCategoryId}`),
  getOverview: () => request<AnalyticsOverview>('/api/analytics/overview'),
  getCategoryStats: () => request<CategoryStat[]>('/api/analytics/category-stats'),
  getMonthlyCompare: () => request<MonthlyCompare[]>('/api/analytics/monthly-compare'),
}

export const ledgerApi = {
  getAll: (params?: { q?: string; type?: string; start_date?: string; end_date?: string }) => {
    const searchParams = new URLSearchParams()
    if (params?.q) searchParams.set('q', params.q)
    if (params?.type) searchParams.set('type', params.type)
    if (params?.start_date) searchParams.set('start_date', params.start_date)
    if (params?.end_date) searchParams.set('end_date', params.end_date)
    const qs = searchParams.toString()
    return request<Ledger[]>(`/api/ledger${qs ? '?' + qs : ''}`)
  },
  ...createWriteApi<Ledger, LedgerCreate, LedgerUpdate>('/api/ledger'),
  getStats: (range: string) =>
    request<LedgerStats[]>(`/api/ledger/stats?range=${range}`),
}

export const budgetApi = {
  getAll: (month?: string) => {
    const params = month ? `?month=${month}` : ''
    return request<Budget[]>(`/api/budget${params}`)
  },
  ...createWriteApi<Budget, BudgetCreate, BudgetUpdate>('/api/budget'),
  getSummary: (month: string) =>
    request<Budget[]>(`/api/budget/summary?month=${month}`),
}

export const notificationApi = {
  getAll: () => request<Notification[]>('/api/notifications'),
  markRead: (id: number) =>
    request(`/api/notifications/${id}/read`, { method: 'PUT' }),
  check: () => request<{ created: number }>('/api/notifications/check', { method: 'POST' }),
}

export const tagApi = {
  getAll: () => request<Tag[]>('/api/tags'),
  ...createWriteApi<Tag, TagCreate, TagUpdate>('/api/tags'),
  addToItem: (itemId: number, tagId: number) =>
    request(`/api/items/${itemId}/tags/${tagId}`, { method: 'POST' }),
  removeFromItem: (itemId: number, tagId: number) =>
    request(`/api/items/${itemId}/tags/${tagId}`, { method: 'DELETE' }),
  getItemTags: (itemId: number) =>
    request<Tag[]>(`/api/items/${itemId}/tags`),
}

export const alertApi = {
  getAlerts: (threshold: number = 5) =>
    request<StockAlert[]>(`/api/alerts?threshold=${threshold}`),
  getConfig: () => request<{ threshold: number }>('/api/alerts/config'),
  updateConfig: (threshold: number) =>
    request<{ threshold: number }>('/api/alerts/config', {
      method: 'PUT',
      body: JSON.stringify({ threshold }),
    }),
}

export const recurringApi = {
  getAll: () => request<RecurringBill[]>('/api/recurring'),
  ...createWriteApi<RecurringBill, RecurringBillCreate, RecurringBillUpdate>('/api/recurring'),
  generate: () =>
    request<{ created: number }>('/api/recurring/generate', { method: 'POST' }),
}

export const uploadApi = {
  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch(`${getBaseUrl()}/api/upload`, {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) throw new Error(translate('app.api.uploadFailed'))
    return response.json()
  },
}

export const backupApi = {
  create: () => request<{ filename: string }>('/api/backup', { method: 'POST' }),
  list: () => request<{ filename: string; size: number; created: string }[]>('/api/backup/list'),
}

/**
 * 货币。`getAll` 是既有的；`getPreference` / `updatePreference` 接
 * `api/system/currency_router.py` 在「通用化」环新增的两个端点。
 *
 * 写 `updatePreference` 只传 `code` —— 符号由服务端查表，客户端自报会被忽略。
 */
/**
 * 计量单位字典（`/api/units`，「通用化」环新增）。
 * 返回**字符串数组**（`["个","包",...]`）—— 单位是要写进数据库的**数据**，
 * 不是界面文案，所以不做 i18n 包装。
 */
export const unitApi = {
  getAll: () => request<string[]>('/api/units'),
}

export const currencyApi = {
  getAll: () => request<CurrencyInfo[]>('/api/currencies'),
  getPreference: () => request<CurrencyPreference>('/api/currencies/preference'),
  updatePreference: (code: string) =>
    request<CurrencyPreference>('/api/currencies/preference', {
      method: 'PUT',
      body: JSON.stringify({ code }),
    }),
}

export const pricingApi = {
  getAll: (params?: { sub_category_id?: number; q?: string }) => {
    const searchParams = new URLSearchParams()
    if (params?.sub_category_id) searchParams.set('sub_category_id', String(params.sub_category_id))
    if (params?.q) searchParams.set('q', params.q)
    const qs = searchParams.toString()
    return request<Pricing[]>(`/api/pricing${qs ? '?' + qs : ''}`)
  },
  ...createWriteApi<Pricing, PricingCreate, PricingUpdate>('/api/pricing'),
}

export const pricingCategoryApi = {
  getAll: () => request<PricingCategory[]>('/api/pricing-categories'),
  ...createWriteApi<PricingCategory, PricingCategoryCreate, PricingCategoryUpdate>(
    '/api/pricing-categories'
  ),
}

export const pricingSubCategoryApi = {
  getAll: (categoryId?: number) => {
    const params = categoryId ? `?category_id=${categoryId}` : ''
    return request<PricingSubCategory[]>(`/api/pricing-sub-categories${params}`)
  },
  ...createWriteApi<PricingSubCategory, PricingSubCategoryCreate, PricingSubCategoryUpdate>(
    '/api/pricing-sub-categories'
  ),
}

/**
 * 国际化（后端 `api/i18n` 分区）。
 *
 * 四个方法**全部实现**，即使界面当前只用到 preference 两个 ——
 * 合同第 3 条是「完成移动端对后端接口的适配」，留一半没接就不叫完整。
 *
 * `getMessages` 的 locale 走 `encodeURIComponent`：路径段里的 `zh-CN` 安全，
 * 但别的写法（语言标签允许带空格等）就未必，编码是零成本的保险。
 */
export const i18nApi = {
  getLocales: () => request<LocaleListResponse>('/api/i18n/locales'),
  getMessages: (locale: string) =>
    request<MessagePackResponse>(`/api/i18n/messages/${encodeURIComponent(locale)}`),
  getPreference: () => request<LocalePreference>('/api/i18n/preference'),
  updatePreference: (locale: string) =>
    request<LocalePreference>('/api/i18n/preference', {
      method: 'PUT',
      body: JSON.stringify({ locale }),
    }),
}
