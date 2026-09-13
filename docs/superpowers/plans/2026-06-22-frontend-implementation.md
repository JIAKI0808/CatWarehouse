# CatWarehouse 前端实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 使用 Vue 3 + Naive UI + GSAP 构建三级分类库存管理系统的前端界面

**Architecture:** 采用集中式状态管理（Pinia），组件化设计，GSAP 动画增强交互体验

**Tech Stack:** Vue 3, TypeScript, Pinia, Naive UI, GSAP, Vite

## Global Constraints

- 单个函数不能超过 50 行
- 单行函数不能超过 120 字符
- 使用 Composition API + `<script setup>` 语法
- API 地址: http://localhost:11222

---

## File Structure

```
Cw_WebUi/src/
├── types/
│   └── index.ts               # TypeScript 类型定义
├── services/
│   └── api.ts                 # HTTP 客户端封装
├── stores/
│   ├── category.ts            # 大类状态管理
│   ├── subCategory.ts         # 子分类状态管理
│   └── item.ts                # 物品状态管理
├── components/
│   ├── CategoryTree.vue       # 左侧分类树
│   ├── ItemTable.vue          # 表格视图
│   ├── ItemCard.vue           # 卡片视图
│   ├── ItemForm.vue           # 新增/编辑物品表单
│   ├── CategoryForm.vue       # 新增分类/子分类表单
│   └── ViewToggle.vue         # 表格/卡片切换按钮
└── views/
    └── HomeView.vue           # 主页面
```

---

### Task 1: 安装依赖

**Files:**
- Modify: `Cw_WebUi/package.json`

**Dependencies:** None

- [ ] **Step 1: 进入前端目录并安装依赖**

```bash
cd Cw_WebUi
npm install naive-ui gsap @vicons/ionicons5
```

- [ ] **Step 2: 验证安装成功**

```bash
npm list naive-ui gsap @vicons/ionicons5
```

Expected: 显示已安装的包版本

- [ ] **Step 3: Commit**

```bash
git add package.json package-lock.json
git commit -m "chore: install naive-ui, gsap, and icon dependencies"
```

---

### Task 2: 创建类型定义

**Files:**
- Create: `Cw_WebUi/src/types/index.ts`

**Dependencies:** None

- [ ] **Step 1: 创建类型定义文件**

```typescript
// Cw_WebUi/src/types/index.ts

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
```

- [ ] **Step 2: Commit**

```bash
git add src/types/index.ts
git commit -m "feat: add TypeScript type definitions"
```

---

### Task 3: 创建 API 服务

**Files:**
- Create: `Cw_WebUi/src/services/api.ts`

**Dependencies:** Task 2 (types)

- [ ] **Step 1: 创建 API 服务文件**

```typescript
// Cw_WebUi/src/services/api.ts

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
```

- [ ] **Step 2: Commit**

```bash
git add src/services/api.ts
git commit -m "feat: add API service layer"
```

---

### Task 4: 创建 Category Store

**Files:**
- Create: `Cw_WebUi/src/stores/category.ts`

**Dependencies:** Task 2 (types), Task 3 (api)

- [ ] **Step 1: 创建 Category Store**

```typescript
// Cw_WebUi/src/stores/category.ts

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Category } from '@/types'
import { categoryApi } from '@/services/api'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])
  const selectedId = ref<number | null>(null)
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      categories.value = await categoryApi.getAll()
    } finally {
      loading.value = false
    }
  }

  async function create(name: string, description: string = '') {
    const newCategory = await categoryApi.create({ name, description })
    categories.value.push(newCategory)
    return newCategory
  }

  function select(id: number | null) {
    selectedId.value = id
  }

  return {
    categories,
    selectedId,
    loading,
    fetchAll,
    create,
    select,
  }
})
```

- [ ] **Step 2: Commit**

```bash
git add src/stores/category.ts
git commit -m "feat: add category store"
```

---

### Task 5: 创建 SubCategory Store

**Files:**
- Create: `Cw_WebUi/src/stores/subCategory.ts`

**Dependencies:** Task 2 (types), Task 3 (api)

- [ ] **Step 1: 创建 SubCategory Store**

```typescript
// Cw_WebUi/src/stores/subCategory.ts

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { SubCategory } from '@/types'
import { subCategoryApi } from '@/services/api'

export const useSubCategoryStore = defineStore('subCategory', () => {
  const subCategories = ref<SubCategory[]>([])
  const selectedId = ref<number | null>(null)
  const loading = ref(false)

  async function fetchByCategory(categoryId: number) {
    loading.value = true
    try {
      subCategories.value = await subCategoryApi.getByCategory(categoryId)
    } finally {
      loading.value = false
    }
  }

  async function create(
    categoryId: number,
    name: string,
    unit: string = '个',
    description: string = '',
    notes: string = ''
  ) {
    const newSubCategory = await subCategoryApi.create({
      category_id: categoryId,
      name,
      unit,
      description,
      notes,
    })
    subCategories.value.push(newSubCategory)
    return newSubCategory
  }

  function select(id: number | null) {
    selectedId.value = id
  }

  return {
    subCategories,
    selectedId,
    loading,
    fetchByCategory,
    create,
    select,
  }
})
```

- [ ] **Step 2: Commit**

```bash
git add src/stores/subCategory.ts
git commit -m "feat: add sub-category store"
```

---

### Task 6: 创建 Item Store

**Files:**
- Create: `Cw_WebUi/src/stores/item.ts`

**Dependencies:** Task 2 (types), Task 3 (api)

- [ ] **Step 1: 创建 Item Store**

```typescript
// Cw_WebUi/src/stores/item.ts

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Item, ItemCreate, ItemUpdate, ViewMode } from '@/types'
import { itemApi } from '@/services/api'

export const useItemStore = defineStore('item', () => {
  const items = ref<Item[]>([])
  const loading = ref(false)
  const viewMode = ref<ViewMode>('table')

  async function fetchBySubCategory(subCategoryId: number) {
    loading.value = true
    try {
      items.value = await itemApi.getBySubCategory(subCategoryId)
    } finally {
      loading.value = false
    }
  }

  async function create(data: ItemCreate) {
    const newItem = await itemApi.create(data)
    items.value.push(newItem)
    return newItem
  }

  async function update(id: number, data: ItemUpdate) {
    const updatedItem = await itemApi.update(id, data)
    const index = items.value.findIndex((item) => item.id === id)
    if (index !== -1) {
      items.value[index] = updatedItem
    }
    return updatedItem
  }

  async function remove(id: number) {
    await itemApi.delete(id)
    items.value = items.value.filter((item) => item.id !== id)
  }

  function setViewMode(mode: ViewMode) {
    viewMode.value = mode
  }

  function clearItems() {
    items.value = []
  }

  return {
    items,
    loading,
    viewMode,
    fetchBySubCategory,
    create,
    update,
    remove,
    setViewMode,
    clearItems,
  }
})
```

- [ ] **Step 2: Commit**

```bash
git add src/stores/item.ts
git commit -m "feat: add item store"
```

---

### Task 7: 创建 ViewToggle 组件

**Files:**
- Create: `Cw_WebUi/src/components/ViewToggle.vue`

**Dependencies:** Task 2 (types), Task 6 (item store)

- [ ] **Step 1: 创建 ViewToggle 组件**

```vue
<!-- Cw_WebUi/src/components/ViewToggle.vue -->

<script setup lang="ts">
import { NButtonGroup, NButton } from 'naive-ui'
import { GridOutline, CardsOutline } from '@vicons/ionicons5'
import { useItemStore } from '@/stores/item'
import type { ViewMode } from '@/types'

const itemStore = useItemStore()

const options = [
  { label: '表格', value: 'table', icon: GridOutline },
  { label: '卡片', value: 'card', icon: CardsOutline },
]

function handleChange(mode: ViewMode) {
  itemStore.setViewMode(mode)
}
</script>

<template>
  <NButtonGroup>
    <NButton
      v-for="option in options"
      :key="option.value"
      :type="itemStore.viewMode === option.value ? 'primary' : 'default'"
      @click="handleChange(option.value)"
    >
      <component :is="option.icon" class="mr-1" />
      {{ option.label }}
    </NButton>
  </NButtonGroup>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/ViewToggle.vue
git commit -m "feat: add view toggle component"
```

---

### Task 8: 创建 CategoryForm 组件

**Files:**
- Create: `Cw_WebUi/src/components/CategoryForm.vue`

**Dependencies:** Task 2 (types)

- [ ] **Step 1: 创建 CategoryForm 组件**

```vue
<!-- Cw_WebUi/src/components/CategoryForm.vue -->

<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NButton } from 'naive-ui'

const props = defineProps<{
  visible: boolean
  type: 'category' | 'subCategory'
  title: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: Record<string, string>): void
}>()

const form = ref({
  name: '',
  description: '',
  unit: '个',
  notes: '',
})

watch(
  () => props.visible,
  (val) => {
    if (!val) {
      resetForm()
    }
  }
)

function resetForm() {
  form.value = {
    name: '',
    description: '',
    unit: '个',
    notes: '',
  }
}

function handleClose() {
  emit('update:visible', false)
}

function handleSubmit() {
  emit('submit', { ...form.value })
  handleClose()
}
</script>

<template>
  <NModal :show="visible" @update:show="emit('update:visible', $event)">
    <div class="bg-white rounded-lg p-6 w-96">
      <h2 class="text-lg font-bold mb-4">{{ title }}</h2>
      <NForm>
        <NFormItem label="名称">
          <NInput v-model:value="form.name" placeholder="请输入名称" />
        </NFormItem>
        <NFormItem label="描述">
          <NInput
            v-model:value="form.description"
            type="textarea"
            placeholder="请输入描述"
          />
        </NFormItem>
        <template v-if="type === 'subCategory'">
          <NFormItem label="单位">
            <NInput v-model:value="form.unit" placeholder="个" />
          </NFormItem>
          <NFormItem label="备注">
            <NInput
              v-model:value="form.notes"
              type="textarea"
              placeholder="请输入备注"
            />
          </NFormItem>
        </template>
      </NForm>
      <div class="flex justify-end gap-2 mt-4">
        <NButton @click="handleClose">取消</NButton>
        <NButton type="primary" @click="handleSubmit">保存</NButton>
      </div>
    </div>
  </NModal>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/CategoryForm.vue
git commit -m "feat: add category form component"
```

---

### Task 9: 创建 ItemForm 组件

**Files:**
- Create: `Cw_WebUi/src/components/ItemForm.vue`

**Dependencies:** Task 2 (types)

- [ ] **Step 1: 创建 ItemForm 组件**

```vue
<!-- Cw_WebUi/src/components/ItemForm.vue -->

<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NInputNumber, NButton } from 'naive-ui'
import type { Item } from '@/types'

const props = defineProps<{
  visible: boolean
  item?: Item | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: Record<string, unknown>): void
}>()

const form = ref({
  name: '',
  price: 0,
  recorder: '',
  description: '',
})

watch(
  () => props.visible,
  (val) => {
    if (val && props.item) {
      form.value = {
        name: props.item.name,
        price: props.item.price,
        recorder: props.item.recorder,
        description: props.item.description,
      }
    } else if (!val) {
      resetForm()
    }
  }
)

function resetForm() {
  form.value = {
    name: '',
    price: 0,
    recorder: '',
    description: '',
  }
}

function handleClose() {
  emit('update:visible', false)
}

function handleSubmit() {
  emit('submit', { ...form.value })
  handleClose()
}
</script>

<template>
  <NModal :show="visible" @update:show="emit('update:visible', $event)">
    <div class="bg-white rounded-lg p-6 w-96">
      <h2 class="text-lg font-bold mb-4">
        {{ item ? '编辑物品' : '新增物品' }}
      </h2>
      <NForm>
        <NFormItem label="名称">
          <NInput v-model:value="form.name" placeholder="请输入名称" />
        </NFormItem>
        <NFormItem label="价格">
          <NInputNumber v-model:value="form.price" :min="0" :precision="2">
            <template #prefix>¥</template>
          </NInputNumber>
        </NFormItem>
        <NFormItem label="录入人">
          <NInput v-model:value="form.recorder" placeholder="请输入录入人" />
        </NFormItem>
        <NFormItem label="描述">
          <NInput
            v-model:value="form.description"
            type="textarea"
            placeholder="请输入描述"
          />
        </NFormItem>
      </NForm>
      <div class="flex justify-end gap-2 mt-4">
        <NButton @click="handleClose">取消</NButton>
        <NButton type="primary" @click="handleSubmit">保存</NButton>
      </div>
    </div>
  </NModal>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/ItemForm.vue
git commit -m "feat: add item form component"
```

---

### Task 10: 创建 CategoryTree 组件

**Files:**
- Create: `Cw_WebUi/src/components/CategoryTree.vue`

**Dependencies:** Task 4 (category store), Task 5 (subCategory store), Task 6 (item store), Task 8 (category form)

- [ ] **Step 1: 创建 CategoryTree 组件**

```vue
<!-- Cw_WebUi/src/components/CategoryTree.vue -->

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { NButton, NTree, NTreeOption, NSpin } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import { useCategoryStore } from '@/stores/category'
import { useSubCategoryStore } from '@/stores/subCategory'
import { useItemStore } from '@/stores/item'
import CategoryForm from './CategoryForm.vue'

const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()
const itemStore = useItemStore()

const showCategoryForm = ref(false)
const showSubCategoryForm = ref(false)
const selectedCategoryId = ref<number | null>(null)

const treeData = computed<NTreeOption[]>(() =>
  categoryStore.categories.map((cat) => ({
    key: `cat-${cat.id}`,
    label: cat.name,
    isLeaf: false,
    children: subCategoryStore.subCategories
      .filter((sub) => sub.category_id === cat.id)
      .map((sub) => ({
        key: `sub-${sub.id}`,
        label: `${sub.name} (${sub.quantity})`,
        isLeaf: true,
      })),
  }))
)

const selectedKeys = computed(() => {
  if (subCategoryStore.selectedId) {
    return [`sub-${subCategoryStore.selectedId}`]
  }
  return []
})

onMounted(() => {
  categoryStore.fetchAll()
})

function handleExpand(keys: string[]) {
  const categoryId = keys
    .filter((k) => k.startsWith('cat-'))
    .map((k) => parseInt(k.replace('cat-', ''), 10))[0]
  if (categoryId) {
    selectedCategoryId.value = categoryId
    subCategoryStore.fetchByCategory(categoryId)
  }
}

function handleSelect(keys: string[]) {
  const subKey = keys.find((k) => k.startsWith('sub-'))
  if (subKey) {
    const subId = parseInt(subKey.replace('sub-', ''), 10)
    subCategoryStore.select(subId)
    itemStore.fetchBySubCategory(subId)
  }
}

function handleAddCategory() {
  showCategoryForm.value = true
}

function handleAddSubCategory() {
  showSubCategoryForm.value = true
}

async function handleCategorySubmit(data: Record<string, string>) {
  await categoryStore.create(data.name, data.description)
}

async function handleSubCategorySubmit(data: Record<string, string>) {
  if (selectedCategoryId.value) {
    await subCategoryStore.create(
      selectedCategoryId.value,
      data.name,
      data.unit,
      data.description,
      data.notes
    )
  }
}
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="p-2 border-b flex gap-2">
      <NButton size="small" @click="handleAddCategory">
        <AddOutline class="mr-1" />
        新增大类
      </NButton>
      <NButton size="small" @click="handleAddSubCategory">
        <AddOutline class="mr-1" />
        新增子分类
      </NButton>
    </div>
    <div class="flex-1 overflow-auto p-2">
      <NSpin :show="categoryStore.loading">
        <NTree
          :data="treeData"
          :selected-keys="selectedKeys"
          default-expand-all
          @update:expanded-keys="handleExpand"
          @update:selected-keys="handleSelect"
        />
      </NSpin>
    </div>

    <CategoryForm
      v-model:visible="showCategoryForm"
      type="category"
      title="新增大类"
      @submit="handleCategorySubmit"
    />

    <CategoryForm
      v-model:visible="showSubCategoryForm"
      type="subCategory"
      title="新增子分类"
      @submit="handleSubCategorySubmit"
    />
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/CategoryTree.vue
git commit -m "feat: add category tree component"
```

---

### Task 11: 创建 ItemTable 组件

**Files:**
- Create: `Cw_WebUi/src/components/ItemTable.vue`

**Dependencies:** Task 2 (types), Task 6 (item store), Task 9 (item form)

- [ ] **Step 1: 创建 ItemTable 组件**

```vue
<!-- Cw_WebUi/src/components/ItemTable.vue -->

<script setup lang="ts">
import { ref, h } from 'vue'
import { NDataTable, NButton, NSpace, NSpin } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import { useItemStore } from '@/stores/item'
import type { Item } from '@/types'
import ItemForm from './ItemForm.vue'

const itemStore = useItemStore()
const showItemForm = ref(false)
const editingItem = ref<Item | null>(null)

const columns: DataTableColumns<Item> = [
  { title: '名称', key: 'name', sorter: true },
  {
    title: '价格',
    key: 'price',
    sorter: true,
    render: (row) => `¥${row.price.toFixed(2)}`,
  },
  { title: '录入人', key: 'recorder' },
  {
    title: '录入日期',
    key: 'entry_date',
    render: (row) =>
      row.entry_date ? new Date(row.entry_date).toLocaleDateString() : '-',
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) =>
      h(NSpace, () => [
        h(
          NButton,
          { size: 'small', onClick: () => handleEdit(row) },
          { default: () => '编辑' }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'error',
            onClick: () => handleDelete(row.id),
          },
          { default: () => '删除' }
        ),
      ]),
  },
]

function handleAdd() {
  editingItem.value = null
  showItemForm.value = true
}

function handleEdit(item: Item) {
  editingItem.value = item
  showItemForm.value = true
}

async function handleDelete(id: number) {
  await itemStore.remove(id)
}

async function handleSubmit(data: Record<string, unknown>) {
  if (editingItem.value) {
    await itemStore.update(editingItem.value.id, data)
  } else {
    await itemStore.create(data as any)
  }
}
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="p-2 border-b flex justify-between items-center">
      <span class="font-bold">
        物品列表 ({{ itemStore.items.length }})
      </span>
      <NButton size="small" type="primary" @click="handleAdd">
        <AddOutline class="mr-1" />
        新增物品
      </NButton>
    </div>
    <div class="flex-1 overflow-auto p-2">
      <NSpin :show="itemStore.loading">
        <NDataTable
          :columns="columns"
          :data="itemStore.items"
          :bordered="false"
          :single-line="false"
        />
      </NSpin>
    </div>

    <ItemForm
      v-model:visible="showItemForm"
      :item="editingItem"
      @submit="handleSubmit"
    />
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/ItemTable.vue
git commit -m "feat: add item table component"
```

---

### Task 12: 创建 ItemCard 组件

**Files:**
- Create: `Cw_WebUi/src/components/ItemCard.vue`

**Dependencies:** Task 2 (types), Task 6 (item store), Task 9 (item form)

- [ ] **Step 1: 创建 ItemCard 组件**

```vue
<!-- Cw_WebUi/src/components/ItemCard.vue -->

<script setup lang="ts">
import { ref } from 'vue'
import { NCard, NGrid, NGridItem, NButton, NSpace, NSpin } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import { useItemStore } from '@/stores/item'
import type { Item } from '@/types'
import ItemForm from './ItemForm.vue'

const itemStore = useItemStore()
const showItemForm = ref(false)
const editingItem = ref<Item | null>(null)

function handleAdd() {
  editingItem.value = null
  showItemForm.value = true
}

function handleEdit(item: Item) {
  editingItem.value = item
  showItemForm.value = true
}

async function handleDelete(id: number) {
  await itemStore.remove(id)
}

async function handleSubmit(data: Record<string, unknown>) {
  if (editingItem.value) {
    await itemStore.update(editingItem.value.id, data)
  } else {
    await itemStore.create(data as any)
  }
}

function formatDate(dateStr: string | null): string {
  return dateStr ? new Date(dateStr).toLocaleDateString() : '-'
}
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="p-2 border-b flex justify-between items-center">
      <span class="font-bold">
        物品列表 ({{ itemStore.items.length }})
      </span>
      <NButton size="small" type="primary" @click="handleAdd">
        <AddOutline class="mr-1" />
        新增物品
      </NButton>
    </div>
    <div class="flex-1 overflow-auto p-2">
      <NSpin :show="itemStore.loading">
        <NGrid :cols="3" :x-gap="12" :y-gap="12">
          <NGridItem v-for="item in itemStore.items" :key="item.id">
            <NCard :title="item.name" size="small">
              <div class="space-y-2">
                <div>价格: ¥{{ item.price.toFixed(2) }}</div>
                <div>录入人: {{ item.recorder }}</div>
                <div>日期: {{ formatDate(item.entry_date) }}</div>
              </div>
              <template #footer>
                <NSpace>
                  <NButton size="small" @click="handleEdit(item)">
                    编辑
                  </NButton>
                  <NButton
                    size="small"
                    type="error"
                    @click="handleDelete(item.id)"
                  >
                    删除
                  </NButton>
                </NSpace>
              </template>
            </NCard>
          </NGridItem>
        </NGrid>
      </NSpin>
    </div>

    <ItemForm
      v-model:visible="showItemForm"
      :item="editingItem"
      @submit="handleSubmit"
    />
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/ItemCard.vue
git commit -m "feat: add item card component"
```

---

### Task 13: 创建 HomeView 页面

**Files:**
- Modify: `Cw_WebUi/src/views/HomeView.vue`

**Dependencies:** Task 10 (CategoryTree), Task 11 (ItemTable), Task 12 (ItemCard), Task 7 (ViewToggle), Task 6 (item store)

- [ ] **Step 1: 更新 HomeView 页面**

```vue
<!-- Cw_WebUi/src/views/HomeView.vue -->

<script setup lang="ts">
import { NLayout, NLayoutSider, NLayoutContent } from 'naive-ui'
import { useItemStore } from '@/stores/item'
import CategoryTree from '@/components/CategoryTree.vue'
import ItemTable from '@/components/ItemTable.vue'
import ItemCard from '@/components/ItemCard.vue'
import ViewToggle from '@/components/ViewToggle.vue'

const itemStore = useItemStore()
</script>

<template>
  <NLayout has-sider class="h-screen">
    <NLayoutSider bordered :width="280">
      <CategoryTree />
    </NLayoutSider>
    <NLayoutContent>
      <div class="p-4 h-full flex flex-col">
        <div class="mb-4 flex justify-end">
          <ViewToggle />
        </div>
        <div class="flex-1 overflow-hidden">
          <ItemTable v-if="itemStore.viewMode === 'table'" />
          <ItemCard v-else />
        </div>
      </div>
    </NLayoutContent>
  </NLayout>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add src/views/HomeView.vue
git commit -m "feat: update home view with layout"
```

---

### Task 14: 更新 App.vue 和 main.ts

**Files:**
- Modify: `Cw_WebUi/src/App.vue`
- Modify: `Cw_WebUi/src/main.ts`

**Dependencies:** Task 13 (HomeView)

- [ ] **Step 1: 更新 App.vue**

```vue
<!-- Cw_WebUi/src/App.vue -->

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>
```

- [ ] **Step 2: 更新 main.ts**

```typescript
// Cw_WebUi/src/main.ts

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import naive from 'naive-ui'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(naive)
app.use(router)

app.mount('#app')
```

- [ ] **Step 3: Commit**

```bash
git add src/App.vue src/main.ts
git commit -m "feat: configure app with naive-ui and pinia"
```

---

### Task 15: 更新路由配置

**Files:**
- Modify: `Cw_WebUi/src/router/index.ts`

**Dependencies:** Task 14

- [ ] **Step 1: 更新路由配置**

```typescript
// Cw_WebUi/src/router/index.ts

import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
  ],
})

export default router
```

- [ ] **Step 2: Commit**

```bash
git add src/router/index.ts
git commit -m "feat: update router configuration"
```

---

### Task 16: 添加 GSAP 动画

**Files:**
- Modify: `Cw_WebUi/src/components/ItemTable.vue`
- Modify: `Cw_WebUi/src/components/ItemCard.vue`

**Dependencies:** Task 11, Task 12

- [ ] **Step 1: 为 ItemTable 添加 GSAP 动画**

在 ItemTable.vue 的 `<script setup>` 中添加：

```typescript
import { gsap } from 'gsap'
import { watch, nextTick } from 'vue'

watch(
  () => itemStore.items.length,
  async () => {
    await nextTick()
    gsap.from('.n-data-table-tr', {
      opacity: 0,
      y: 20,
      duration: 0.3,
      stagger: 0.05,
    })
  }
)
```

- [ ] **Step 2: 为 ItemCard 添加 GSAP 动画**

在 ItemCard.vue 的 `<script setup>` 中添加：

```typescript
import { gsap } from 'gsap'
import { watch, nextTick } from 'vue'

watch(
  () => itemStore.items.length,
  async () => {
    await nextTick()
    gsap.from('.n-card', {
      opacity: 0,
      scale: 0.8,
      duration: 0.3,
      stagger: 0.05,
    })
  }
)
```

- [ ] **Step 3: Commit**

```bash
git add src/components/ItemTable.vue src/components/ItemCard.vue
git commit -m "feat: add GSAP animations for list transitions"
```

---

### Task 17: 添加全局样式

**Files:**
- Modify: `Cw_WebUi/src/assets/main.css`

**Dependencies:** None

- [ ] **Step 1: 更新全局样式**

```css
/* Cw_WebUi/src/assets/main.css */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}

.n-layout-sider {
  background: #fff;
}

.n-layout-content {
  background: #f5f5f5;
}
```

- [ ] **Step 2: Commit**

```bash
git add src/assets/main.css
git commit -m "feat: add global styles"
```

---

### Task 18: 验证与测试

**Files:** None

**Dependencies:** All previous tasks

- [ ] **Step 1: 启动开发服务器**

```bash
cd Cw_WebUi
npm run dev
```

Expected: 服务器启动，无编译错误

- [ ] **Step 2: 检查页面加载**

在浏览器中打开 http://localhost:5173

Expected:
- 页面显示左侧分类树和右侧内容区域
- 无控制台错误

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: complete frontend implementation"
```
