<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { NCard, NGrid, NGridItem, NButton, NSpace, NSpin, NDropdown } from 'naive-ui'
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
    gsap.from('.n-card', {
      opacity: 0,
      scale: 0.8,
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

function formatDate(dateStr: string | null): string {
  return dateStr ? new Date(dateStr).toLocaleDateString() : '-'
}
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="flex-1 overflow-auto p-4">
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
