<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NButton, NInputNumber, NDatePicker } from 'naive-ui'
import type { Pricing } from '@/types'

interface FormData {
  name: string
  cost: number
  suggested_price: number
  discount: number
  description: string
  notes: string
  record_date: number
}

const props = defineProps<{
  visible: boolean
  editData?: Pricing | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: FormData): void
}>()

const form = ref<FormData>({
  name: '',
  cost: 0,
  suggested_price: 0,
  discount: 1.0,
  description: '',
  notes: '',
  record_date: Date.now(),
})

watch(() => props.visible, (val) => {
  if (val && props.editData) {
    form.value = {
      name: props.editData.name ?? '',
      cost: props.editData.cost ?? 0,
      suggested_price: props.editData.suggested_price ?? 0,
      discount: props.editData.discount ?? 1.0,
      description: props.editData.description ?? '',
      notes: props.editData.notes ?? '',
      record_date: props.editData.record_date ? new Date(props.editData.record_date).getTime() : Date.now(),
    }
  } else if (!val) {
    resetForm()
  }
})

function resetForm() {
  form.value = {
    name: '',
    cost: 0,
    suggested_price: 0,
    discount: 1.0,
    description: '',
    notes: '',
    record_date: Date.now(),
  }
}

function handleClose() {
  emit('update:visible', false)
}

function handleSubmit() {
  emit('submit', { ...form.value })
  handleClose()
}
</script>

<template>
  <NModal :show="visible" @update:show="emit('update:visible', $event)">
    <div class="bg-white rounded-lg p-6 w-96">
      <h2 class="text-lg font-bold mb-4">{{ editData ? '编辑售价' : '新增售价' }}</h2>
      <NForm>
        <NFormItem label="商品名">
          <NInput v-model:value="form.name" placeholder="请输入商品名" />
        </NFormItem>
        <NFormItem label="成本">
          <NInputNumber v-model:value="form.cost" :min="0" :precision="2" style="width: 100%" />
        </NFormItem>
        <NFormItem label="建议售价">
          <NInputNumber v-model:value="form.suggested_price" :min="0" :precision="2" style="width: 100%" />
        </NFormItem>
        <NFormItem label="折扣系数">
          <NInputNumber v-model:value="form.discount" :min="0" :max="10" :step="0.1" :precision="2" style="width: 100%" />
        </NFormItem>
        <NFormItem label="描述">
          <NInput v-model:value="form.description" type="textarea" placeholder="请输入描述" />
        </NFormItem>
        <NFormItem label="备注">
          <NInput v-model:value="form.notes" type="textarea" placeholder="请输入备注" />
        </NFormItem>
        <NFormItem label="记录日期">
          <NDatePicker v-model:value="form.record_date" type="date" style="width: 100%" />
        </NFormItem>
      </NForm>
      <div class="flex justify-end gap-2 mt-4">
        <NButton @click="handleClose">取消</NButton>
        <NButton type="primary" @click="handleSubmit">保存</NButton>
      </div>
    </div>
  </NModal>
</template>
