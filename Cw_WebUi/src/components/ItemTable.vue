<script setup lang="ts">
import { ref, h, watch, nextTick } from 'vue'
import { NDataTable, NButton, NSpace, NSpin } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import { gsap } from 'gsap'
import { useItemStore } from '@/stores/item'
import type { Item } from '@/types'
import ItemForm from './ItemForm.vue'

const itemStore = useItemStore()
const showItemForm = ref(false)
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
