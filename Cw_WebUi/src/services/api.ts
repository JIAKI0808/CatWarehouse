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
  getBySubCategory: (subCategoryId: number) =>
    request<Item[]>(
      `/api/items?sub_category_id=${subCategoryId}`
    ),
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
}
