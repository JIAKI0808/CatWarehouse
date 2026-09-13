<script setup lang="ts">
import { ref, h, onMounted, computed } from 'vue'
import { NDataTable, NButton, NInput, NSpace, NModal } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import { usePricingStore } from '@/stores/pricing'
import { useCurrencyStore } from '@/stores/currency'
import PricingForm from './PricingForm.vue'
import type { Pricing, PricingCreate } from '@/types'

const store = usePricingStore()
const currencyStore = useCurrencyStore()
const { t } = useI18n()

const showForm = ref(false)
const editingItem = ref<Pricing | null>(null)
const searchQuery = ref('')
const showDeleteConfirm = ref(false)
const itemToDelete = ref<number | null>(null)

onMounted(() => {
  store.fetchAll()
})

const columns = computed(() => [
  { title: t('app.pricing.productName'), key: 'name', width: 120 },
  {
    title: t('app.pricing.cost'),
    key: 'cost',
    width: 80,
    render: (row: Pricing) => `${currencyStore.symbol}${row.cost.toFixed(2)}`,
  },
  {
    title: t('app.pricing.suggestedPrice'),
    key: 'suggested_price',
    width: 100,
    render: (row: Pricing) => `${currencyStore.symbol}${row.suggested_price.toFixed(2)}`,
  },
  { title: t('app.pricing.discount'), key: 'discount', width: 80 },
  { title: t('app.common.description'), key: 'description', width: 150 },
  { title: t('app.common.notes'), key: 'notes', width: 100 },
  {
    title: t('app.pricing.recordDate'),
    key: 'record_date',
    width: 100,
    render: (row: Pricing) =>
      row.record_date ? new Date(row.record_date).toLocaleDateString() : '-',
  },
  {
    title: t('app.common.actions'), key: 'actions', width: 120,
    render: (row: Pricing) => {
      return h('div', { class: 'flex gap-1' }, [
        h(NButton, { size: 'tiny', onClick: () => handleEdit(row) }, () => t('app.common.edit')),
        h(
          NButton,
          { size: 'tiny', type: 'error', onClick: () => handleDelete(row.id) },
          () => t('app.common.remove')
        ),
      ])
    },
  },
])

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
      <h2 class="text-lg font-bold">{{ t('app.pricing.title') }}</h2>
      <NSpace>
        <NInput
          v-model:value="searchQuery"
          :placeholder="t('app.pricing.searchPlaceholder')"
          clearable
          style="width: 200px"
          @update:value="handleSearch"
        />
        <NButton type="primary" @click="handleAdd">{{ t('app.common.create') }}</NButton>
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
      :title="t('app.common.confirmDeleteTitle')"
      :content="t('app.pricing.deleteConfirm')"
      :positive-text="t('app.common.remove')"
      :negative-text="t('app.common.cancel')"
      type="error"
      @positive-click="handleDeleteConfirm"
      @negative-click="showDeleteConfirm = false"
    />
  </div>
</template>
