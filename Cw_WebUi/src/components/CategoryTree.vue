<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { NTree, NTreeOption, NSpin } from 'naive-ui'
import { useCategoryStore } from '@/stores/category'
import { useSubCategoryStore } from '@/stores/subCategory'
import { useItemStore } from '@/stores/item'
import CategoryForm from './CategoryForm.vue'

const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()
const itemStore = useItemStore()

const selectedCategoryId = ref<number | null>(null)
const showSubCategoryForm = ref(false)
const contextCategoryId = ref<number | null>(null)

const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)

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
  document.addEventListener('click', closeContextMenu)
  document.addEventListener('contextmenu', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
  document.removeEventListener('contextmenu', closeContextMenu)
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

function handleNodeContextmenu(e: MouseEvent) {
  const target = e.target as HTMLElement
  const nodeEl = target.closest('.n-tree-node')

  if (nodeEl) {
    const keyAttr = nodeEl.querySelector('[data-key]')?.getAttribute('data-key')
    if (keyAttr && keyAttr.startsWith('cat-')) {
      e.preventDefault()
      e.stopPropagation()

      const catId = parseInt(keyAttr.replace('cat-', ''), 10)
      contextCategoryId.value = catId
      contextMenuX.value = e.clientX
      contextMenuY.value = e.clientY
      contextMenuVisible.value = true
    }
  }
}

function closeContextMenu() {
  contextMenuVisible.value = false
}

function handleContextMenuAction() {
  if (contextCategoryId.value) {
    showSubCategoryForm.value = true
  }
  closeContextMenu()
}

async function handleSubCategorySubmit(data: Record<string, string>) {
  if (contextCategoryId.value) {
    await subCategoryStore.create(
      contextCategoryId.value,
      data.name,
      data.unit,
      data.description,
      data.notes
    )
    subCategoryStore.fetchByCategory(contextCategoryId.value)
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
          @contextmenu="handleNodeContextmenu"
        />
      </NSpin>
    </div>

    <div
      v-if="contextMenuVisible"
      class="fixed bg-white border rounded-lg shadow-lg py-1 z-50"
      :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }"
    >
      <div
        class="px-4 py-2 hover:bg-gray-100 cursor-pointer text-sm"
        @click="handleContextMenuAction"
      >
        新增子分类
      </div>
    </div>

    <CategoryForm
      v-model:visible="showSubCategoryForm"
      type="subCategory"
      title="新增子分类"
      @submit="handleSubCategorySubmit"
    />
  </div>
</template>
