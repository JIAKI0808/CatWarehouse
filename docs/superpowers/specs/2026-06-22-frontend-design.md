# CatWarehouse 前端设计方案

## 概述

基于后端已有的三级分类库存 API，使用 Vue 3 + Naive UI + GSAP 构建前端界面。

## 技术栈

- **框架**: Vue 3 (Composition API + `<script setup>`)
- **UI 库**: Naive UI
- **状态管理**: Pinia
- **动画**: GSAP
- **构建工具**: Vite
- **语言**: TypeScript

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Cw_WebUi 前端架构                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           App.vue                                   │   │
│  │  ┌──────────────┐  ┌────────────────────────────────────────────┐  │   │
│  │  │  NLayout     │  │  NLayoutContent                            │  │   │
│  │  │  NLayoutSider│  │  ┌──────────────────────────────────────┐  │  │   │
│  │  │              │  │  │  CategoryTree.vue                    │  │  │   │
│  │  │  三级分类树   │  │  │  - 显示 Category 列表               │  │  │   │
│  │  │  (GSAP 动画) │  │  │  - 展开显示 SubCategory             │  │  │   │
│  │  │              │  │  │  - 点击选择 SubCategory             │  │  │   │
│  │  │              │  │  └──────────────────────────────────────┘  │  │   │
│  │  │              │  │  ┌──────────────────────────────────────┐  │  │   │
│  │  │              │  │  │  物品列表区域                         │  │  │   │
│  │  │              │  │  │  - 表格/卡片视图切换                  │  │  │   │
│  │  │              │  │  │  - 物品 CRUD 操作                    │  │  │   │
│  │  │              │  │  └──────────────────────────────────────┘  │  │   │
│  │  └──────────────┘  └────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────── Pinia Stores ─────────────────────────────────────┐  │
│  │                                                                       │  │
│  │  categoryStore            subCategoryStore          itemStore         │  │
│  │  ──────────────           ─────────────────         ─────────         │  │
│  │  state:                   state:                    state:            │  │
│  │    categories: []           subCategories: []         items: []       │  │
│  │    selectedId: null         selectedId: null          viewMode: 'table'│  │
│  │    loading: false           loading: false            loading: false  │  │
│  │                                                                       │  │
│  │  actions:                 actions:                  actions:          │  │
│  │    fetchAll()               fetchByCategory()         fetchAll()     │  │
│  │    create()                 create()                  create()       │  │
│  │    select()                 select()                  update()       │  │
│  │                            fetchQuantity()            delete()       │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────── Services ──────────────────────────────────────────┐  │
│  │                                                                       │  │
│  │  api.ts                                                              │  │
│  │  ──────                                                              │  │
│  │  - 统一 HTTP 客户端封装 (fetch)                                       │  │
│  │  - API_BASE_URL = "http://localhost:11222"                            │  │
│  │  - 请求/响应拦截器                                                   │  │
│  │  - 错误处理                                                          │  │
│  │                                                                       │  │
│  │  endpoints:                                                           │  │
│  │    /api/categories          GET, POST                                 │  │
│  │    /api/sub-categories      GET, POST                                 │  │
│  │    /api/items               GET, POST, PUT, DELETE                    │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户操作 ──▶ Pinia Action ──▶ API Service ──▶ 后端 API
    │                                            │
    │                                            ▼
    │                                      数据库
    │                                            │
    ◀───────────────── State 更新 ◀───────────────
```

## 组件设计

### 文件结构

```
src/
├── App.vue                    # 根组件，NLayout 布局
├── main.ts                    # 入口，Naive UI + Pinia 注册
│
├── types/
│   └── index.ts               # TypeScript 类型定义
│
├── services/
│   └── api.ts                 # HTTP 客户端封装
│
├── stores/
│   ├── category.ts            # 大类状态管理
│   ├── subCategory.ts         # 子分类状态管理
│   └── item.ts                # 物品状态管理
│
├── components/
│   ├── CategoryTree.vue       # 左侧分类树
│   ├── ItemTable.vue          # 表格视图
│   ├── ItemCard.vue           # 卡片视图
│   ├── ItemForm.vue           # 新增/编辑物品表单
│   ├── CategoryForm.vue       # 新增分类/子分类表单
│   └── ViewToggle.vue         # 表格/卡片切换按钮
│
└── views/
    └── HomeView.vue           # 主页面，组合所有组件
```

### 组件详细设计

#### 1. CategoryTree.vue（左侧分类树）

```
┌─────────────────────────────────────────┐
│  [+] 新增大类                           │
├─────────────────────────────────────────┤
│  ▼ 日用品                               │
│    ├── 洗护用品                         │
│    │   └── 洗发水 (5)                   │
│    └── 清洁用品                         │
│        └── 洗洁精 (3)                   │
│  ▶ 食物                                 │
│  ▶ 配料                                 │
└─────────────────────────────────────────┘
```

- 使用 Naive UI `NTree` 组件
- GSAP 动画：展开/折叠时的平滑过渡
- 点击子分类时高亮并加载物品列表
- 右键菜单：编辑、删除分类

#### 2. ItemTable.vue（表格视图）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  物品管理 - 洗发水 (5)                          [新增物品] [切换卡片视图]    │
├─────────────────────────────────────────────────────────────────────────────┤
│  名称          │ 价格    │ 录入人  │ 录入日期    │ 操作                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  海飞丝洗发水   │ ¥29.9  │ 张三   │ 2024-01-15 │ [编辑] [删除]           │
│  潘婷洗发水     │ ¥35.5  │ 李四   │ 2024-01-16 │ [编辑] [删除]           │
│  飘柔洗发水     │ ¥25.0  │ 张三   │ 2024-01-17 │ [编辑] [删除]           │
└─────────────────────────────────────────────────────────────────────────────┘
```

- 使用 Naive UI `NDataTable` 组件
- 支持排序、筛选
- GSAP 动画：新增/删除行时的淡入淡出

#### 3. ItemCard.vue（卡片视图）

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  海飞丝洗发水    │  │  潘婷洗发水      │  │  飘柔洗发水      │
│  ─────────────  │  │  ─────────────  │  │  ─────────────  │
│  价格: ¥29.9    │  │  价格: ¥35.5    │  │  价格: ¥25.0    │
│  录入人: 张三   │  │  录入人: 李四    │  │  录入人: 张三    │
│  日期: 2024-01- │  │  日期: 2024-01- │  │  日期: 2024-01- │
│  [编辑] [删除]  │  │  [编辑] [删除]  │  │  [编辑] [删除]  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

- 使用 Naive UI `NCard` 组件
- GSAP 动画：卡片进入/退出时的缩放和淡入淡出

#### 4. ItemForm.vue（物品表单）

```
┌─────────────────────────────────────────┐
│  新增物品                                │
├─────────────────────────────────────────┤
│  名称: [                    ]           │
│  价格: [                    ]           │
│  录入人: [                  ]           │
│  描述: [                    ]           │
│  ─────────────────────────────────────  │
│  [取消]                         [保存]  │
└─────────────────────────────────────────┘
```

- 使用 Naive UI `NModal` + `NForm` 组件
- GSAP 动画：弹窗出现/消失时的缩放和透明度动画

## GSAP 动画设计

### 1. 页面过渡动画 (Route Transition)

- 使用 Vue Router + GSAP 实现页面切换
- 效果：淡入淡出 + 轻微位移
- 时长：0.3s

### 2. 分类树展开/折叠 (Tree Expand/Collapse)

- 子节点展开时：height: 0 → auto, opacity: 0 → 1
- 子节点折叠时：height: auto → 0, opacity: 1 → 0
- 时长：0.25s

### 3. 物品列表动画 (List Animation)

- 新增物品：从下方滑入 + 淡入
- 删除物品：向右滑出 + 淡出
- 切换分类：旧列表淡出 → 新列表淡入
- 时长：0.3s

### 4. 弹窗动画 (Modal Animation)

- 弹窗出现：scale(0.8) → scale(1), opacity: 0 → 1
- 弹窗消失：scale(1) → scale(0.8), opacity: 1 → 0
- 时长：0.25s

### 5. 视图切换动画 (View Toggle)

- 表格 → 卡片：表格淡出 → 卡片淡入
- 卡片 → 表格：卡片淡出 → 表格淡入
- 时长：0.3s

## API Service 封装

```typescript
// services/api.ts
const API_BASE_URL = 'http://localhost:11222'

// 请求封装
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) throw new Error(`API Error: ${response.status}`)
  return response.json()
}

// API 方法
export const categoryApi = {
  getAll: () => request<Category[]>('/api/categories'),
  create: (data: CategoryCreate) => request<Category>('/api/categories', {
    method: 'POST', body: JSON.stringify(data)
  }),
}

export const subCategoryApi = {
  getByCategory: (categoryId: number) =>
    request<SubCategory[]>(`/api/sub-categories?category_id=${categoryId}`),
  create: (data: SubCategoryCreate) => request<SubCategory>('/api/sub-categories', {
    method: 'POST', body: JSON.stringify(data)
  }),
  getQuantity: (id: number) =>
    request<{quantity: number}>(`/api/sub-categories/${id}/quantity`),
}

export const itemApi = {
  getBySubCategory: (subCategoryId: number) =>
    request<Item[]>(`/api/items?sub_category_id=${subCategoryId}`),
  create: (data: ItemCreate) => request<Item>('/api/items', {
    method: 'POST', body: JSON.stringify(data)
  }),
  update: (id: number, data: ItemUpdate) => request<Item>(`/api/items/${id}`, {
    method: 'PUT', body: JSON.stringify(data)
  }),
  delete: (id: number) => request(`/api/items/${id}`, {
    method: 'DELETE'
  }),
}
```

## 类型定义

```typescript
// types/index.ts
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
```

## 依赖安装

```bash
# 进入前端目录
cd Cw_WebUi

# 安装 Naive UI
npm install naive-ui

# 安装 GSAP
npm install gsap

# 安装 @vicons/ionicons5 (Naive UI 图标)
npm install @vicons/ionicons5
```
