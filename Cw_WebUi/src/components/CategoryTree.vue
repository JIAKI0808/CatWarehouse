<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { NTree, NTreeOption, NSpin } from 'naive-ui'
import { useCategoryStore } from '@/stores/category'
import { useSubCategoryStore } from '@/stores/subCategory'
import { useItemStore } from '@/stores/item'

const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()
const itemStore = useItemStore()

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
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="p-3 border-b">
      <h3 class="text-sm font-semibold text-gray-600">分类</h3>
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
  </div>
</template>
