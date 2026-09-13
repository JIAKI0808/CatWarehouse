<script setup lang="ts">
import { ref, watch } from 'vue'
import { showToast } from 'vant'
import { useI18n } from 'vue-i18n'
import { useUnitStore } from '@/stores/units'
import {
  categoryIconOptions,
  categoryColors,
  getCategoryIcon,
} from '@/utils/categoryIcons'

const unitStore = useUnitStore()

const { t } = useI18n()

interface FormModel {
  name: string
  description: string
  icon: string
  icon_color: string
  unit: string
  notes: string
}

const props = defineProps<{
  visible: boolean
  type: 'category' | 'subCategory'
  title: string
  editData?: Partial<FormModel>
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: Record<string, string>): void
}>()

function blankForm(): FormModel {
  return {
    name: '',
    description: '',
    icon: 'FolderOutline',
    icon_color: '#f59e0b',
    unit: unitStore.defaultUnit,
    notes: '',
  }
}

const form = ref<FormModel>(blankForm())

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
    } else if (val) {
      form.value = blankForm()
    }
  }
)

function close() {
  emit('update:visible', false)
}

function submit() {
  if (!form.value.name.trim()) {
    showToast(t('app.common.inputName'))
    return
  }
  emit('submit', { ...form.value })
  close()
}
</script>

<template>
  <van-popup
    :show="visible"
    position="bottom"
    round
    :style="{ maxHeight: '88%' }"
    @update:show="emit('update:visible', $event)"
  >
    <van-nav-bar
      :title="title"
      :left-text="t('app.common.cancel')"
      :right-text="t('app.common.save')"
      @click-left="close"
      @click-right="submit"
    />
    <div class="cat-body">
      <van-cell-group inset>
        <van-field
          v-model="form.name"
          :label="t('app.common.name')"
          :placeholder="t('app.common.inputName')"
        />
        <van-field
          v-model="form.description"
          rows="2"
          autosize
          type="textarea"
          :label="t('app.common.description')"
          :placeholder="t('app.common.inputDescription')"
        />
        <template v-if="type === 'category'">
          <van-cell :title="t('app.common.icon')" :border="false" />
          <div class="icon-grid">
            <div
              v-for="icon in categoryIconOptions"
              :key="icon.name"
              class="icon-item"
              :class="{ active: form.icon === icon.name }"
              :title="t('app.icons.' + icon.name)"
              @click="form.icon = icon.name"
            >
              <component
                :is="getCategoryIcon(icon.name)"
                :style="{ color: form.icon_color }"
              />
            </div>
          </div>
          <van-cell :title="t('app.common.iconColor')" :border="false" />
          <div class="color-row">
            <span
              v-for="c in categoryColors"
              :key="c"
              class="color-dot"
              :class="{ active: form.icon_color === c }"
              :style="{ background: c }"
              @click="form.icon_color = c"
            />
          </div>
        </template>
        <template v-else>
          <van-field
            v-model="form.unit"
            :label="t('app.common.unit')"
            :placeholder="t('app.common.inputUnit')"
          />
          <!-- 单位字典：**收纳在字段正下方**的一行 chips，点一下填入。
               不替换输入框 —— 字典里没有的单位仍然可以手打（「选或自由输入」）。 -->
          <div v-if="unitStore.units.length" class="unit-chips">
            <span
              v-for="u in unitStore.units"
              :key="u"
              class="unit-chip"
              :class="{ active: form.unit === u }"
              @click="form.unit = u"
            >
              {{ u }}
            </span>
          </div>
          <van-field
            v-model="form.notes"
            rows="2"
            autosize
            type="textarea"
            :label="t('app.common.notes')"
            :placeholder="t('app.common.inputNotes')"
          />
        </template>
      </van-cell-group>
    </div>
  </van-popup>
</template>

<style scoped>
.cat-body {
  max-height: 76vh;
  overflow-y: auto;
  padding-bottom: 24px;
}

.icon-grid {
  display: flex;
  flex-wrap: wrap;
  padding: 0 16px 8px;
}

.icon-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  margin: 4px;
  font-size: 20px;
  border: 1px solid #ebedf0;
  border-radius: 8px;
}

.icon-item.active {
  border-color: #1989fa;
  background: #ecf5ff;
}

.color-row {
  display: flex;
  flex-wrap: wrap;
  padding: 0 16px 12px;
}

.color-dot {
  width: 28px;
  height: 28px;
  margin: 6px;
  border-radius: 50%;
  border: 2px solid transparent;
}

.color-dot.active {
  border-color: #1989fa;
  box-shadow: 0 0 0 2px #fff inset;
}

/* 单位字典 chips：横向滚动一行，不挤占表单高度 */
.unit-chips {
  display: flex;
  gap: 6px;
  padding: 8px 16px 0;
  overflow-x: auto;
  white-space: nowrap;
}

.unit-chip {
  flex: 0 0 auto;
  padding: 3px 10px;
  border: 1px solid var(--van-border-color);
  border-radius: 12px;
  font-size: 12px;
  color: var(--van-text-color-2);
}

.unit-chip.active {
  border-color: #1989fa;
  color: #1989fa;
  background: rgba(25, 137, 250, 0.08);
}
</style>
