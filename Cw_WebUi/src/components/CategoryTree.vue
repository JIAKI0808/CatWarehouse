<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NSpin, NButton, NIcon, NModal, NTooltip } from 'naive-ui'
import {
  AddOutline,
  TrashOutline,
  CreateOutline,
  FolderOutline,
  FolderOpenOutline,
  DocumentOutline,
  CartOutline,
  ShirtOutline,
  HardwareChipOutline,
  NutritionOutline,
  CameraOutline,
  GameControllerOutline,
  BookOutline,
  MusicalNotesOutline,
  FitnessOutline,
  HeartOutline,
  StarOutline,
  FlashlightOutline,
  ColorPaletteOutline,
  CubeOutline,
  DiamondOutline,
} from '@vicons/ionicons5'
import { useCategoryStore } from '@/stores/category'
import { useSubCategoryStore } from '@/stores/subCategory'
import { useItemStore } from '@/stores/item'
import CategoryForm from './CategoryForm.vue'
import ItemForm from './ItemForm.vue'

const iconMap: Record<string, typeof FolderOutline> = {
  FolderOutline,
  CartOutline,
  ShirtOutline,
  HardwareChipOutline,
  NutritionOutline,
  CameraOutline,
  GameControllerOutline,
  BookOutline,
  MusicalNotesOutline,
  FitnessOutline,
  HeartOutline,
  StarOutline,
  FlashlightOutline,
  ColorPaletteOutline,
  CubeOutline,
  DiamondOutline,
}

function getCategoryIcon(iconName: string | undefined) {
  return iconMap[iconName ?? 'FolderOutline'] ?? FolderOutline
}

const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()
const itemStore = useItemStore()

const expandedCategories = ref<Set<number>>(new Set())
const showCategoryForm = ref(false)
const showSubCategoryForm = ref(false)
const showItemForm = ref(false)
const contextCategoryId = ref<number | null>(null)
const contextSubCategoryId = ref<number | null>(null)
const showDeleteConfirm = ref(false)
const categoryToDelete = ref<{ id: number; name: string } | null>(null)
const showSubDeleteConfirm = ref(false)
const subCategoryToDelete = ref<{ id: number; name: string; categoryId: number } | null>(null)

const editingCategory = ref<{ id: number; name: string; description: string; icon: string } | null>(null)
const editingSubCategory = ref<{ id: number; name: string; description: string; unit: string; notes: string } | null>(null)

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

function handleAddItem(subId: number) {
  contextSubCategoryId.value = subId
  showItemForm.value = true
}

function handleDeleteCategory(cat: { id: number; name: string }) {
  categoryToDelete.value = cat
  showDeleteConfirm.value = true
}

function handleEditCategory(category: { id: number; name: string; description: string; icon: string }) {
  editingCategory.value = { ...category }
  showCategoryForm.value = true
}

function handleEditSubCategory(sub: { id: number; name: string; description: string; unit: string; notes: string }) {
  editingSubCategory.value = { ...sub }
  showSubCategoryForm.value = true
}

async function handleSubCategorySubmit(data: Record<string, string>) {
  if (editingSubCategory.value) {
    await subCategoryStore.update(editingSubCategory.value.id, {
      name: data.name,
      unit: data.unit,
      description: data.description,
      notes: data.notes,
    })
    editingSubCategory.value = null
  } else if (contextCategoryId.value) {
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

async function handleItemSubmit(data: Record<string, unknown>) {
  if (contextSubCategoryId.value) {
    await itemStore.create({
      sub_category_id: contextSubCategoryId.value,
      name: data.name as string,
      recorder: data.recorder as string,
      price: data.price as number,
      description: data.description as string,
    })
    itemStore.fetchBySubCategory(contextSubCategoryId.value)

    // 直接更新子分类数量
    for (const catId of Object.keys(subCategoryStore.subCategoriesByCategory)) {
      const list = subCategoryStore.subCategoriesByCategory[Number(catId)]
      const subIndex = list.findIndex(s => s.id === contextSubCategoryId.value)
      if (subIndex !== -1) {
        list[subIndex].quantity++
        break
      }
    }
  }
}

async function handleCategorySubmit(data: Record<string, string>) {
  if (editingCategory.value) {
    await categoryStore.update(editingCategory.value.id, {
      name: data.name,
      description: data.description,
      icon: data.icon,
    })
    editingCategory.value = null
  } else {
    await categoryStore.create(data.name, data.description, data.icon)
  }
}

async function handleDeleteCategoryConfirm() {
  if (categoryToDelete.value) {
    await categoryStore.remove(categoryToDelete.value.id)
    showDeleteConfirm.value = false
    categoryToDelete.value = null
  }
}

function handleDeleteSubCategory(sub: { id: number; name: string }, categoryId: number) {
  subCategoryToDelete.value = { id: sub.id, name: sub.name, categoryId }
  showSubDeleteConfirm.value = true
}

async function handleDeleteSubCategoryConfirm() {
  if (subCategoryToDelete.value) {
    const { categoryId, id } = subCategoryToDelete.value
    await subCategoryStore.remove(categoryId, id)
    showSubDeleteConfirm.value = false
    subCategoryToDelete.value = null
  }
}
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="p-3 border-b flex items-center justify-between">
      <h3 class="text-sm font-semibold text-gray-600">分类</h3>
      <NButton
        size="tiny"
        type="primary"
        @click="showCategoryForm = true"
      >
        <template #icon>
          <NIcon :size="14"><AddOutline /></NIcon>
        </template>
      </NButton>
    </div>
    <div class="flex-1 overflow-auto p-2">
      <NSpin :show="categoryStore.loading">
        <div class="space-y-0.5">
          <div
            v-for="category in categoryStore.categories"
            :key="category.id"
          >
            <!-- 大类 -->
            <NTooltip trigger="hover" placement="right">
              <template #trigger>
                <div
                  class="group flex items-center gap-1 px-2 py-1.5 rounded cursor-pointer hover:bg-gray-100"
                  @click="toggleCategory(category.id)"
                >
                  <NIcon :size="16" class="text-amber-500 flex-shrink-0" :component="getCategoryIcon(category.icon)" />
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
                      @click.stop="handleEditCategory(category)"
                    >
                      <template #icon>
                        <NIcon :size="12"><CreateOutline /></NIcon>
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
              </template>
              {{ category.description || '暂无描述' }}
            </NTooltip>

            <!-- 子分类列表 -->
            <div
              v-if="expandedCategories.has(category.id)"
              class="ml-5 border-l-2 border-gray-200"
            >
              <div
                v-for="sub in subCategoryStore.getSubCategories(category.id)"
                :key="sub.id"
              >
                <NTooltip trigger="hover" placement="right">
                  <template #trigger>
                    <div
                      class="group/sub flex items-center gap-2 px-2 py-1 cursor-pointer rounded text-sm"
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

                      <div class="flex gap-0.5 opacity-0 group-hover/sub:opacity-100 transition-opacity">
                        <NButton
                          size="tiny"
                          quaternary
                          circle
                          @click.stop="handleAddItem(sub.id)"
                        >
                          <template #icon>
                            <NIcon :size="12"><AddOutline /></NIcon>
                          </template>
                        </NButton>
                        <NButton
                          size="tiny"
                          quaternary
                          circle
                          @click.stop="handleEditSubCategory(sub)"
                        >
                          <template #icon>
                            <NIcon :size="12"><CreateOutline /></NIcon>
                          </template>
                        </NButton>
                        <NButton
                          size="tiny"
                          quaternary
                          circle
                          type="error"
                          @click.stop="handleDeleteSubCategory(sub, category.id)"
                        >
                          <template #icon>
                            <NIcon :size="12"><TrashOutline /></NIcon>
                          </template>
                        </NButton>
                      </div>
                    </div>
                  </template>
                  <div v-if="sub.description || sub.notes">
                    <div v-if="sub.description">{{ sub.description }}</div>
                    <div v-if="sub.notes" class="text-xs text-gray-400 mt-1">{{ sub.notes }}</div>
                  </div>
                  <div v-else>暂无描述</div>
                </NTooltip>
              </div>
              <div
                v-if="subCategoryStore.getSubCategories(category.id).length === 0"
                class="px-2 py-1 text-xs text-gray-400 italic"
              >
                暂无数据
              </div>
            </div>
          </div>
        </div>
      </NSpin>
    </div>

    <CategoryForm
      v-model:visible="showCategoryForm"
      type="category"
      :title="editingCategory ? '编辑大类' : '新增大类'"
      :edit-data="editingCategory ?? undefined"
      @submit="handleCategorySubmit"
    />

    <CategoryForm
      v-model:visible="showSubCategoryForm"
      type="subCategory"
      :title="editingSubCategory ? '编辑子分类' : '新增子分类'"
      :edit-data="editingSubCategory ?? undefined"
      @submit="handleSubCategorySubmit"
    />

    <ItemForm
      v-model:visible="showItemForm"
      @submit="handleItemSubmit"
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

    <NModal
      v-model:show="showSubDeleteConfirm"
      preset="dialog"
      title="确认删除"
      :content="`确定要删除子分类「${subCategoryToDelete?.name}」吗？`"
      positive-text="删除"
      negative-text="取消"
      type="error"
      @positive-click="handleDeleteSubCategoryConfirm"
      @negative-click="showSubDeleteConfirm = false"
    />
  </div>
</template>
