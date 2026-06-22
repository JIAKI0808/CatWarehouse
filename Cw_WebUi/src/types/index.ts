export interface Category {
  id: number
  name: string
  description: string
}

export interface CategoryCreate {
  name: string
  description?: string
}

export interface SubCategory {
  id: number
  category_id: number
  name: string
  quantity: number
  unit: string
  description: string
  notes: string
}

export interface SubCategoryCreate {
  category_id: number
  name: string
  unit?: string
  description?: string
  notes?: string
}

export interface Item {
  id: number
  sub_category_id: number
  name: string
  entry_date: string | null
  update_date: string | null
  recorder: string
  price: number
  description: string
}

export interface ItemCreate {
  sub_category_id: number
  name: string
  recorder?: string
  price?: number
  description?: string
}

export interface ItemUpdate {
  name?: string
  recorder?: string
  price?: number
  description?: string
}

export type ViewMode = 'table' | 'card'
