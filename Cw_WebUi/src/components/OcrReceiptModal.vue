<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  NAlert, NButton, NCard, NCheckbox, NDescriptions, NDescriptionsItem,
  NEmpty, NModal, NSelect, NSpace, NSpin, useMessage,
} from 'naive-ui'
import { useI18n } from 'vue-i18n'
import { useCategoryStore } from '@/stores/category'
import { useCurrencyStore } from '@/stores/currency'
import { useSubCategoryStore } from '@/stores/subCategory'
import { ocrApi } from '@/services/api'
import type { ApplyResult, ReceiptRecognizeResponse } from '@/types'

const props = defineProps<{
  visible: boolean
  response: ReceiptRecognizeResponse | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'applied'): void
}>()

const { t } = useI18n()
const message = useMessage()
const currencyStore = useCurrencyStore()
const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()

const applying = ref(false)
const result = ref<ApplyResult | null>(null)
const subCategoryId = ref<number | null>(null)

const receipt = computed(() => props.response?.receipt ?? null)
const draft = computed(() => props.response?.draft ?? null)

// 分类下拉：大类名 / 子分类名 → 子分类 id。选项来自既有的两个 store。
const subOptions = computed(() => {
  const opts: { label: string; value: number }[] = []
  for (const cat of categoryStore.categories) {
    for (const sub of subCategoryStore.getSubCategories(cat.id)) {
      opts.push({ label: `${cat.name} / ${sub.name}`, value: sub.id })
    }
  }
  return opts
})

onMounted(loadCategories)
watch(() => props.visible, (v) => { if (v) loadCategories() })

async function loadCategories() {
  if (categoryStore.categories.length === 0) {
    await categoryStore.fetchAll()
  }
  for (const cat of categoryStore.categories) {
    if (subCategoryStore.getSubCategories(cat.id).length === 0) {
      await subCategoryStore.fetchByCategory(cat.id)
    }
  }
}

function fmt(n: number | null | undefined): string {
  return n == null ? '-' : String(n)
}

function fmtMoney(n: number | null | undefined): string {
  return n == null ? '-' : `${currencyStore.symbol}${n.toFixed(2)}`
}

async function handleApply() {
  const d = draft.value
  if (!d) return
  applying.value = true
  try {
    d.sub_category_id = subCategoryId.value
    result.value = await ocrApi.apply(d)
    message.success(t('app.ocr.applySuccess'))
    emit('applied')
  } catch (e: any) {
    message.error(e.message || t('app.ocr.applyFailed'))
  } finally {
    applying.value = false
  }
}

function handleClose() {
  emit('update:visible', false)
  result.value = null
  subCategoryId.value = null
}
</script>

<template>
  <NModal :show="visible" @update:show="handleClose">
    <NCard :title="t('app.ocr.reviewTitle')" style="width: 640px" :bordered="false" role="dialog">

      <!-- 结果视图 -->
      <div v-if="result">
        <NAlert type="success" :bordered="false" class="mb-3">
          {{ t('app.ocr.applySuccess') }}
        </NAlert>
        <NDescriptions :column="2" size="small" class="mb-3">
          <NDescriptionsItem :label="t('app.ocr.createdItems')">
            {{ result.created_items.length }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('app.ocr.updatedSubCategories')">
            {{ result.updated_sub_categories.length }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('app.ocr.createdLedger')">
            {{ result.created_ledger_id ?? '-' }}
          </NDescriptionsItem>
        </NDescriptions>
        <NAlert v-if="result.skipped.length" type="warning" :bordered="false" class="mb-2">
          <template #header>{{ t('app.ocr.skipped') }}</template>
          <div v-for="s in result.skipped" :key="s">{{ s }}</div>
        </NAlert>
        <NAlert v-if="result.clamped.length" type="error" :bordered="false" class="mb-2">
          <template #header>{{ t('app.ocr.clamped') }}</template>
          <div v-for="s in result.clamped" :key="s">{{ s }}</div>
        </NAlert>
      </div>

      <!-- 核对视图 -->
      <div v-else>
        <NDescriptions :column="2" size="small" class="mb-3">
          <NDescriptionsItem :label="t('app.ocr.merchant')">
            {{ receipt?.merchant ?? '-' }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('app.ocr.date')">
            {{ receipt?.date ?? '-' }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('app.ocr.orderNo')">
            {{ receipt?.order_no ?? '-' }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('app.ocr.docType')">
            {{ receipt?.doc_type ?? '-' }}
          </NDescriptionsItem>
          <NDescriptionsItem :label="t('app.ocr.total')">
            {{ fmtMoney(receipt?.total) }}
          </NDescriptionsItem>
        </NDescriptions>

        <NAlert
          v-if="receipt && receipt.low_confidence.length"
          type="warning"
          :bordered="false"
          class="mb-3"
        >
          <template #header>{{ t('app.ocr.lowConfidence') }}</template>
          <div v-for="l in receipt.low_confidence" :key="l.text">
            {{ l.text }}（{{ (l.confidence * 100).toFixed(0) }}%）
          </div>
        </NAlert>

        <NSelect
          v-model:value="subCategoryId"
          :options="subOptions"
          :placeholder="t('app.ocr.categoryPlaceholder')"
          clearable
          class="mb-3"
        />

        <NEmpty v-if="!draft || draft.items.length === 0" :description="t('app.ocr.noItems')" />
        <div v-else class="space-y-1 max-h-64 overflow-y-auto">
          <div
            v-for="(item, i) in draft.items"
            :key="i"
            class="flex items-center gap-3 py-1"
          >
            <NCheckbox v-model:checked="item.selected" />
            <span class="flex-1 truncate">{{ item.name }}</span>
            <span class="w-14 text-right text-xs">{{ t('app.ocr.itemQuantity') }} {{ fmt(item.quantity) }}</span>
            <span class="w-24 text-right text-xs">{{ fmtMoney(item.unit_price) }}</span>
            <span class="w-24 text-right text-xs">{{ fmtMoney(item.amount) }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <NSpace justify="end">
          <template v-if="result">
            <NButton type="primary" @click="handleClose">{{ t('app.common.close') }}</NButton>
          </template>
          <template v-else>
            <NButton @click="handleClose">{{ t('app.common.cancel') }}</NButton>
            <NButton type="primary" :loading="applying" @click="handleApply">
              {{ applying ? t('app.ocr.applying') : t('app.ocr.apply') }}
            </NButton>
          </template>
        </NSpace>
      </template>
    </NCard>
  </NModal>
</template>
