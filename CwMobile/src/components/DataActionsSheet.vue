<script setup lang="ts">
import { ref } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { exportApi } from '@/services/api'
import UploadModal from './UploadModal.vue'
import ImportModal from './ImportModal.vue'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'changed'): void
}>()

const showUpload = ref(false)
const showImport = ref(false)

const actions = [
  { name: '上传单据', key: 'upload' },
  { name: '导出数据', key: 'export' },
  { name: '导入数据', key: 'import' },
]

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
    showSuccessToast('导出成功')
  } catch (e: any) {
    showToast(e.message || '导出失败')
  }
}

function onImported() {
  emit('changed')
}
</script>

<template>
  <van-action-sheet
    :show="visible"
    :actions="actions"
    cancel-text="取消"
    description="库存数据工具"
    @update:show="emit('update:visible', $event)"
    @select="onAction"
  />

  <UploadModal v-model:visible="showUpload" />
  <ImportModal v-model:visible="showImport" @imported="onImported" />
</template>
