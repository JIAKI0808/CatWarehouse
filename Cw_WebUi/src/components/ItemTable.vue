<script setup lang="ts">
import { ref, h, watch, nextTick } from 'vue'
import { NDataTable, NButton, NSpace, NSpin, NDropdown } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import { gsap } from 'gsap'
import { useItemStore } from '@/stores/item'
import { useCategoryStore } from '@/stores/category'
import { useSubCategoryStore } from '@/stores/subCategory'
import type { Item } from '@/types'
import ItemForm from './ItemForm.vue'
import CategoryForm from './CategoryForm.vue'

const itemStore = useItemStore()
const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()

const showItemForm = ref(false)
const showCategoryForm = ref(false)
const showSubCategoryForm = ref(false)
const editingItem = ref<Item | null>(null)

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

const addOptions = [
  { label: '新增大类', key: 'category' },
  { label: '新增子分类', key: 'subCategory' },
  { label: '新增物品', key: 'item' },
]

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

function handleAdd(key: string) {
  if (key === 'category') {
    showCategoryForm.value = true
  } else if (key === 'subCategory') {
    showSubCategoryForm.value = true
  } else {
    editingItem.value = null
    showItemForm.value = true
  }
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

async function handleCategorySubmit(data: Record<string, string>) {
  await categoryStore.create(data.name, data.description)
}

async function handleSubCategorySubmit(data: Record<string, string>) {
  await subCategoryStore.create(
    subCategoryStore.selectedId || 0,
    data.name,
    data.unit,
    data.description,
    data.notes
  )
}
</script>

<template>
  <div class="h-full flex flex-col relative">
    <div class="flex-1 overflow-auto p-4">
      <NSpin :show="itemStore.loading">
        <NDataTable
          :columns="columns"
          :data="itemStore.items"
          :bordered="false"
          :single-line="false"
        />
      </NSpin>
    </div>

    <div class="absolute bottom-6 right-6">
      <NDropdown :options="addOptions" @select="handleAdd">
        <NButton type="primary" circle size="large">
          <AddOutline :size="24" />
        </NButton>
      </NDropdown>
    </div>

    <ItemForm
      v-model:visible="showItemForm"
      :item="editingItem"
      @submit="handleSubmit"
    />

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
