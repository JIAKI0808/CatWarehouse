<script setup lang="ts">
import { ref, watch } from 'vue'
import { showConfirmDialog } from 'vant'
import { useCategoryStore } from '@/stores/category'
import { useSubCategoryStore } from '@/stores/subCategory'
import { getCategoryIcon } from '@/utils/categoryIcons'
import CategoryForm from './CategoryForm.vue'
import type { Category, SubCategory } from '@/types'

interface CatEdit {
  id: number
  name: string
  description: string
  icon: string
  icon_color: string
}

interface SubEdit {
  id: number
  categoryId: number
  name: string
  description: string
  unit: string
  notes: string
}

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'select', sub: SubCategory): void
}>()

const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()

const activeCats = ref<number[]>([])
const loadedCats = ref<Set<number>>(new Set())
const showCatForm = ref(false)
const catFormType = ref<'category' | 'subCategory'>('category')
const catFormTitle = ref('')
const editingCategory = ref<CatEdit | null>(null)
const editingSubCategory = ref<SubEdit | null>(null)
const contextCategoryId = ref<number | null>(null)

watch(
  () => props.visible,
  (val) => {
    if (val) {
      activeCats.value = []
      loadedCats.value = new Set()
      categoryStore.fetchAll()
    }
  }
)

watch(activeCats, (ids) => {
  ids.forEach((id) => {
    if (!loadedCats.value.has(id)) {
      loadedCats.value.add(id)
      subCategoryStore.fetchByCategory(id)
    }
  })
})

function close() {
  emit('update:visible', false)
}

function onSelect(sub: SubCategory) {
  emit('select', sub)
  close()
}

function openAddCategory() {
  editingCategory.value = null
  catFormType.value = 'category'
  catFormTitle.value = '新增大类'
  showCatForm.value = true
}

function openEditCategory(cat: Category) {
  editingCategory.value = {
    id: cat.id,
    name: cat.name,
    description: cat.description,
    icon: cat.icon ?? 'FolderOutline',
    icon_color: cat.icon_color ?? '#f59e0b',
  }
  catFormType.value = 'category'
  catFormTitle.value = '编辑大类'
  showCatForm.value = true
}

function openAddSub(catId: number) {
  contextCategoryId.value = catId
  editingSubCategory.value = null
  catFormType.value = 'subCategory'
  catFormTitle.value = '新增子分类'
  showCatForm.value = true
}

function openEditSub(sub: SubCategory) {
  contextCategoryId.value = sub.category_id
  editingSubCategory.value = {
    id: sub.id,
    categoryId: sub.category_id,
    name: sub.name,
    description: sub.description,
    unit: sub.unit,
    notes: sub.notes,
  }
  catFormType.value = 'subCategory'
  catFormTitle.value = '编辑子分类'
  showCatForm.value = true
}

async function submitCategory(data: Record<string, string>) {
  const name = data.name ?? ''
  const description = data.description ?? ''
  const icon = data.icon ?? 'FolderOutline'
  const icon_color = data.icon_color ?? '#f59e0b'
  if (editingCategory.value) {
    await categoryStore.update(editingCategory.value.id, {
      name,
      description,
      icon,
      icon_color,
    })
    editingCategory.value = null
  } else {
    await categoryStore.create(name, description, icon, icon_color)
  }
}

async function submitSub(data: Record<string, string>) {
  const name = data.name ?? ''
  const unit = data.unit ?? '个'
  const description = data.description ?? ''
  const notes = data.notes ?? ''
  if (editingSubCategory.value) {
    const s = editingSubCategory.value
    await subCategoryStore.update(s.id, {
      name,
      unit,
      description,
      notes,
    })
    editingSubCategory.value = null
  } else if (contextCategoryId.value) {
    await subCategoryStore.create(
      contextCategoryId.value,
      name,
      unit,
      description,
      notes
    )
    subCategoryStore.fetchByCategory(contextCategoryId.value)
  }
}

function askDeleteCategory(cat: Category) {
  showConfirmDialog({
    title: '删除大类',
    message: `确定要删除大类「${cat.name}」吗？`,
    confirmButtonText: '删除',
    confirmButtonColor: '#ee0a24',
  }).then(() => categoryStore.remove(cat.id)).catch(() => undefined)
}

function askDeleteSub(sub: SubCategory) {
  showConfirmDialog({
    title: '删除子分类',
    message: `确定要删除子分类「${sub.name}」吗？`,
    confirmButtonText: '删除',
    confirmButtonColor: '#ee0a24',
  }).then(() => subCategoryStore.remove(sub.category_id, sub.id)).catch(() => undefined)
}
</script>

<template>
  <van-popup
    :show="visible"
    position="left"
    :style="{ width: '86%', height: '100%' }"
    @update:show="emit('update:visible', $event)"
  >
    <div class="mgr">
      <van-nav-bar title="分类管理" left-arrow @click-left="close">
        <template #right>
          <van-icon name="plus" class="nav-plus" @click="openAddCategory" />
        </template>
      </van-nav-bar>

      <div class="mgr-body">
        <van-empty
          v-if="!categoryStore.categories.length && !categoryStore.loading"
          description="暂无分类，点击右上角新增"
        />
        <van-collapse v-else v-model="activeCats">
          <van-collapse-item
            v-for="cat in categoryStore.categories"
            :key="cat.id"
            :name="cat.id"
          >
            <template #title>
              <span class="cat-name">
                <component
                  :is="getCategoryIcon(cat.icon)"
                  :style="{
                    color: cat.icon_color || '#f59e0b',
                    fontSize: '16px',
                  }"
                />
                {{ cat.name }}
              </span>
            </template>
            <template #value>
              <span class="cat-actions" @click.stop>
                <van-icon name="plus" @click.stop="openAddSub(cat.id)" />
                <van-icon name="edit" @click.stop="openEditCategory(cat)" />
                <van-icon name="delete-o" @click.stop="askDeleteCategory(cat)" />
              </span>
            </template>

            <div class="sub-list">
              <van-empty
                v-if="!subCategoryStore.getSubCategories(cat.id).length"
                description="暂无子分类"
              />
              <div
                v-for="sub in subCategoryStore.getSubCategories(cat.id)"
                :key="sub.id"
                class="sub-row"
                :class="{ active: subCategoryStore.selectedId === sub.id }"
                @click="onSelect(sub)"
              >
                <span class="sub-name">{{ sub.name }}</span>
                <span v-if="sub.quantity" class="sub-count">{{ sub.quantity }}</span>
                <span class="sub-actions" @click.stop>
                  <van-icon name="edit" @click.stop="openEditSub(sub)" />
                  <van-icon name="delete-o" @click.stop="askDeleteSub(sub)" />
                </span>
              </div>
            </div>
          </van-collapse-item>
        </van-collapse>
      </div>
    </div>
  </van-popup>

  <CategoryForm
    v-model:visible="showCatForm"
    :type="catFormType"
    :title="catFormTitle"
    :edit-data="
      catFormType === 'category'
        ? (editingCategory ?? undefined)
        : (editingSubCategory ?? undefined)
    "
    @submit="catFormType === 'category' ? submitCategory : submitSub"
  />
</template>

<style scoped>
.mgr {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.nav-plus {
  font-size: 20px;
}

.mgr-body {
  flex: 1;
  overflow-y: auto;
}

.cat-name {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.cat-actions {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  color: var(--van-text-color-2);
}

.sub-list {
  padding-left: 8px;
  background: var(--van-background);
}

.sub-row {
  display: flex;
  align-items: center;
  padding: 10px 8px;
  border-bottom: 1px solid var(--van-border-color);
  cursor: pointer;
}

.sub-row.active {
  color: #1989fa;
  background: #ecf5ff;
}

html.dark .sub-row.active {
  color: #1989fa;
  background: rgba(25, 137, 250, 0.15);
}

.sub-name {
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.sub-count {
  color: var(--van-text-color-2);
  font-size: 12px;
  margin-right: 10px;
}

.sub-actions {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  color: var(--van-text-color-2);
}
</style>
