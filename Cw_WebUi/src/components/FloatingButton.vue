<script setup lang="ts">
import { ref } from 'vue'
import { NButton, NDropdown, NIcon, useMessage } from 'naive-ui'
import { ArrowUpOutline } from '@vicons/ionicons5'
import { exportApi } from '@/services/api'
import UploadModal from './UploadModal.vue'
import ImportModal from './ImportModal.vue'

const message = useMessage()
const showUploadModal = ref(false)
const showImportModal = ref(false)

const addOptions = [
  { label: '上传单据', key: 'upload' },
  { label: '导出数据', key: 'export' },
  { label: '导入数据', key: 'import' },
]

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
    message.success('导出成功')
  } catch (e: any) {
    message.error(e.message || '导出失败')
  }
}

async function handleUpload(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  try {
    const response = await fetch('/api/image-analysis', {
      method: 'POST',
      body: formData,
    })
    if (response.ok) {
      const result = await response.json()
      console.log('上传成功:', result)
    }
  } catch (error) {
    console.error('上传失败:', error)
  }
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

    <UploadModal
      v-model:visible="showUploadModal"
      @upload="handleUpload"
    />

    <ImportModal v-model:visible="showImportModal" />
  </div>
</template>
