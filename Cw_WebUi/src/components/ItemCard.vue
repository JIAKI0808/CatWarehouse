<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { NCard, NGrid, NGridItem, NButton, NSpace, NSpin } from 'naive-ui'
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
    gsap.from('.n-card', {
      opacity: 0,
      scale: 0.8,
      duration: 0.3,
      stagger: 0.05,
    })
  }
)

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
