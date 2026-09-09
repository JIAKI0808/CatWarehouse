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
} from '@/types'
import { useServerConfigStore } from '@/stores/serverConfig'

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
    let detail = `请求失败 (${response.status})`
    try {
      const body = await response.json()
      if (body.detail) detail = body.detail
    } catch {}
    throw new Error(detail)
  }
  return response.json()
}

export const categoryApi = {
  getAll: () => request<Category[]>('/api/categories'),
  getById: (id: number) => request<Category>(`/api/categories/${id}`),
  create: (data: CategoryCreate) =>
    request<Category>('/api/categories', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: CategoryUpdate) =>
    request<Category>(`/api/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request(`/api/categories/${id}`, {
      method: 'DELETE',
    }),
}

export const subCategoryApi = {
  getByCategory: (categoryId: number) =>
    request<SubCategory[]>(
      `/api/sub-categories?category_id=${categoryId}`
    ),
  getById: (id: number) =>
    request<SubCategory>(`/api/sub-categories/${id}`),
  create: (data: SubCategoryCreate) =>
    request<SubCategory>('/api/sub-categories', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: SubCategoryUpdate) =>
    request<SubCategory>(`/api/sub-categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request(`/api/sub-categories/${id}`, {
      method: 'DELETE',
    }),
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
  create: (data: ItemCreate) =>
    request<Item>('/api/items', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: ItemUpdate) =>
    request<Item>(`/api/items/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request(`/api/items/${id}`, {
      method: 'DELETE',
    }),
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
  create: (data: LedgerCreate) =>
    request<Ledger>('/api/ledger', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: LedgerUpdate) =>
    request<Ledger>(`/api/ledger/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request(`/api/ledger/${id}`, { method: 'DELETE' }),
  getStats: (range: string) =>
    request<LedgerStats[]>(`/api/ledger/stats?range=${range}`),
}

export const budgetApi = {
  getAll: (month?: string) => {
    const params = month ? `?month=${month}` : ''
    return request<Budget[]>(`/api/budget${params}`)
  },
  create: (data: BudgetCreate) =>
    request<Budget>('/api/budget', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: BudgetUpdate) =>
    request<Budget>(`/api/budget/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request(`/api/budget/${id}`, { method: 'DELETE' }),
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
  create: (data: TagCreate) =>
    request<Tag>('/api/tags', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: TagUpdate) =>
    request<Tag>(`/api/tags/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request(`/api/tags/${id}`, { method: 'DELETE' }),
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
  create: (data: RecurringBillCreate) =>
    request<RecurringBill>('/api/recurring', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: RecurringBillUpdate) =>
    request<RecurringBill>(`/api/recurring/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request(`/api/recurring/${id}`, { method: 'DELETE' }),
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
    if (!response.ok) throw new Error('上传失败')
    return response.json()
  },
}

export const backupApi = {
  create: () => request<{ filename: string }>('/api/backup', { method: 'POST' }),
  list: () => request<{ filename: string; size: number; created: string }[]>('/api/backup/list'),
}

export const currencyApi = {
  getAll: () => request<{ code: string; name: string; symbol: string }[]>('/api/currencies'),
}

export const pricingApi = {
  getAll: (params?: { sub_category_id?: number; q?: string }) => {
    const searchParams = new URLSearchParams()
    if (params?.sub_category_id) searchParams.set('sub_category_id', String(params.sub_category_id))
    if (params?.q) searchParams.set('q', params.q)
    const qs = searchParams.toString()
    return request<Pricing[]>(`/api/pricing${qs ? '?' + qs : ''}`)
  },
  create: (data: PricingCreate) =>
    request<Pricing>('/api/pricing', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: PricingUpdate) =>
    request<Pricing>(`/api/pricing/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request(`/api/pricing/${id}`, { method: 'DELETE' }),
}

export const pricingCategoryApi = {
  getAll: () => request<PricingCategory[]>('/api/pricing-categories'),
  create: (data: PricingCategoryCreate) =>
    request<PricingCategory>('/api/pricing-categories', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: PricingCategoryUpdate) =>
    request<PricingCategory>(`/api/pricing-categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request(`/api/pricing-categories/${id}`, { method: 'DELETE' }),
}

export const pricingSubCategoryApi = {
  getAll: (categoryId?: number) => {
    const params = categoryId ? `?category_id=${categoryId}` : ''
    return request<PricingSubCategory[]>(`/api/pricing-sub-categories${params}`)
  },
  create: (data: PricingSubCategoryCreate) =>
    request<PricingSubCategory>('/api/pricing-sub-categories', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: PricingSubCategoryUpdate) =>
    request<PricingSubCategory>(`/api/pricing-sub-categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request(`/api/pricing-sub-categories/${id}`, { method: 'DELETE' }),
}
