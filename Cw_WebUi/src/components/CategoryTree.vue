<script setup lang="ts">
import { ref, onMounted, computed, h } from 'vue'
import { NSpin, NButton, NIcon, NModal, NText } from 'naive-ui'
import { AddOutline, TrashOutline } from '@vicons/ionicons5'
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
const showDeleteConfirm = ref(false)
const categoryToDelete = ref<{ id: number; name: string } | null>(null)

interface TreeNode {
  key: string
  label: string
  isLeaf: boolean
  children?: TreeNode[]
  suffix?: () => any
}

const treeData = computed<TreeNode[]>(() =>
  categoryStore.categories.map((cat) => ({
    key: `cat-${cat.id}`,
    label: cat.name,
    isLeaf: false,
    suffix: () => h('span', { class: 'flex gap-1' }, [
      h(NButton, {
        size: 'tiny',
        quaternary: true,
        circle: true,
        onClick: (e: Event) => {
          e.stopPropagation()
          contextCategoryId.value = cat.id
          showSubCategoryForm.value = true
        },
      }, {
        default: () => h(NIcon, { size: 14 }, { default: () => h(AddOutline) }),
      }),
      h(NButton, {
        size: 'tiny',
        quaternary: true,
        circle: true,
        type: 'error',
        onClick: (e: Event) => {
          e.stopPropagation()
          categoryToDelete.value = { id: cat.id, name: cat.name }
          showDeleteConfirm.value = true
        },
      }, {
        default: () => h(NIcon, { size: 14 }, { default: () => h(TrashOutline) }),
      }),
    ]),
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

async function handleDeleteCategory() {
  if (categoryToDelete.value) {
    // TODO: 实现删除大类的 API
    console.log('删除大类:', categoryToDelete.value.id)
    showDeleteConfirm.value = false
    categoryToDelete.value = null
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
        <div class="space-y-1">
          <div
            v-for="category in treeData"
            :key="category.key"
            class="group"
          >
            <div
              class="flex items-center justify-between px-2 py-1.5 rounded hover:bg-gray-100 cursor-pointer"
              @click="handleExpand([category.key])"
            >
              <span class="text-sm truncate">{{ category.label }}</span>
              <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <NButton
                  size="tiny"
                  quaternary
                  circle
                  @click.stop="contextCategoryId = parseInt(category.key.replace('cat-', ''), 10); showSubCategoryForm = true"
                >
                  <template #icon>
                    <NIcon :size="14"><AddOutline /></NIcon>
                  </template>
                </NButton>
                <NButton
                  size="tiny"
                  quaternary
                  circle
                  type="error"
                  @click.stop="categoryToDelete = { id: parseInt(category.key.replace('cat-', ''), 10), name: category.label }; showDeleteConfirm = true"
                >
                  <template #icon>
                    <NIcon :size="14"><TrashOutline /></NIcon>
                  </template>
                </NButton>
              </div>
            </div>

            <div
              v-if="selectedCategoryId === parseInt(category.key.replace('cat-', ''), 10)"
              class="ml-4 space-y-0.5"
            >
              <div
                v-for="child in category.children"
                :key="child.key"
                class="flex items-center px-2 py-1 rounded cursor-pointer text-sm"
                :class="subCategoryStore.selectedId === parseInt(child.key.replace('sub-', ''), 10)
                  ? 'bg-blue-100 text-blue-600'
                  : 'hover:bg-gray-100'"
                @click="handleSelect([child.key])"
              >
                {{ child.label }}
              </div>
            </div>
          </div>
        </div>
      </NSpin>
    </div>

    <CategoryForm
      v-model:visible="showSubCategoryForm"
      type="subCategory"
      title="新增子分类"
      @submit="handleSubCategorySubmit"
    />

    <NModal
      v-model:show="showDeleteConfirm"
      preset="dialog"
      title="确认删除"
      :content="`确定要删除大类「${categoryToDelete?.name}」吗？`"
      positive-text="删除"
      negative-text="取消"
      type="error"
      @positive-click="handleDeleteCategory"
      @negative-click="showDeleteConfirm = false"
    />
  </div>
</template>
