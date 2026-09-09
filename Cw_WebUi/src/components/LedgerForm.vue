<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NButton, NSelect, NDatePicker } from 'naive-ui'
import type { Ledger } from '@/types'

interface FormData {
  amount: number
  date: number
  platform: string
  description: string
  notes: string
  person: string
  type: 'income' | 'expense'
}

const props = defineProps<{
  visible: boolean
  editData?: Ledger | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: FormData): void
}>()

const form = ref<FormData>({
  amount: 0,
  date: Date.now(),
  platform: '',
  description: '',
  notes: '',
  person: '',
  type: 'expense',
})

const typeOptions = [
  { label: '支出', value: 'expense' },
  { label: '收入', value: 'income' },
]

watch(() => props.visible, (val) => {
  if (val && props.editData) {
    form.value = {
      amount: props.editData.amount,
      date: new Date(props.editData.date).getTime(),
      platform: props.editData.platform,
      description: props.editData.description,
      notes: props.editData.notes,
      person: props.editData.person,
      type: props.editData.type,
    }
  } else if (!val) {
    resetForm()
  }
})

function resetForm() {
  form.value = {
    amount: 0,
    date: Date.now(),
    platform: '',
    description: '',
    notes: '',
    person: '',
    type: 'expense',
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
      <h2 class="text-lg font-bold mb-4">{{ editData ? '编辑账单' : '新增账单' }}</h2>
      <NForm>
        <NFormItem label="金额">
          <NInput v-model:value="form.amount" type="number" placeholder="0.00" />
        </NFormItem>
        <NFormItem label="类型">
          <NSelect v-model:value="form.type" :options="typeOptions" />
        </NFormItem>
        <NFormItem label="日期">
          <NDatePicker v-model:value="form.date" type="date" style="width: 100%" />
        </NFormItem>
        <NFormItem label="平台">
          <NInput v-model:value="form.platform" placeholder="支付宝/微信/银行等" />
        </NFormItem>
        <NFormItem label="描述">
          <NInput v-model:value="form.description" placeholder="消费描述" />
        </NFormItem>
        <NFormItem label="记账人">
          <NInput v-model:value="form.person" placeholder="谁记的" />
        </NFormItem>
        <NFormItem label="备注">
          <NInput v-model:value="form.notes" type="textarea" placeholder="备注" />
        </NFormItem>
      </NForm>
      <div class="flex justify-end gap-2 mt-4">
        <NButton @click="handleClose">取消</NButton>
        <NButton type="primary" @click="handleSubmit">保存</NButton>
      </div>
    </div>
  </NModal>
</template>
