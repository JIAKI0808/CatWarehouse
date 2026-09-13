<script setup lang="ts">
import { ref, h, watch, nextTick, computed } from 'vue'
import { NDataTable, NButton, NSpace, NSpin } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { gsap } from 'gsap'
import { useI18n } from 'vue-i18n'
import { useItemStore } from '@/stores/item'
import { useCurrencyStore } from '@/stores/currency'
import type { Item } from '@/types'
import ItemForm from './ItemForm.vue'
import ViewToggle from './ViewToggle.vue'

const itemStore = useItemStore()
const currencyStore = useCurrencyStore()
const { t } = useI18n()

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

// computed 而非 const：列标题与操作按钮文案都要随语言切换重算。
const columns = computed<DataTableColumns<Item>>(() => [
  { title: t('app.common.name'), key: 'name', sorter: true },
  {
    title: t('app.common.price'),
    key: 'price',
    sorter: true,
    render: (row) => `${currencyStore.symbol}${row.price.toFixed(2)}`,
  },
  {
    title: t('app.common.stock'),
    key: 'quantity',
    sorter: true,
    render: (row) => `${row.quantity} ${row.unit}`,
  },
  {
    title: t('app.common.updatedAt'),
    key: 'update_date',
    render: (row) =>
      row.update_date ? new Date(row.update_date).toLocaleDateString() : '-',
  },
  {
    title: t('app.common.expiresAt'),
    key: 'expire_date',
    render: (row) =>
      row.expire_date ? new Date(row.expire_date).toLocaleDateString() : '-',
  },
  { title: t('app.common.description'), key: 'description' },
  { title: t('app.common.recorder'), key: 'recorder' },
  {
    title: t('app.common.actions'),
    key: 'actions',
    render: (row) =>
      h(NSpace, () => [
        h(
          NButton,
          { size: 'small', onClick: () => handleEdit(row) },
          { default: () => t('app.common.edit') }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'error',
            onClick: () => handleDelete(row.id),
          },
          { default: () => t('app.common.remove') }
        ),
      ]),
  },
])

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
    <div class="flex items-center justify-between p-4 border-b">
      <div class="text-lg font-medium">{{ t('app.inventory.title') }}</div>
      <ViewToggle />
    </div>
    <div class="flex-1 overflow-auto p-4 min-h-0">
      <NSpin :show="itemStore.loading">
        <NDataTable
          :columns="columns"
          :data="itemStore.items"
          :bordered="false"
          :single-line="false"
          :style="{ height: '100%' }"
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
