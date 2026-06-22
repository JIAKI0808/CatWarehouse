<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NInputNumber, NButton } from 'naive-ui'
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
        <NFormItem label="录入人">
          <NInput v-model:value="form.recorder" placeholder="请输入录入人" />
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
