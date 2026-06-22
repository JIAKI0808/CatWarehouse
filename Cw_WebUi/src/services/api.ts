import type {
  Category,
  CategoryCreate,
  SubCategory,
  SubCategoryCreate,
  Item,
  ItemCreate,
  ItemUpdate,
} from '@/types'

const API_BASE_URL = 'http://localhost:11222'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`)
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
