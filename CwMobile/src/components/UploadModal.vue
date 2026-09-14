<script setup lang="ts">
import { ref } from 'vue'
import { showToast, type UploaderFileListItem } from 'vant'
import { useI18n } from 'vue-i18n'
import { ocrApi } from '@/services/api'
import type { ReceiptRecognizeResponse } from '@/types'

const { t } = useI18n()

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'recognized', response: ReceiptRecognizeResponse): void
}>()

const fileList = ref<UploaderFileListItem[]>([])
const uploading = ref(false)

/**
 * 选中图片 → 调真实 OCR 接口识别 → 把结果交给上层打开「核对 + 入库」弹层。
 * 原先这里只是 `uploadApi.upload`（存盘，不识别），改成识别后，
 * 识别结果经 `recognized` 事件上抛，由 `DataActionsSheet` 打开 `OcrReceiptSheet`。
 */
async function handleRead(
  files: UploaderFileListItem | UploaderFileListItem[]
) {
  const item = Array.isArray(files) ? files[0] : files
  const file = item?.file
  if (!file) return
  uploading.value = true
  try {
    const response = await ocrApi.recognize(file)
    emit('recognized', response)
    emit('update:visible', false)
    fileList.value = []
  } catch (e: any) {
    showToast(e.message || t('app.ocr.recognizeFailed'))
  } finally {
    uploading.value = false
  }
}

function close() {
  emit('update:visible', false)
  fileList.value = []
}
</script>

<template>
  <van-popup
    :show="visible"
    position="bottom"
    round
    @update:show="emit('update:visible', $event)"
  >
    <div class="upload">
      <div class="upload-title">{{ t('app.intake.uploadReceipt') }}</div>
      <div class="upload-body">
        <van-uploader
          v-model="fileList"
          :max-count="1"
          accept="image/*"
          :after-read="handleRead"
        >
          <div class="upload-tip">
            <van-icon name="photograph" size="36" color="var(--van-text-color-3)" />
            <div>{{ t('app.intake.chooseImage') }}</div>
          </div>
        </van-uploader>
        <div v-if="uploading" class="uploading">{{ t('app.intake.uploading') }}</div>
      </div>
      <van-button block plain @click="close">{{ t('app.common.cancel') }}</van-button>
      <div class="pad" />
    </div>
  </van-popup>
</template>

<style scoped>
.upload {
  padding: 0 16px;
}

.upload-title {
  padding: 16px 0;
  text-align: center;
  font-weight: 600;
}

.upload-body {
  display: flex;
  justify-content: center;
  padding-bottom: 16px;
}

.upload-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 180px;
  height: 120px;
  gap: 8px;
  color: var(--van-text-color-2);
  font-size: 13px;
  border: 1px dashed var(--van-text-color-3);
  border-radius: 8px;
}

.uploading {
  color: var(--van-text-color-2);
  text-align: center;
  font-size: 13px;
}

.pad {
  height: 16px;
}
</style>
