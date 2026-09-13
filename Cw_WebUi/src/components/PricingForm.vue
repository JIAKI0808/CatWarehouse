<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NButton, NInputNumber, NDatePicker } from 'naive-ui'
import { useI18n } from 'vue-i18n'
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

const { t } = useI18n()

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
      <h2 class="text-lg font-bold mb-4">
        {{ editData ? t('app.pricing.editPricing') : t('app.pricing.addPricing') }}
      </h2>
      <NForm>
        <NFormItem :label="t('app.pricing.productName')">
          <NInput v-model:value="form.name" :placeholder="t('app.pricing.inputName')" />
        </NFormItem>
        <NFormItem :label="t('app.pricing.cost')">
          <NInputNumber v-model:value="form.cost" :min="0" :precision="2" style="width: 100%" />
        </NFormItem>
        <NFormItem :label="t('app.pricing.suggestedPrice')">
          <NInputNumber v-model:value="form.suggested_price" :min="0" :precision="2" style="width: 100%" />
        </NFormItem>
        <NFormItem :label="t('app.pricing.discount')">
          <NInputNumber v-model:value="form.discount" :min="0" :max="10" :step="0.1" :precision="2" style="width: 100%" />
        </NFormItem>
        <NFormItem :label="t('app.common.description')">
          <NInput v-model:value="form.description" type="textarea" :placeholder="t('app.common.inputDescription')" />
        </NFormItem>
        <NFormItem :label="t('app.common.notes')">
          <NInput v-model:value="form.notes" type="textarea" :placeholder="t('app.common.inputNotes')" />
        </NFormItem>
        <NFormItem :label="t('app.pricing.recordDate')">
          <NDatePicker v-model:value="form.record_date" type="date" style="width: 100%" />
        </NFormItem>
      </NForm>
      <div class="flex justify-end gap-2 mt-4">
        <NButton @click="handleClose">{{ t('app.common.cancel') }}</NButton>
        <NButton type="primary" @click="handleSubmit">{{ t('app.common.save') }}</NButton>
      </div>
    </div>
  </NModal>
</template>
