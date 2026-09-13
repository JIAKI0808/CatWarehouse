<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { NDataTable, NButton, NInput, NSpace, NModal } from 'naive-ui'
import { usePricingStore } from '@/stores/pricing'
import PricingForm from './PricingForm.vue'
import type { Pricing, PricingCreate } from '@/types'

const store = usePricingStore()

const showForm = ref(false)
const editingItem = ref<Pricing | null>(null)
const searchQuery = ref('')
const showDeleteConfirm = ref(false)
const itemToDelete = ref<number | null>(null)

onMounted(() => {
  store.fetchAll()
})

const columns = [
  { title: '商品名', key: 'name', width: 120 },
  { title: '成本', key: 'cost', width: 80, render: (row: Pricing) => `¥${row.cost.toFixed(2)}` },
  { title: '建议售价', key: 'suggested_price', width: 100, render: (row: Pricing) => `¥${row.suggested_price.toFixed(2)}` },
  { title: '折扣系数', key: 'discount', width: 80 },
  { title: '描述', key: 'description', width: 150 },
  { title: '备注', key: 'notes', width: 100 },
  { title: '记录日期', key: 'record_date', width: 100, render: (row: Pricing) => row.record_date ? new Date(row.record_date).toLocaleDateString() : '-' },
  {
    title: '操作', key: 'actions', width: 120,
    render: (row: Pricing) => {
      return h('div', { class: 'flex gap-1' }, [
        h(NButton, { size: 'tiny', onClick: () => handleEdit(row) }, () => '编辑'),
        h(NButton, { size: 'tiny', type: 'error', onClick: () => handleDelete(row.id) }, () => '删除'),
      ])
    },
  },
]

function handleAdd() {
  editingItem.value = null
  showForm.value = true
}

function handleEdit(item: Pricing) {
  editingItem.value = item
  showForm.value = true
}

function handleDelete(id: number) {
  itemToDelete.value = id
  showDeleteConfirm.value = true
}

async function handleDeleteConfirm() {
  if (itemToDelete.value) {
    await store.remove(itemToDelete.value)
    showDeleteConfirm.value = false
    itemToDelete.value = null
  }
}

async function handleSubmit(data: PricingCreate) {
  if (editingItem.value) {
    await store.update(editingItem.value.id, data)
  } else {
    await store.create(data)
  }
}

function handleSearch() {
  store.fetchAll({ q: searchQuery.value || undefined })
}

defineExpose({ handleAdd })
</script>

<template>
  <div class="h-full flex flex-col p-4">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-bold">售价管理</h2>
      <NSpace>
        <NInput v-model:value="searchQuery" placeholder="搜索商品名" clearable style="width: 200px" @update:value="handleSearch" />
        <NButton type="primary" @click="handleAdd">新增</NButton>
      </NSpace>
    </div>

    <NDataTable :columns="columns" :data="store.items" :loading="store.loading" :flex-height="true" style="flex: 1" />

    <PricingForm
      v-model:visible="showForm"
      :edit-data="editingItem"
      @submit="handleSubmit"
    />

    <NModal
      v-model:show="showDeleteConfirm"
      preset="dialog"
      title="确认删除"
      content="确定要删除这条售价记录吗？"
      positive-text="删除"
      negative-text="取消"
      type="error"
      @positive-click="handleDeleteConfirm"
      @negative-click="showDeleteConfirm = false"
    />
  </div>
</template>
