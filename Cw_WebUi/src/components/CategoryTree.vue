<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NSpin, NButton, NIcon, NModal } from 'naive-ui'
import {
  AddOutline,
  TrashOutline,
  FolderOutline,
  FolderOpenOutline,
  DocumentOutline,
} from '@vicons/ionicons5'
import { useCategoryStore } from '@/stores/category'
import { useSubCategoryStore } from '@/stores/subCategory'
import { useItemStore } from '@/stores/item'
import CategoryForm from './CategoryForm.vue'

const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()
const itemStore = useItemStore()

const expandedCategories = ref<Set<number>>(new Set())
const showSubCategoryForm = ref(false)
const contextCategoryId = ref<number | null>(null)
const showDeleteConfirm = ref(false)
const categoryToDelete = ref<{ id: number; name: string } | null>(null)

onMounted(() => {
  categoryStore.fetchAll()
})

function toggleCategory(catId: number) {
  if (expandedCategories.value.has(catId)) {
    expandedCategories.value.delete(catId)
  } else {
    expandedCategories.value.add(catId)
    subCategoryStore.fetchByCategory(catId)
  }
}

function handleSelectSubCategory(subId: number) {
  subCategoryStore.select(subId)
  itemStore.fetchBySubCategory(subId)
}

function handleAddSubCategory(catId: number) {
  contextCategoryId.value = catId
  showSubCategoryForm.value = true
}

function handleDeleteCategory(cat: { id: number; name: string }) {
  categoryToDelete.value = cat
  showDeleteConfirm.value = true
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

async function handleDeleteCategoryConfirm() {
  if (categoryToDelete.value) {
    console.log('删除大类:', categoryToDelete.value.id)
    showDeleteConfirm.value = false
    categoryToDelete.value = null
  }
}
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="p-3 border-b flex items-center justify-between">
      <h3 class="text-sm font-semibold text-gray-600">分类</h3>
    </div>
    <div class="flex-1 overflow-auto p-2">
      <NSpin :show="categoryStore.loading">
        <div class="space-y-0.5">
          <div
            v-for="category in categoryStore.categories"
            :key="category.id"
          >
            <!-- 大类 -->
            <div
              class="group flex items-center gap-1 px-2 py-1.5 rounded cursor-pointer hover:bg-gray-100"
              @click="toggleCategory(category.id)"
            >
              <NIcon :size="16" class="text-amber-500 flex-shrink-0">
                <FolderOpenOutline v-if="expandedCategories.has(category.id)" />
                <FolderOutline v-else />
              </NIcon>
              <span class="text-sm font-medium truncate flex-1">{{ category.name }}</span>

              <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                <NButton
                  size="tiny"
                  quaternary
                  circle
                  @click.stop="handleAddSubCategory(category.id)"
                >
                  <template #icon>
                    <NIcon :size="12"><AddOutline /></NIcon>
                  </template>
                </NButton>
                <NButton
                  size="tiny"
                  quaternary
                  circle
                  type="error"
                  @click.stop="handleDeleteCategory({ id: category.id, name: category.name })"
                >
                  <template #icon>
                    <NIcon :size="12"><TrashOutline /></NIcon>
                  </template>
                </NButton>
              </div>
            </div>

            <!-- 子分类列表 -->
            <div
              v-if="expandedCategories.has(category.id)"
              class="ml-5 border-l-2 border-gray-200"
            >
              <div
                v-for="sub in subCategoryStore.subCategories.filter(s => s.category_id === category.id)"
                :key="sub.id"
                class="flex items-center gap-2 px-2 py-1 cursor-pointer rounded text-sm"
                :class="subCategoryStore.selectedId === sub.id
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'"
                @click.stop="handleSelectSubCategory(sub.id)"
              >
                <NIcon :size="14" class="flex-shrink-0">
                  <DocumentOutline />
                </NIcon>
                <span class="truncate flex-1">{{ sub.name }}</span>
                <span class="text-xs text-gray-400">{{ sub.quantity }}</span>
              </div>
              <div
                v-if="subCategoryStore.subCategories.filter(s => s.category_id === category.id).length === 0"
                class="px-2 py-1 text-xs text-gray-400 italic"
              >
                暂无子分类
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
      @positive-click="handleDeleteCategoryConfirm"
      @negative-click="showDeleteConfirm = false"
    />
  </div>
</template>
