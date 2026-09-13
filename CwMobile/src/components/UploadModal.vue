<script setup lang="ts">
import { ref } from 'vue'
import { showToast, showSuccessToast, type UploaderFileListItem } from 'vant'
import { uploadApi } from '@/services/api'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: 'update:visible', value: boolean): void }>()

const fileList = ref<UploaderFileListItem[]>([])
const uploading = ref(false)

async function handleRead(
  files: UploaderFileListItem | UploaderFileListItem[]
) {
  const item = Array.isArray(files) ? files[0] : files
  const file = item?.file
  if (!file) return
  uploading.value = true
  try {
    await uploadApi.upload(file)
    showSuccessToast('上传成功')
    emit('update:visible', false)
    fileList.value = []
  } catch (e: any) {
    showToast(e.message || '上传失败')
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
      <div class="upload-title">上传单据</div>
      <div class="upload-body">
        <van-uploader
          v-model="fileList"
          :max-count="1"
          accept="image/*"
          :after-read="handleRead"
        >
          <div class="upload-tip">
            <van-icon name="photograph" size="36" color="var(--van-text-color-3)" />
            <div>点击选择图片上传</div>
          </div>
        </van-uploader>
        <div v-if="uploading" class="uploading">上传中…</div>
      </div>
      <van-button block plain @click="close">取消</van-button>
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
