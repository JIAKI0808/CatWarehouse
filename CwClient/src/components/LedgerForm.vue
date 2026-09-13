<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { NModal, NForm, NFormItem, NInput, NButton, NSelect, NDatePicker } from 'naive-ui'
import { useI18n } from 'vue-i18n'
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

const { t } = useI18n()

const typeOptions = computed(() => [
  { label: t('app.ledger.typeExpense'), value: 'expense' },
  { label: t('app.ledger.typeIncome'), value: 'income' },
])

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
      <h2 class="text-lg font-bold mb-4">
        {{ editData ? t('app.ledger.editBill') : t('app.ledger.addBill') }}
      </h2>
      <NForm>
        <NFormItem :label="t('app.ledger.amount')">
          <NInput v-model:value="form.amount" type="number" placeholder="0.00" />
        </NFormItem>
        <NFormItem :label="t('app.ledger.type')">          <NSelect v-model:value="form.type" :options="typeOptions" />
        </NFormItem>
        <NFormItem :label="t('app.ledger.date')">
          <NDatePicker v-model:value="form.date" type="date" style="width: 100%" />
        </NFormItem>
        <NFormItem :label="t('app.ledger.platform')">
          <NInput v-model:value="form.platform" :placeholder="t('app.ledger.inputPlatform')" />
        </NFormItem>
        <NFormItem :label="t('app.common.description')">
          <NInput v-model:value="form.description" :placeholder="t('app.ledger.inputDescription')" />
        </NFormItem>
        <NFormItem :label="t('app.ledger.person')">
          <NInput v-model:value="form.person" :placeholder="t('app.ledger.inputPerson')" />
        </NFormItem>
        <NFormItem :label="t('app.common.notes')">
          <NInput v-model:value="form.notes" type="textarea" :placeholder="t('app.common.notes')" />
        </NFormItem>
      </NForm>
      <div class="flex justify-end gap-2 mt-4">
        <NButton @click="handleClose">{{ t('app.common.cancel') }}</NButton>
        <NButton type="primary" @click="handleSubmit">{{ t('app.common.save') }}</NButton>
      </div>
    </div>
  </NModal>
</template>
