<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NButton } from 'naive-ui'

const props = defineProps<{
  visible: boolean
  type: 'category' | 'subCategory'
  title: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: Record<string, string>): void
}>()

const form = ref({
  name: '',
  description: '',
  unit: '个',
  notes: '',
})

watch(
  () => props.visible,
  (val) => {
    if (!val) {
      resetForm()
    }
  }
)

function resetForm() {
  form.value = {
    name: '',
    description: '',
    unit: '个',
    notes: '',
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
      <h2 class="text-lg font-bold mb-4">{{ title }}</h2>
      <NForm>
        <NFormItem label="名称">
          <NInput v-model:value="form.name" placeholder="请输入名称" />
        </NFormItem>
        <NFormItem label="描述">
          <NInput
            v-model:value="form.description"
            type="textarea"
            placeholder="请输入描述"
          />
        </NFormItem>
        <template v-if="type === 'subCategory'">
          <NFormItem label="单位">
            <NInput v-model:value="form.unit" placeholder="个" />
          </NFormItem>
          <NFormItem label="备注">
            <NInput
              v-model:value="form.notes"
              type="textarea"
              placeholder="请输入备注"
            />
          </NFormItem>
        </template>
      </NForm>
      <div class="flex justify-end gap-2 mt-4">
        <NButton @click="handleClose">取消</NButton>
        <NButton type="primary" @click="handleSubmit">保存</NButton>
      </div>
    </div>
  </NModal>
</template>
