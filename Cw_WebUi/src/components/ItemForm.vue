<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NInputNumber, NButton, NDatePicker, NSwitch } from 'naive-ui'
import type { Item } from '@/types'

const props = defineProps<{
  visible: boolean
  item?: Item | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: Record<string, unknown>): void
}>()

const form = ref({
  name: '',
  price: 0,
  recorder: '',
  description: '',
  quantity: 0,
  unit: '个',
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
    unit: '个',
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
        {{ item ? '编辑物品' : '新增物品' }}
      </h2>
      <NForm>
        <NFormItem label="名称">
          <NInput v-model:value="form.name" placeholder="请输入名称" />
        </NFormItem>
        <NFormItem label="价格">
          <NInputNumber v-model:value="form.price" :min="0" :precision="2">
            <template #prefix>¥</template>
          </NInputNumber>
        </NFormItem>
        <NFormItem label="库存数量">
          <NInputNumber v-model:value="form.quantity" :min="0" />
        </NFormItem>
        <NFormItem label="单位">
          <NInput v-model:value="form.unit" placeholder="请输入单位" />
        </NFormItem>
        <NFormItem label="录入人">
          <NInput v-model:value="form.recorder" placeholder="请输入录入人" />
        </NFormItem>
        <NFormItem label="过期时间">
          <NDatePicker
            v-model:value="form.expire_date"
            type="date"
            clearable
            placeholder="请选择过期时间"
          />
        </NFormItem>
        <NFormItem label="已过期">
          <NSwitch v-model:value="form.is_expired" />
        </NFormItem>
        <NFormItem label="描述">
          <NInput
            v-model:value="form.description"
            type="textarea"
            placeholder="请输入描述"
          />
        </NFormItem>
      </NForm>
      <div class="flex justify-end gap-2 mt-4">
        <NButton @click="handleClose">取消</NButton>
        <NButton type="primary" @click="handleSubmit">保存</NButton>
      </div>
    </div>
  </NModal>
</template>
