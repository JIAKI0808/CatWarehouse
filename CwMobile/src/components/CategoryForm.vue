<script setup lang="ts">
import { ref, watch } from 'vue'
import { showToast } from 'vant'
import {
  categoryIconOptions,
  categoryColors,
  getCategoryIcon,
} from '@/utils/categoryIcons'

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
    unit: '个',
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
        unit: props.editData.unit ?? '个',
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
    showToast('请输入名称')
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
      left-text="取消"
      right-text="保存"
      @click-left="close"
      @click-right="submit"
    />
    <div class="cat-body">
      <van-cell-group inset>
        <van-field v-model="form.name" label="名称" placeholder="请输入名称" />
        <van-field
          v-model="form.description"
          rows="2"
          autosize
          type="textarea"
          label="描述"
          placeholder="请输入描述"
        />
        <template v-if="type === 'category'">
          <van-cell title="图标" :border="false" />
          <div class="icon-grid">
            <div
              v-for="icon in categoryIconOptions"
              :key="icon.name"
              class="icon-item"
              :class="{ active: form.icon === icon.name }"
              :title="icon.label"
              @click="form.icon = icon.name"
            >
              <component
                :is="getCategoryIcon(icon.name)"
                :style="{ color: form.icon_color }"
              />
            </div>
          </div>
          <van-cell title="图标颜色" :border="false" />
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
          <van-field v-model="form.unit" label="单位" placeholder="个" />
          <van-field
            v-model="form.notes"
            rows="2"
            autosize
            type="textarea"
            label="备注"
            placeholder="请输入备注"
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
</style>
