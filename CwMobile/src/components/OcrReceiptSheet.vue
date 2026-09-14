<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { showFailToast, showSuccessToast } from 'vant'
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
const currencyStore = useCurrencyStore()
const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()

const applying = ref(false)
const result = ref<ApplyResult | null>(null)
const subCategoryId = ref<number | null>(null)
const showCategorySheet = ref(false)

const receipt = computed(() => props.response?.receipt ?? null)
const draft = computed(() => props.response?.draft ?? null)

const subOptions = computed(() => {
  const opts: { name: string; value: number }[] = []
  for (const cat of categoryStore.categories) {
    for (const sub of subCategoryStore.getSubCategories(cat.id)) {
      opts.push({ name: `${cat.name} / ${sub.name}`, value: sub.id })
    }
  }
  return opts
})

// 当前选中的分类显示名；没选时回占位符。
const categoryLabel = computed(() => {
  const hit = subOptions.value.find((o) => o.value === subCategoryId.value)
  return hit ? hit.name : t('app.ocr.categoryPlaceholder')
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

function handleSelectCategory(action: { value?: number }) {
  showCategorySheet.value = false
  if (action.value != null) subCategoryId.value = action.value
}

async function handleApply() {
  const d = draft.value
  if (!d) return
  applying.value = true
  try {
    d.sub_category_id = subCategoryId.value
    result.value = await ocrApi.apply(d)
    showSuccessToast(t('app.ocr.applySuccess'))
    emit('applied')
  } catch (e: any) {
    showFailToast(e.message || t('app.ocr.applyFailed'))
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
  <van-popup
    :show="visible"
    position="bottom"
    round
    class="ocr-sheet"
    @update:show="handleClose"
  >
    <div class="ocr">
      <div class="ocr-title">{{ t('app.ocr.reviewTitle') }}</div>

      <!-- 结果视图 -->
      <div v-if="result" class="ocr-body">
        <div class="ocr-meta">
          {{ t('app.ocr.createdItems') }}：{{ result.created_items.length }} ·
          {{ t('app.ocr.updatedSubCategories') }}：{{ result.updated_sub_categories.length }}
        </div>
        <div v-if="result.skipped.length" class="ocr-warn">
          <div class="ocr-warn-title">{{ t('app.ocr.skipped') }}</div>
          <div v-for="s in result.skipped" :key="s">{{ s }}</div>
        </div>
        <div v-if="result.clamped.length" class="ocr-warn">
          <div class="ocr-warn-title">{{ t('app.ocr.clamped') }}</div>
          <div v-for="s in result.clamped" :key="s">{{ s }}</div>
        </div>
        <van-button block type="primary" @click="handleClose">
          {{ t('app.common.close') }}
        </van-button>
      </div>

      <!-- 核对视图 -->
      <div v-else class="ocr-body">
        <div class="ocr-meta">
          {{ t('app.ocr.merchant') }}：{{ receipt?.merchant ?? '-' }} ·
          {{ t('app.ocr.date') }}：{{ receipt?.date ?? '-' }}
        </div>
        <div class="ocr-meta">
          {{ t('app.ocr.total') }}：{{ fmtMoney(receipt?.total) }}
        </div>

        <div v-if="receipt && receipt.low_confidence.length" class="ocr-warn">
          <div class="ocr-warn-title">{{ t('app.ocr.lowConfidence') }}</div>
          <div v-for="l in receipt.low_confidence" :key="l.text">
            {{ l.text }}（{{ (l.confidence * 100).toFixed(0) }}%）
          </div>
        </div>

        <van-cell
          :title="categoryLabel"
          is-link
          @click="showCategorySheet = true"
        />

        <div v-if="draft && draft.items.length" class="ocr-items">
          <div v-for="(item, i) in draft.items" :key="i" class="ocr-item">
            <van-checkbox v-model="item.selected" />
            <div class="ocr-item-main">
              <div class="ocr-item-name">{{ item.name }}</div>
              <div class="ocr-item-meta">
                {{ t('app.ocr.itemQuantity') }} {{ fmt(item.quantity) }} ·
                {{ fmtMoney(item.unit_price) }} · {{ fmtMoney(item.amount) }}
              </div>
            </div>
          </div>
        </div>
        <div v-else class="ocr-empty">{{ t('app.ocr.noItems') }}</div>

        <van-button
          block
          type="primary"
          :loading="applying"
          :loading-text="t('app.ocr.applying')"
          @click="handleApply"
        >
          {{ t('app.ocr.apply') }}
        </van-button>
        <van-button block plain @click="handleClose">{{ t('app.common.cancel') }}</van-button>
      </div>
    </div>

    <van-action-sheet
      v-model:show="showCategorySheet"
      :actions="subOptions"
      :cancel-text="t('app.common.cancel')"
      @select="handleSelectCategory"
    />
  </van-popup>
</template>

<style scoped>
.ocr {
  padding: 16px;
  max-height: 80vh;
  overflow-y: auto;
}

.ocr-title {
  font-weight: 600;
  text-align: center;
  margin-bottom: 12px;
}

.ocr-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ocr-meta {
  font-size: 13px;
  color: var(--van-text-color-2);
}

.ocr-warn {
  padding: 10px 12px;
  font-size: 12px;
  color: #b7791f;
  background: rgba(250, 173, 20, 0.12);
  border-radius: 6px;
}

.ocr-warn-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.ocr-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 40vh;
  overflow-y: auto;
}

.ocr-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
}

.ocr-item-main {
  flex: 1;
  min-width: 0;
}

.ocr-item-name {
  font-size: 14px;
}

.ocr-item-meta {
  font-size: 12px;
  color: var(--van-text-color-3);
}

.ocr-empty {
  text-align: center;
  font-size: 13px;
  color: var(--van-text-color-3);
  padding: 16px 0;
}
</style>
