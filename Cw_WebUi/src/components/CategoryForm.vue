<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { NModal, NForm, NFormItem, NInput, NButton, NIcon } from 'naive-ui'
import {
  FolderOutline,
  CartOutline,
  ShirtOutline,
  HardwareChipOutline,
  NutritionOutline,
  CameraOutline,
  GameControllerOutline,
  BookOutline,
  MusicalNotesOutline,
  FitnessOutline,
  HeartOutline,
  StarOutline,
  FlashlightOutline,
  ColorPaletteOutline,
  CubeOutline,
  DiamondOutline,
} from '@vicons/ionicons5'

const iconOptions = [
  { name: 'FolderOutline', label: '文件夹', component: FolderOutline },
  { name: 'CartOutline', label: '购物车', component: CartOutline },
  { name: 'ShirtOutline', label: '衣物', component: ShirtOutline },
  { name: 'HardwareChipOutline', label: '芯片', component: HardwareChipOutline },
  { name: 'NutritionOutline', label: '营养', component: NutritionOutline },
  { name: 'CameraOutline', label: '相机', component: CameraOutline },
  { name: 'GameControllerOutline', label: '游戏', component: GameControllerOutline },
  { name: 'BookOutline', label: '书本', component: BookOutline },
  { name: 'MusicalNotesOutline', label: '音乐', component: MusicalNotesOutline },
  { name: 'FitnessOutline', label: '健身', component: FitnessOutline },
  { name: 'HeartOutline', label: '心形', component: HeartOutline },
  { name: 'StarOutline', label: '星形', component: StarOutline },
  { name: 'FlashlightOutline', label: '手电', component: FlashlightOutline },
  { name: 'ColorPaletteOutline', label: '调色板', component: ColorPaletteOutline },
  { name: 'CubeOutline', label: '立方体', component: CubeOutline },
  { name: 'DiamondOutline', label: '钻石', component: DiamondOutline },
]

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
  icon: 'FolderOutline',
  unit: '个',
  notes: '',
})

const selectedIcon = computed(() =>
  iconOptions.find(i => i.name === form.value.icon) ?? iconOptions[0]
)

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
    icon: 'FolderOutline',
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
        <template v-if="type === 'category'">
          <NFormItem label="图标">
            <div class="flex flex-wrap gap-2">
              <div
                v-for="icon in iconOptions"
                :key="icon.name"
                class="w-10 h-10 rounded-lg border-2 cursor-pointer flex items-center justify-center transition-all"
                :class="form.icon === icon.name
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-400'"
                :title="icon.label"
                @click="form.icon = icon.name"
              >
                <NIcon :size="20" :component="icon.component" />
              </div>
            </div>
          </NFormItem>
        </template>
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
