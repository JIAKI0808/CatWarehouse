export interface Category {
  id: number
  name: string
  description: string
  icon?: string
}

export interface CategoryCreate {
  name: string
  description?: string
  icon?: string
}

export interface CategoryUpdate {
  name?: string
  description?: string
  icon?: string
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

export interface SubCategoryUpdate {
  name?: string
  unit?: string
  description?: string
  notes?: string
}

export interface Item {
  id: number
  sub_category_id: number
  sub_category_name: string
  quantity: number
  unit: string
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
  quantity?: number
  unit?: string
}

export type ViewMode = 'table' | 'card'

export interface AIConfig {
  api_key: string
  base_url: string
  model_name: string
  max_tokens: number
}

export interface PluginConfig {
  ai_category_suggestion: boolean
  smart_autocomplete: boolean
  description_generation: boolean
  voice_input: boolean
}

export interface SettingsResponse {
  ai_config: AIConfig
  plugin_config: PluginConfig
}

export interface SettingsUpdate {
  ai_config?: AIConfig
  plugin_config?: PluginConfig
}

export interface VersionResponse {
  app_name: string
  version: string
  description: string
  start_time: string
}
