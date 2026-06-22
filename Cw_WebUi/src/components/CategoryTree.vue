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
