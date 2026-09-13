<script setup lang="ts">
import { ref } from 'vue'
import { NModal, NCard, NButton, NSpace, NUpload, NUploadDragger, NText, NIcon } from 'naive-ui'
import { ImageOutline } from '@vicons/ionicons5'
import type { UploadFileInfo } from 'naive-ui'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'upload', file: File): void
}>()

const fileList = ref<UploadFileInfo[]>([])

function handleClose() {
  emit('update:visible', false)
  fileList.value = []
}

function handleUploadChange({ fileList: newFileList }: { fileList: UploadFileInfo[] }) {
  fileList.value = newFileList
}

function handleUpload() {
  if (fileList.value.length > 0) {
    const file = fileList.value[0].file
    if (file) {
      emit('upload', file)
      handleClose()
    }
  }
}
</script>

<template>
  <NModal :show="visible" @update:show="handleClose">
    <NCard
      title="上传单据"
      style="width: 500px"
      :bordered="false"
      size="huge"
      role="dialog"
      aria-modal="true"
    >
      <NUpload
        v-model:file-list="fileList"
        :max="1"
        accept="image/*"
        @update:file-list="handleUploadChange"
      >
        <NUploadDragger>
          <div style="margin-bottom: 12px">
            <NIcon size="48" :depth="3">
              <ImageOutline />
            </NIcon>
          </div>
          <NText depth="3" style="font-size: 16px">
            点击或者拖动图片到此区域上传
          </NText>
        </NUploadDragger>
      </NUpload>

      <template #footer>
        <NSpace justify="end">
          <NButton @click="handleClose">取消</NButton>
          <NButton type="primary" :disabled="fileList.length === 0" @click="handleUpload">
            上传
          </NButton>
        </NSpace>
      </template>
    </NCard>
  </NModal>
</template>
