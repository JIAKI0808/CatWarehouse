<script setup lang="ts">
import { ref } from 'vue'
import { NModal, NCard, NButton, NSpace, NUpload, NUploadDragger, NText, NIcon } from 'naive-ui'
import { ImageOutline } from '@vicons/ionicons5'
import { useI18n } from 'vue-i18n'
import type { UploadFileInfo } from 'naive-ui'

const { t } = useI18n()

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
      :title="t('app.inventory.uploadReceipt')"
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
            {{ t('app.intake.uploadDropHint') }}
          </NText>
        </NUploadDragger>
      </NUpload>

      <template #footer>
        <NSpace justify="end">
          <NButton @click="handleClose">{{ t('app.common.cancel') }}</NButton>
          <NButton type="primary" :disabled="fileList.length === 0" @click="handleUpload">
            {{ t('app.intake.upload') }}
          </NButton>
        </NSpace>
      </template>
    </NCard>
  </NModal>
</template>
