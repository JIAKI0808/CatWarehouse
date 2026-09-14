<script setup lang="ts">
import { ref, computed } from 'vue'
import { NButton, NDropdown, NIcon, useMessage } from 'naive-ui'
import { ArrowUpOutline } from '@vicons/ionicons5'
import { useI18n } from 'vue-i18n'
import { exportApi, ocrApi } from '@/services/api'
import { useCategoryStore } from '@/stores/category'
import UploadModal from './UploadModal.vue'
import ImportModal from './ImportModal.vue'
import OcrReceiptModal from './OcrReceiptModal.vue'
import type { ReceiptRecognizeResponse } from '@/types'

const message = useMessage()
const categoryStore = useCategoryStore()
const { t } = useI18n()
const showUploadModal = ref(false)
const showImportModal = ref(false)
const showOcrModal = ref(false)
const ocrResponse = ref<ReceiptRecognizeResponse | null>(null)

// computed：菜单项文案要随语言切换重算（模板里 :options 会自动解包）。
const addOptions = computed(() => [
  { label: t('app.inventory.uploadReceipt'), key: 'upload' },
  { label: t('app.inventory.exportData'), key: 'export' },
  { label: t('app.inventory.importData'), key: 'import' },
])

function handleAdd(key: string) {
  if (key === 'upload') {
    showUploadModal.value = true
  } else if (key === 'export') {
    handleExport()
  } else if (key === 'import') {
    showImportModal.value = true
  }
}

async function handleExport() {
  try {
    const data = await exportApi.getData()
    const json = JSON.stringify(data, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `catwarehouse-export-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    message.success(t('app.inventory.exportSuccess'))
  } catch (e: any) {
    message.error(e.message || t('app.inventory.exportFailed'))
  }
}

function handleImported() {
  categoryStore.fetchAll()
}

/**
 * 选中图片 → 调真实 OCR 接口识别 → 打开「核对 + 入库」弹层。
 *
 * 原先这里是 `fetch('/api/image-analysis')` —— **该路径不存在**，且结果只 console.log，
 * 用户什么都看不到。现在接上真实的 `/api/ocr/receipt`，识别结果交给
 * `OcrReceiptModal` 核对后再经 `/api/ocr/receipt/apply` 落库。
 */
async function handleUpload(file: File) {
  try {
    ocrResponse.value = await ocrApi.recognize(file)
    showOcrModal.value = true
  } catch (e: any) {
    message.error(e.message || t('app.ocr.recognizeFailed'))
  }
}

function handleOcrApplied() {
  // 入库后刷新分类（数量变了），保持界面与库一致
  categoryStore.fetchAll()
}
</script>

<template>
  <div class="fixed bottom-6 right-6 z-50">
    <NDropdown :options="addOptions" @select="handleAdd">
      <NButton type="primary" circle size="large">
        <template #icon>
          <NIcon :size="24"><ArrowUpOutline /></NIcon>
        </template>
      </NButton>
    </NDropdown>

    <UploadModal v-model:visible="showUploadModal" @upload="handleUpload" />

    <OcrReceiptModal
      v-model:visible="showOcrModal"
      :response="ocrResponse"
      @applied="handleOcrApplied"
    />

    <ImportModal v-model:visible="showImportModal" @imported="handleImported" />
  </div>
</template>
