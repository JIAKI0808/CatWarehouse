<script setup lang="ts">
import { ref, computed } from 'vue'
import { NButton, NDropdown, NIcon, useMessage } from 'naive-ui'
import { ArrowUpOutline } from '@vicons/ionicons5'
import { useI18n } from 'vue-i18n'
import { exportApi } from '@/services/api'
import { useCategoryStore } from '@/stores/category'
import UploadModal from './UploadModal.vue'
import ImportModal from './ImportModal.vue'

const message = useMessage()
const categoryStore = useCategoryStore()
const { t } = useI18n()
const showUploadModal = ref(false)
const showImportModal = ref(false)

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

    <ImportModal v-model:visible="showImportModal" @imported="handleImported" />
  </div>
</template>
