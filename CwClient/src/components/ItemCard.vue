<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { NCard, NGrid, NGridItem, NButton, NSpace, NSpin } from 'naive-ui'
import { gsap } from 'gsap'
import { useI18n } from 'vue-i18n'
import { useItemStore } from '@/stores/item'
import { useCategoryStore } from '@/stores/category'
import type { Item } from '@/types'
import ItemForm from './ItemForm.vue'
import CategoryForm from './CategoryForm.vue'
import ViewToggle from './ViewToggle.vue'

const itemStore = useItemStore()
const categoryStore = useCategoryStore()
const { t } = useI18n()

const showItemForm = ref(false)
const showCategoryForm = ref(false)
const editingItem = ref<Item | null>(null)

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
  await categoryStore.create(data.name, data.description, data.icon, data.icon_color)
}

function formatDate(dateStr: string | null): string {
  return dateStr ? new Date(dateStr).toLocaleDateString() : '-'
}
</script>

<template>
  <div class="h-full flex flex-col relative">
    <div class="flex items-center justify-between p-4 border-b border-pink-200">
      <div class="text-lg font-bold text-gray-800">{{ t('app.inventory.title') }}</div>
      <ViewToggle />
    </div>
    <div class="flex-1 overflow-auto p-4">
      <NSpin :show="itemStore.loading">
        <div v-if="itemStore.items.length === 0 && !itemStore.loading" class="flex flex-col items-center justify-center h-64 text-gray-400">
          <div class="text-6xl mb-4">📦</div>
          <div class="text-lg">{{ t('app.common.noData') }}</div>
          <div class="text-sm mt-1">{{ t('app.inventory.emptyHint') }}</div>
        </div>
        <NGrid v-else :cols="3" :x-gap="12" :y-gap="12">
          <NGridItem v-for="item in itemStore.items" :key="item.id">
            <NCard :title="item.name" size="small" style="background-color: #fce7f3; color: black;" :header-style="{ color: 'black', fontSize: '18px', fontWeight: 'bold' }">
              <div class="space-y-2" style="color: black;">
                <div>{{ t('app.common.price') }}: ¥{{ item.price.toFixed(2) }}</div>
                <div>{{ t('app.common.stock') }}: {{ item.quantity }} {{ item.unit }}</div>
                <div>{{ t('app.common.updatedAt') }}: {{ formatDate(item.update_date) }}</div>
                <div>{{ t('app.common.description') }}: {{ item.description || '-' }}</div>
                <div>{{ t('app.common.expiresAt') }}:
                  {{ item.expire_date ? formatDate(item.expire_date) : '-' }}</div>
                <div>{{ t('app.common.expired') }}:
                  {{ item.is_expired ? t('app.common.yes') : t('app.common.no') }}</div>
                <div>{{ t('app.common.recorder') }}: {{ item.recorder }}</div>
              </div>
              <template #footer>
                <NSpace>
                  <NButton size="small" @click="handleEdit(item)">
                    {{ t('app.common.edit') }}
                  </NButton>
                  <NButton
                    size="small"
                    type="error"
                    @click="handleDelete(item.id)"
                  >
                    {{ t('app.common.remove') }}
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

    <CategoryForm
      v-model:visible="showCategoryForm"
      type="category"
      :title="t('app.inventory.addCategory')"
      @submit="handleCategorySubmit"
    />
  </div>
</template>
