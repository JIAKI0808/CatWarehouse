<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import {
  NModal, NForm, NFormItem, NInput, NInputNumber, NButton, NDatePicker, NSwitch, NSelect,
} from 'naive-ui'
import { useI18n } from 'vue-i18n'
import { useCurrencyStore } from '@/stores/currency'
import { useUnitStore } from '@/stores/units'
import type { Item } from '@/types'

const currencyStore = useCurrencyStore()
const unitStore = useUnitStore()
const unitOptions = computed(() => unitStore.units.map((u) => ({ label: u, value: u })))

const props = defineProps<{
  visible: boolean
  item?: Item | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: Record<string, unknown>): void
}>()

const { t } = useI18n()

const form = ref({
  name: '',
  price: 0,
  recorder: '',
  description: '',
  quantity: 0,
  unit: unitStore.defaultUnit,
  expire_date: null as number | null,
  is_expired: false,
})

watch(
  () => props.visible,
  (val) => {
    if (val && props.item) {
      form.value = {
        name: props.item.name,
        price: props.item.price,
        recorder: props.item.recorder,
        description: props.item.description,
        quantity: props.item.quantity,
        unit: props.item.unit,
        expire_date: props.item.expire_date
          ? new Date(props.item.expire_date).getTime()
          : null,
        is_expired: props.item.is_expired,
      }
    } else if (!val) {
      resetForm()
    }
  }
)

function resetForm() {
  form.value = {
    name: '',
    price: 0,
    recorder: '',
    description: '',
    quantity: 0,
    // 重置时取当前默认单位（字典是异步拉的，不能在建模块时取常量）
    unit: unitStore.defaultUnit,
    expire_date: null,
    is_expired: false,
  }
}

function handleClose() {
  emit('update:visible', false)
}

function handleSubmit() {
  const data: Record<string, unknown> = { ...form.value }
  if (data.expire_date) {
    data.expire_date = new Date(data.expire_date as number).toISOString()
  }
  emit('submit', data)
  handleClose()
}
</script>

<template>
  <NModal :show="visible" @update:show="emit('update:visible', $event)">
    <div class="bg-white rounded-lg p-6 w-96">
      <h2 class="text-lg font-bold mb-4">
        {{ item ? t('app.inventory.editItem') : t('app.inventory.addItem') }}
      </h2>
      <NForm>
        <NFormItem :label="t('app.common.name')">
          <NInput v-model:value="form.name" :placeholder="t('app.common.inputName')" />
        </NFormItem>
        <NFormItem :label="t('app.common.price')">
          <NInputNumber v-model:value="form.price" :min="0" :precision="2">
            <template #prefix>{{ currencyStore.symbol }}</template>
          </NInputNumber>
        </NFormItem>
        <NFormItem :label="t('app.common.quantity')">
          <NInputNumber v-model:value="form.quantity" :min="0" />
        </NFormItem>
        <NFormItem :label="t('app.common.unit')">
          <!-- 选或自由输入：字典来自后端，同时允许输入清单外的单位 -->
          <NSelect
            v-model:value="form.unit"
            :options="unitOptions"
            filterable
            tag
            :placeholder="t('app.common.inputUnit')"
          />
        </NFormItem>
        <NFormItem :label="t('app.common.recorder')">
          <NInput v-model:value="form.recorder" :placeholder="t('app.common.inputRecorder')" />
        </NFormItem>
        <NFormItem :label="t('app.common.expiresAt')">
          <NDatePicker
            v-model:value="form.expire_date"
            type="date"
            clearable
            :placeholder="t('app.common.selectExpiry')"
          />
        </NFormItem>
        <NFormItem :label="t('app.common.expired')">
          <NSwitch v-model:value="form.is_expired" />
        </NFormItem>
        <NFormItem :label="t('app.common.description')">
          <NInput
            v-model:value="form.description"
            type="textarea"
            :placeholder="t('app.common.inputDescription')"
          />
        </NFormItem>
      </NForm>
      <div class="flex justify-end gap-2 mt-4">
        <NButton @click="handleClose">{{ t('app.common.cancel') }}</NButton>
        <NButton type="primary" @click="handleSubmit">{{ t('app.common.save') }}</NButton>
      </div>
    </div>
  </NModal>
</template>
