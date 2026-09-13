<script setup lang="ts">
import { ref } from 'vue'
import { showToast, type UploaderFileListItem } from 'vant'
import { importApi, type ExportData, type ConflictItem, type ImportResult } from '@/services/api'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'imported'): void
}>()

type Step = 'upload' | 'conflicts' | 'result'

const step = ref<Step>('upload')
const fileList = ref<UploaderFileListItem[]>([])
const importData = ref<ExportData | null>(null)
const conflicts = ref<ConflictItem[]>([])
const skipSet = ref<Set<string>>(new Set())
const result = ref<ImportResult | null>(null)
const loading = ref(false)

function close() {
  emit('update:visible', false)
  resetState()
}

function resetState() {
  step.value = 'upload'
  fileList.value = []
  importData.value = null
  conflicts.value = []
  skipSet.value = new Set()
  result.value = null
}

async function handleRead(
  files: UploaderFileListItem | UploaderFileListItem[]
) {
  const item = Array.isArray(files) ? files[0] : files
  const file = item?.file
  if (!file) return
  loading.value = true
  try {
    const text = await file.text()
    const data = JSON.parse(text) as ExportData
    importData.value = data
    const resp = await importApi.checkConflicts(data)
    if (resp.has_conflicts) {
      conflicts.value = resp.conflicts
      step.value = 'conflicts'
    } else {
      await executeImport()
    }
  } catch (e: any) {
    showToast(e.message || '文件解析失败')
  } finally {
    loading.value = false
  }
}

function conflictKey(c: ConflictItem): string {
  if (c.type === 'category') return `category:${c.name}`
  return `sub_category:${c.name}`
}

function toggleSkip(c: ConflictItem) {
  const key = conflictKey(c)
  if (skipSet.value.has(key)) {
    skipSet.value.delete(key)
  } else {
    skipSet.value.add(key)
  }
}

async function executeImport() {
  if (!importData.value) return
  loading.value = true
  try {
    const resp = await importApi.execute(
      importData.value,
      Array.from(skipSet.value)
    )
    result.value = resp
    step.value = 'result'
    emit('imported')
  } catch (e: any) {
    showToast(e.message || '导入失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <van-popup
    :show="visible"
    position="bottom"
    round
    :style="{ maxHeight: '80%' }"
    @update:show="emit('update:visible', $event)"
  >
    <div class="import">
      <div class="import-title">导入数据</div>
      <div class="import-body" :style="{ textAlign: 'center' }">
        <van-loading v-if="loading" />

        <div v-else-if="step === 'upload'">
          <van-uploader
            v-model="fileList"
            :max-count="1"
            accept=".json"
            :after-read="handleRead"
          >
            <div class="import-tip">
              <van-icon name="description" size="40" color="var(--van-text-color-3)" />
              <div>选择 JSON 备份文件</div>
            </div>
          </van-uploader>
        </div>

        <div v-else-if="step === 'conflicts'" class="left">
          <div class="conflict-desc">
            发现以下冲突项，勾选的项目将被跳过：
          </div>
          <van-cell-group inset>
            <van-cell
              v-for="c in conflicts"
              :key="conflictKey(c)"
              :title="c.name"
              :label="c.type === 'category' ? '大类' : '子分类'"
              clickable
              @click="toggleSkip(c)"
            >
              <template #right-icon>
                <van-checkbox
                  :model-value="skipSet.has(conflictKey(c))"
                  @update:model-value="toggleSkip(c)"
                />
              </template>
            </van-cell>
          </van-cell-group>
          <van-button
            block
            type="primary"
            :disabled="loading"
            @click="executeImport"
          >
            确认导入
          </van-button>
        </div>

        <div v-else-if="step === 'result' && result">
          <van-icon name="checked" size="56" color="#07c160" />
          <div class="result-title">导入完成</div>
          <div class="result-desc">
            新增大类 {{ result.categories_created }} 个，子分类
            {{ result.sub_categories_created }} 个，物品
            {{ result.items_created }} 个
          </div>
          <van-button block plain type="primary" @click="close">关闭</van-button>
        </div>
      </div>

      <template v-if="step !== 'result'">
        <van-button block plain @click="close">取消</van-button>
        <div class="pad" />
      </template>
    </div>
  </van-popup>
</template>

<style scoped>
.import {
  padding: 0 16px;
}

.import-title {
  padding: 16px 0;
  text-align: center;
  font-weight: 600;
}

.import-body {
  min-height: 120px;
  padding-bottom: 8px;
}

.import-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 200px;
  margin: 0 auto;
  height: 110px;
  gap: 8px;
  color: var(--van-text-color-2);
  font-size: 13px;
  border: 1px dashed var(--van-text-color-3);
  border-radius: 8px;
}

.left {
  text-align: left;
}

.conflict-desc {
  color: var(--van-text-color-2);
  font-size: 13px;
  padding: 4px 8px 8px;
}

.result-title {
  margin-top: 12px;
  font-size: 16px;
  font-weight: 600;
}

.result-desc {
  color: var(--van-text-color-2);
  font-size: 13px;
  margin: 8px 0 16px;
  line-height: 1.5;
}

.pad {
  height: 16px;
}
</style>
