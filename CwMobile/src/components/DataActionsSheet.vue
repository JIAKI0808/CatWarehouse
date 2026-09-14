<script setup lang="ts">
import { ref, computed } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { useI18n } from 'vue-i18n'
import { exportApi } from '@/services/api'
import type { ReceiptRecognizeResponse } from '@/types'
import UploadModal from './UploadModal.vue'
import ImportModal from './ImportModal.vue'
import OcrReceiptSheet from './OcrReceiptSheet.vue'

const { t } = useI18n()

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'changed'): void
}>()

const showUpload = ref(false)
const showImport = ref(false)
const showOcr = ref(false)
const ocrResponse = ref<ReceiptRecognizeResponse | null>(null)

// computed：`:actions` 要随语言切换重算。
const actions = computed(() => [
  { name: t('app.intake.uploadReceipt'), key: 'upload' },
  { name: t('app.intake.exportData'), key: 'export' },
  { name: t('app.intake.importData'), key: 'import' },
])

function onAction(action: { key: string }) {
  emit('update:visible', false)
  if (action.key === 'upload') {
    showUpload.value = true
  } else if (action.key === 'export') {
    handleExport()
  } else if (action.key === 'import') {
    showImport.value = true
  }
}

async function handleExport() {
  try {
    const data = await exportApi.getData()
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `catwarehouse-export-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    showSuccessToast(t('app.intake.exportSuccess'))
  } catch (e: any) {
    showToast(e.message || t('app.intake.exportFailed'))
  }
}

function onImported() {
  emit('changed')
}

/** 识别结果到了 → 打开核对弹层。 */
function onRecognized(response: ReceiptRecognizeResponse) {
  ocrResponse.value = response
  showOcr.value = true
}

/** 入库完成 → 通知上层刷新（数量变了）。 */
function onOcrApplied() {
  emit('changed')
}
</script>

<template>
  <van-action-sheet
    :show="visible"
    :actions="actions"
    :cancel-text="t('app.common.cancel')"
    :description="t('app.intake.dataTools')"
    @update:show="emit('update:visible', $event)"
    @select="onAction"
  />

  <UploadModal v-model:visible="showUpload" @recognized="onRecognized" />
  <OcrReceiptSheet
    v-model:visible="showOcr"
    :response="ocrResponse"
    @applied="onOcrApplied"
  />
  <ImportModal v-model:visible="showImport" @imported="onImported" />
</template>
