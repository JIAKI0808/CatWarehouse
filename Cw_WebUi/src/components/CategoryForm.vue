<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import {
  NModal, NForm, NFormItem, NInput, NButton, NIcon, NColorPicker, NSelect,
} from 'naive-ui'
import { useI18n } from 'vue-i18n'
import { useUnitStore } from '@/stores/units'
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
  HomeOutline,
  CarOutline,
  WalkOutline,
  AirplaneOutline,
  PawOutline,
  LeafOutline,
  FlameOutline,
  WaterOutline,
  SunnyOutline,
  MoonOutline,
  CloudyOutline,
  UmbrellaOutline,
  GiftOutline,
  SparklesOutline,
  TrophyOutline,
  WineOutline,
  CafeOutline,
  PizzaOutline,
  MedicalOutline,
  WalletOutline,
  KeyOutline,
  LockClosedOutline,
  GlobeOutline,
  MapOutline,
  TimeOutline,
  BoatOutline,
  BeerOutline,
  BugOutline,
  FishOutline,
  BulbOutline,
  ExtensionPuzzleOutline,
  RibbonOutline,
} from '@vicons/ionicons5'

/**
 * 图标选择器。**刻意不带 label 字段** —— tooltip 文案走 `t('app.icons.<组件名>')`
 * 在模板里查语言包。理由：把 48 条中文写在这里，等于同一份文案在语言包之外
 * 又存了一份，翻译时必然漏掉这一处；键直接取组件名，也不会有对不上的风险。
 */
const iconOptions = [
  { name: 'FolderOutline', component: FolderOutline },
  { name: 'CartOutline', component: CartOutline },
  { name: 'ShirtOutline', component: ShirtOutline },
  { name: 'HardwareChipOutline', component: HardwareChipOutline },
  { name: 'NutritionOutline', component: NutritionOutline },
  { name: 'CameraOutline', component: CameraOutline },
  { name: 'GameControllerOutline', component: GameControllerOutline },
  { name: 'BookOutline', component: BookOutline },
  { name: 'MusicalNotesOutline', component: MusicalNotesOutline },
  { name: 'FitnessOutline', component: FitnessOutline },
  { name: 'HeartOutline', component: HeartOutline },
  { name: 'StarOutline', component: StarOutline },
  { name: 'FlashlightOutline', component: FlashlightOutline },
  { name: 'ColorPaletteOutline', component: ColorPaletteOutline },
  { name: 'CubeOutline', component: CubeOutline },
  { name: 'DiamondOutline', component: DiamondOutline },
  { name: 'HomeOutline', component: HomeOutline },
  { name: 'CarOutline', component: CarOutline },
  { name: 'WalkOutline', component: WalkOutline },
  { name: 'AirplaneOutline', component: AirplaneOutline },
  { name: 'BoatOutline', component: BoatOutline },
  { name: 'PawOutline', component: PawOutline },
  { name: 'LeafOutline', component: LeafOutline },
  { name: 'FlameOutline', component: FlameOutline },
  { name: 'WaterOutline', component: WaterOutline },
  { name: 'SunnyOutline', component: SunnyOutline },
  { name: 'MoonOutline', component: MoonOutline },
  { name: 'CloudyOutline', component: CloudyOutline },
  { name: 'UmbrellaOutline', component: UmbrellaOutline },
  { name: 'GiftOutline', component: GiftOutline },
  { name: 'SparklesOutline', component: SparklesOutline },
  { name: 'TrophyOutline', component: TrophyOutline },
  { name: 'WineOutline', component: WineOutline },
  { name: 'CafeOutline', component: CafeOutline },
  { name: 'PizzaOutline', component: PizzaOutline },
  { name: 'MedicalOutline', component: MedicalOutline },
  { name: 'WalletOutline', component: WalletOutline },
  { name: 'KeyOutline', component: KeyOutline },
  { name: 'LockClosedOutline', component: LockClosedOutline },
  { name: 'GlobeOutline', component: GlobeOutline },
  { name: 'MapOutline', component: MapOutline },
  { name: 'TimeOutline', component: TimeOutline },
  { name: 'BeerOutline', component: BeerOutline },
  { name: 'BugOutline', component: BugOutline },
  { name: 'FishOutline', component: FishOutline },
  { name: 'BulbOutline', component: BulbOutline },
  { name: 'ExtensionPuzzleOutline', component: ExtensionPuzzleOutline },
  { name: 'RibbonOutline', component: RibbonOutline },
]

interface EditData {
  name: string
  description?: string
  icon?: string
  icon_color?: string
  unit?: string
  notes?: string
}

const props = defineProps<{
  visible: boolean
  type: 'category' | 'subCategory'
  title: string
  editData?: EditData
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: Record<string, string>): void
}>()

const unitStore = useUnitStore()
const { t } = useI18n()

const unitOptions = computed(() => unitStore.units.map((u) => ({ label: u, value: u })))

const form = ref({
  name: '',
  description: '',
  icon: 'FolderOutline',
  icon_color: '#f59e0b',
  unit: unitStore.defaultUnit,
  notes: '',
})

const selectedIcon = computed(() =>
  iconOptions.find(i => i.name === form.value.icon) ?? iconOptions[0]
)

watch(
  () => props.visible,
  (val) => {
    if (val && props.editData) {
      form.value = {
        name: props.editData.name ?? '',
        description: props.editData.description ?? '',
        icon: props.editData.icon ?? 'FolderOutline',
        icon_color: props.editData.icon_color ?? '#f59e0b',
        unit: props.editData.unit ?? unitStore.defaultUnit,
        notes: props.editData.notes ?? '',
      }
    } else if (!val) {
      resetForm()
    }
  }
)

function resetForm() {
  form.value = {
    name: '',
    description: '',
    icon: 'FolderOutline',
    icon_color: '#f59e0b',
    // 在**重置时**取值而不是在模块顶层取常量：字典是异步拉的，
    // 顶层取会永远拿到兜底值（与 i18n 那边「存 key 而不是存译文」同一个道理）。
    unit: unitStore.defaultUnit,
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
        <NFormItem :label="t('app.common.name')">
          <NInput v-model:value="form.name" :placeholder="t('app.common.inputName')" />
        </NFormItem>
        <NFormItem :label="t('app.common.description')">
          <NInput
            v-model:value="form.description"
            type="textarea"
            :placeholder="t('app.common.inputDescription')"
          />
        </NFormItem>
        <template v-if="type === 'category'">
          <NFormItem :label="t('app.common.icon')">
            <div class="flex flex-wrap gap-2">
              <div
                v-for="icon in iconOptions"
                :key="icon.name"
                class="w-10 h-10 rounded-lg border-2 cursor-pointer flex items-center justify-center transition-all"
                :class="form.icon === icon.name
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-400'"
                :title="t('app.icons.' + icon.name)"
                @click="form.icon = icon.name"
              >
                <NIcon :size="20" :component="icon.component" :color="form.icon_color" />
              </div>
            </div>
          </NFormItem>
          <NFormItem :label="t('app.common.iconColor')">
            <NColorPicker v-model:value="form.icon_color" :show-alpha="false" />
          </NFormItem>
        </template>
        <template v-if="type === 'subCategory'">
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
          <NFormItem :label="t('app.common.notes')">
            <NInput
              v-model:value="form.notes"
              type="textarea"
              :placeholder="t('app.common.inputNotes')"
            />
          </NFormItem>
        </template>
      </NForm>
      <div class="flex justify-end gap-2 mt-4">
        <NButton @click="handleClose">{{ t('app.common.cancel') }}</NButton>
        <NButton type="primary" @click="handleSubmit">{{ t('app.common.save') }}</NButton>
      </div>
    </div>
  </NModal>
</template>
