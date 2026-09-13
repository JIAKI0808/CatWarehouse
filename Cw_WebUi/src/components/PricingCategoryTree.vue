<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { NSpin, NButton, NIcon, NModal, NInput, NTooltip } from 'naive-ui'
import { AddOutline, TrashOutline, CreateOutline, FolderOutline, DocumentOutline } from '@vicons/ionicons5'
import { useI18n } from 'vue-i18n'
import { pricingCategoryApi, pricingSubCategoryApi } from '@/services/api'
import type { PricingCategory, PricingSubCategory } from '@/types'

const { t } = useI18n()

const categories = ref<PricingCategory[]>([])
const subCategoriesByCategory = ref<Record<number, PricingSubCategory[]>>({})
const selectedCategoryId = ref<number | null>(null)
const selectedSubCategoryId = ref<number | null>(null)
const loading = ref(false)

const showCategoryForm = ref(false)
const showSubCategoryForm = ref(false)
const editingCategory = ref<PricingCategory | null>(null)
const editingSubCategory = ref<PricingSubCategory | null>(null)
const categoryFormName = ref('')
const subCategoryFormName = ref('')

const emit = defineEmits<{
  (e: 'select-category', id: number | null): void
  (e: 'select-sub-category', id: number | null): void
}>()

onMounted(async () => {
  await fetchCategories()
})

async function fetchCategories() {
  loading.value = true
  try {
    categories.value = await pricingCategoryApi.getAll()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchSubCategories(categoryId: number) {
  try {
    const subs = await pricingSubCategoryApi.getAll(categoryId)
    subCategoriesByCategory.value[categoryId] = subs
  } catch (e) {
    console.error(e)
  }
}

function handleAddCategory() {
  editingCategory.value = null
  categoryFormName.value = ''
  showCategoryForm.value = true
}

function handleEditCategory(cat: PricingCategory) {
  editingCategory.value = cat
  categoryFormName.value = cat.name
  showCategoryForm.value = true
}

async function handleDeleteCategory(catId: number) {
  await pricingCategoryApi.delete(catId)
  categories.value = categories.value.filter(c => c.id !== catId)
  if (selectedCategoryId.value === catId) {
    selectedCategoryId.value = null
    selectedSubCategoryId.value = null
    emit('select-category', null)
    emit('select-sub-category', null)
  }
}

async function handleCategorySubmit() {
  if (editingCategory.value) {
    await pricingCategoryApi.update(editingCategory.value.id, { name: categoryFormName.value })
  } else {
    await pricingCategoryApi.create({ name: categoryFormName.value })
  }
  showCategoryForm.value = false
  await fetchCategories()
}

function handleAddSubCategory(categoryId: number) {
  selectedCategoryId.value = categoryId
  editingSubCategory.value = null
  subCategoryFormName.value = ''
  showSubCategoryForm.value = true
}

function handleEditSubCategory(sub: PricingSubCategory) {
  editingSubCategory.value = sub
  subCategoryFormName.value = sub.name
  showSubCategoryForm.value = true
}

async function handleDeleteSubCategory(subId: number, categoryId: number) {
  await pricingSubCategoryApi.delete(subId)
  if (subCategoriesByCategory.value[categoryId]) {
    subCategoriesByCategory.value[categoryId] = subCategoriesByCategory.value[categoryId].filter(s => s.id !== subId)
  }
  if (selectedSubCategoryId.value === subId) {
    selectedSubCategoryId.value = null
    emit('select-sub-category', null)
  }
}

async function handleSubCategorySubmit() {
  if (editingSubCategory.value) {
    await pricingSubCategoryApi.update(editingSubCategory.value.id, { name: subCategoryFormName.value })
  } else if (selectedCategoryId.value) {
    await pricingSubCategoryApi.create({ category_id: selectedCategoryId.value, name: subCategoryFormName.value })
    await fetchSubCategories(selectedCategoryId.value)
  }
  showSubCategoryForm.value = false
}

function toggleCategory(catId: number) {
  selectedCategoryId.value = catId
  selectedSubCategoryId.value = null
  emit('select-category', catId)
  emit('select-sub-category', null)
  if (!subCategoriesByCategory.value[catId]) {
    fetchSubCategories(catId)
  }
}

function selectSubCategory(subId: number) {
  selectedSubCategoryId.value = subId
  emit('select-sub-category', subId)
}
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="p-3 border-b flex items-center justify-between">
      <h3 class="text-sm font-semibold text-gray-600">{{ t('app.pricing.categoryTitle') }}</h3>
      <NButton size="tiny" type="primary" @click="handleAddCategory">
        <template #icon><NIcon :size="14"><AddOutline /></NIcon></template>
      </NButton>
    </div>
    <div class="flex-1 overflow-auto p-2">
      <NSpin :show="loading">
        <div class="space-y-0.5">
          <div v-for="cat in categories" :key="cat.id">
            <NTooltip trigger="hover" placement="right">
              <template #trigger>
                <div
                  class="group flex items-center gap-1 px-2 py-1.5 rounded cursor-pointer hover:bg-gray-100"
                  @click="toggleCategory(cat.id)"
                >
                  <NIcon :size="16" class="text-amber-500 flex-shrink-0" :component="FolderOutline" />
                  <span class="text-sm font-medium truncate flex-1">{{ cat.name }}</span>
                  <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <NButton size="tiny" quaternary circle @click.stop="handleAddSubCategory(cat.id)">
                      <template #icon><NIcon :size="12"><AddOutline /></NIcon></template>
                    </NButton>
                    <NButton size="tiny" quaternary circle @click.stop="handleEditCategory(cat)">
                      <template #icon><NIcon :size="12"><CreateOutline /></NIcon></template>
                    </NButton>
                    <NButton size="tiny" quaternary circle type="error" @click.stop="handleDeleteCategory(cat.id)">
                      <template #icon><NIcon :size="12"><TrashOutline /></NIcon></template>
                    </NButton>
                  </div>
                </div>
              </template>
              {{ cat.description || t('app.common.noDescription') }}
            </NTooltip>

            <div v-if="subCategoriesByCategory[cat.id]?.length" class="ml-5 border-l-2 border-gray-200">
              <div v-for="sub in subCategoriesByCategory[cat.id]" :key="sub.id">
                <NTooltip trigger="hover" placement="right">
                  <template #trigger>
                    <div
                      class="group/sub flex items-center gap-2 px-2 py-1 cursor-pointer rounded text-sm"
                      :class="selectedSubCategoryId === sub.id ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'"
                      @click.stop="selectSubCategory(sub.id)"
                    >
                      <NIcon :size="14" class="flex-shrink-0"><DocumentOutline /></NIcon>
                      <span class="truncate flex-1">{{ sub.name }}</span>
                      <div class="flex gap-0.5 opacity-0 group-hover/sub:opacity-100 transition-opacity">
                        <NButton size="tiny" quaternary circle @click.stop="handleEditSubCategory(sub)">
                          <template #icon><NIcon :size="12"><CreateOutline /></NIcon></template>
                        </NButton>
                        <NButton size="tiny" quaternary circle type="error" @click.stop="handleDeleteSubCategory(sub.id, cat.id)">
                          <template #icon><NIcon :size="12"><TrashOutline /></NIcon></template>
                        </NButton>
                      </div>
                    </div>
                  </template>
                  {{ sub.description || t('app.common.noDescription') }}
                </NTooltip>
              </div>
            </div>
          </div>
        </div>
      </NSpin>
    </div>

    <NModal v-model:show="showCategoryForm">
      <div class="bg-white rounded-lg p-4 w-80">
        <h3 class="text-lg font-bold mb-4">
          {{ editingCategory ? t('app.pricing.editCategory') : t('app.pricing.addCategory') }}
        </h3>
        <NInput v-model:value="categoryFormName" :placeholder="t('app.pricing.categoryNamePlaceholder')" />
        <div class="flex justify-end gap-2 mt-4">
          <NButton @click="showCategoryForm = false">{{ t('app.common.cancel') }}</NButton>
          <NButton type="primary" @click="handleCategorySubmit">{{ t('app.common.save') }}</NButton>
        </div>
      </div>
    </NModal>

    <NModal v-model:show="showSubCategoryForm">
      <div class="bg-white rounded-lg p-4 w-80">
        <h3 class="text-lg font-bold mb-4">
          {{ editingSubCategory ? t('app.pricing.editSubCategory') : t('app.pricing.addSubCategory') }}
        </h3>
        <NInput v-model:value="subCategoryFormName" :placeholder="t('app.pricing.subCategoryNamePlaceholder')" />
        <div class="flex justify-end gap-2 mt-4">
          <NButton @click="showSubCategoryForm = false">{{ t('app.common.cancel') }}</NButton>
          <NButton type="primary" @click="handleSubCategorySubmit">{{ t('app.common.save') }}</NButton>
        </div>
      </div>
    </NModal>
  </div>
</template>
