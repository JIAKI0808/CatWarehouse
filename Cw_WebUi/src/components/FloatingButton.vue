<script setup lang="ts">
import { ref } from 'vue'
import { NButton, NDropdown } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import UploadModal from './UploadModal.vue'

const showUploadModal = ref(false)

const addOptions = [
  { label: '上传单据', key: 'upload' },
]

function handleAdd(key: string) {
  if (key === 'upload') {
    showUploadModal.value = true
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
        <AddOutline :size="24" />
      </NButton>
    </NDropdown>

    <UploadModal
      v-model:visible="showUploadModal"
      @upload="handleUpload"
    />
  </div>
</template>
