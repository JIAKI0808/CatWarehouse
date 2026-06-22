<script setup lang="ts">
import { ref } from 'vue'
import {
  NModal, NCard, NButton, NSpace, NUpload, NUploadDragger,
  NText, NIcon, NTable, NCheckbox, NSpin, NResult,
} from 'naive-ui'
import { DocumentTextOutline } from '@vicons/ionicons5'
import type { UploadFileInfo } from 'naive-ui'
import { exportApi, importApi } from '@/services/api'
import type { ExportData, ConflictItem, ImportResult } from '@/services/api'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'imported'): void
}>()

const step = ref<'upload' | 'conflicts' | 'result'>('upload')
const fileList = ref<UploadFileInfo[]>([])
const loading = ref(false)
const importData = ref<ExportData | null>(null)
const conflicts = ref<ConflictItem[]>([])
const skipSet = ref<Set<string>>(new Set())
const result = ref<ImportResult | null>(null)

function handleClose() {
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

async function handleFileReady({ fileList: list }: { fileList: UploadFileInfo[] }) {
  const file = list[0]?.file
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
    importData.value = null
    alert(e.message || '文件解析失败')
  } finally {
    loading.value = false
  }
}

function toggleSkip(key: string) {
  if (skipSet.value.has(key)) {
    skipSet.value.delete(key)
  } else {
    skipSet.value.add(key)
  }
}

function conflictKey(c: ConflictItem) {
  if (c.type === 'category') return `category:${c.name}`
  return `sub_category:${c.name}`
}

async function executeImport() {
  if (!importData.value) return
  loading.value = true
  try {
    const resp = await importApi.execute(importData.value, Array.from(skipSet.value))
    result.value = resp
    step.value = 'result'
    emit('imported')
  } catch (e: any) {
    alert(e.message || '导入失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <NModal :show="visible" @update:show="handleClose">
    <NCard
      title="导入数据"
      style="width: 600px"
      :bordered="false"
      size="huge"
    >
      <NSpin :show="loading">
        <!-- Step 1: Upload -->
        <div v-if="step === 'upload'">
          <NUpload
            :max="1"
            accept=".json"
            :default-upload="false"
            @change="handleFileReady"
          >
            <NUploadDragger>
              <div style="margin-bottom: 12px">
                <NIcon size="48" :depth="3">
                  <DocumentTextOutline />
                </NIcon>
              </div>
              <NText depth="3" style="font-size: 16px">
                点击或者拖动 JSON 文件到此区域
              </NText>
            </NUploadDragger>
          </NUpload>
        </div>

        <!-- Step 2: Conflicts -->
        <div v-else-if="step === 'conflicts'">
          <NText depth="2" style="margin-bottom: 12px; display: block">
            发现以下冲突项，勾选的项目将被跳过：
          </NText>
          <NTable :bordered="false" :single-line="false" size="small">
            <thead>
              <tr>
                <th style="width: 50px">跳过</th>
                <th>类型</th>
                <th>名称</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in conflicts" :key="conflictKey(c)">
                <td>
                  <NCheckbox
                    :checked="skipSet.has(conflictKey(c))"
                    @update:checked="toggleSkip(conflictKey(c))"
                  />
                </td>
                <td>{{ c.type === 'category' ? '大类' : '子分类' }}</td>
                <td>{{ c.name }}</td>
              </tr>
            </tbody>
          </NTable>
        </div>

        <!-- Step 3: Result -->
        <div v-else-if="step === 'result' && result">
          <NResult
            status="success"
            title="导入完成"
            :description="`新增大类 ${result.categories_created} 个，子分类 ${result.sub_categories_created} 个，物品 ${result.items_created} 个`"
          />
        </div>
      </NSpin>

      <template #footer>
        <NSpace justify="end">
          <NButton @click="handleClose">关闭</NButton>
          <NButton
            v-if="step === 'conflicts'"
            type="primary"
            :loading="loading"
            @click="executeImport"
          >
            确认导入
          </NButton>
        </NSpace>
      </template>
    </NCard>
  </NModal>
</template>
