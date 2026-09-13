export interface Category {
  id: number
  name: string
  description: string
  icon?: string
  icon_color?: string
}

export interface CategoryCreate {
  name: string
  description?: string
  icon?: string
  icon_color?: string
}

export interface CategoryUpdate {
  name?: string
  description?: string
  icon?: string
  icon_color?: string
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
  expire_date: string | null
  is_expired: boolean
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
  expire_date?: string | null
  is_expired?: boolean
}

export interface ItemUpdate {
  name?: string
  recorder?: string
  price?: number
  description?: string
  quantity?: number
  unit?: string
  expire_date?: string | null
  is_expired?: boolean
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

export interface TrendPoint {
  date: string
  quantity: number
  price: number
  total_price: number
  unit_price: number
}

export interface Ledger {
  id: number
  amount: number
  date: string
  platform: string
  description: string
  notes: string
  person: string
  type: 'income' | 'expense'
}

export interface LedgerCreate {
  amount: number
  date: string
  platform?: string
  description?: string
  notes?: string
  person?: string
  type?: 'income' | 'expense'
}

export interface LedgerUpdate {
  amount?: number
  date?: string
  platform?: string
  description?: string
  notes?: string
  person?: string
  type?: 'income' | 'expense'
}

export interface LedgerStats {
  period: string
  income: number
  expense: number
}

export interface TrendData {
  sub_category_id: number
  sub_category_name: string
  unit: string
  data: TrendPoint[]
}

export interface AnalyticsOverview {
  total_items: number
  total_value: number
  total_income: number
  total_expense: number
}

export interface CategoryStat {
  name: string
  value: number
}

export interface MonthlyCompare {
  month: string
  income: number
  expense: number
}

export interface Notification {
  id: number
  type: string
  message: string
  is_read: boolean
  created_at: string
  related_id: number | null
}

export interface Tag {
  id: number
  name: string
  color: string
}

export interface TagCreate {
  name: string
  color?: string
}

export interface TagUpdate {
  name?: string
  color?: string
}

export interface StockAlert {
  id: number
  type: string
  message: string
  quantity: number
  threshold: number
}

export interface RecurringBill {
  id: number
  amount: number
  description: string
  platform: string
  person: string
  type: 'income' | 'expense'
  frequency: 'monthly' | 'yearly'
  next_date: string
  is_active: boolean
}

export interface RecurringBillCreate {
  amount: number
  description?: string
  platform?: string
  person?: string
  type?: 'income' | 'expense'
  frequency?: 'monthly' | 'yearly'
  next_date: string
}

export interface RecurringBillUpdate {
  amount?: number
  description?: string
  platform?: string
  person?: string
  type?: 'income' | 'expense'
  frequency?: 'monthly' | 'yearly'
  next_date?: string
  is_active?: boolean
}

export interface Budget {
  id: number
  category_id: number
  category_name: string
  month: string
  amount: number
  spent: number
}

export interface BudgetCreate {
  category_id: number
  month: string
  amount: number
}

export interface BudgetUpdate {
  category_id?: number
  month?: string
  amount?: number
}

export interface Pricing {
  id: number
  sub_category_id: number
  sub_category_name: string
  name: string
  cost: number
  suggested_price: number
  discount: number
  description: string
  notes: string
  record_date: string | null
}

export interface PricingCreate {
  sub_category_id: number
  name: string
  cost?: number
  suggested_price?: number
  discount?: number
  description?: string
  notes?: string
}

export interface PricingUpdate {
  name?: string
  cost?: number
  suggested_price?: number
  discount?: number
  description?: string
  notes?: string
}

export interface PricingCategory {
  id: number
  name: string
  description: string
}

export interface PricingCategoryCreate {
  name: string
  description?: string
}

export interface PricingCategoryUpdate {
  name?: string
  description?: string
}

export interface PricingSubCategory {
  id: number
  category_id: number
  name: string
  description: string
}

export interface PricingSubCategoryCreate {
  category_id: number
  name: string
  description?: string
}

export interface PricingSubCategoryUpdate {
  name?: string
  description?: string
}

// ---------------------------------------------------------------------------
// i18n（后端 `api/i18n` 分区）
// ---------------------------------------------------------------------------

/** `GET /api/i18n/locales` —— 支持哪些语言。刻意不写死在前端。 */
export interface LocaleListResponse {
  default: string
  locales: string[]
}

/** `GET|PUT /api/i18n/preference` */
export interface LocalePreference {
  locale: string
}

/**
 * `GET /api/i18n/messages/{locale}` —— 后端文案包。
 * `backend_messages` 的键是后端 `detail` 的**原文**，值是本地化文本。
 */
export interface MessagePackResponse {
  locale: string
  meta: Record<string, unknown>
  backend_messages: Record<string, string>
}
