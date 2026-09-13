<script setup lang="ts">
import { ref, watch } from 'vue'
import { showToast } from 'vant'
import type { Item } from '@/types'

interface FormModel {
  name: string
  price: number
  quantity: number
  unit: string
  recorder: string
  description: string
  is_expired: boolean
  expire_date: number | null
}

const props = defineProps<{ visible: boolean; item?: Item | null }>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: Record<string, unknown>): void
}>()

function blankForm(): FormModel {
  return {
    name: '',
    price: 0,
    quantity: 0,
    unit: '个',
    recorder: '',
    description: '',
    is_expired: false,
    expire_date: null,
  }
}

const form = ref<FormModel>(blankForm())
const showCalendar = ref(false)

watch(
  () => props.visible,
  (val) => {
    if (val && props.item) {
      form.value = {
        name: props.item.name,
        price: props.item.price,
        quantity: props.item.quantity,
        unit: props.item.unit || '个',
        recorder: props.item.recorder,
        description: props.item.description,
        is_expired: props.item.is_expired,
        expire_date: props.item.expire_date
          ? new Date(props.item.expire_date).getTime()
          : null,
      }
    } else if (val) {
      form.value = blankForm()
    }
  }
)

function close() {
  emit('update:visible', false)
}

function onPick(date: Date) {
  form.value.expire_date = date.getTime()
  showCalendar.value = false
}

function clearExpire() {
  form.value.expire_date = null
}

function pad(n: number) {
  return String(n).padStart(2, '0')
}

function formatDate(ts: number | null): string {
  if (!ts) return ''
  const d = new Date(ts)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function submit() {
  if (!form.value.name.trim()) {
    showToast('请输入名称')
    return
  }
  const data: Record<string, unknown> = {
    name: form.value.name.trim(),
    price: form.value.price,
    quantity: form.value.quantity,
    unit: form.value.unit,
    recorder: form.value.recorder,
    description: form.value.description,
    is_expired: form.value.is_expired,
  }
  if (form.value.expire_date) {
    data.expire_date = new Date(form.value.expire_date).toISOString()
  }
  emit('submit', data)
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
    <div class="form-popup">
      <van-nav-bar
        :title="item ? '编辑物品' : '新增物品'"
        left-text="取消"
        right-text="保存"
        @click-left="close"
        @click-right="submit"
      />
      <div class="form-body">
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            label="名称"
            placeholder="请输入名称"
          />
          <van-field
            v-model="form.price"
            type="number"
            label="价格"
            placeholder="0.00"
          >
            <template #left-icon><span class="price-symbol">¥</span></template>
          </van-field>
          <van-field
            v-model="form.quantity"
            type="number"
            label="库存数量"
            placeholder="0"
          />
          <van-field v-model="form.unit" label="单位" placeholder="请输入单位" />
          <van-field
            v-model="form.recorder"
            label="录入人"
            placeholder="请输入录入人"
          />
          <van-cell
            title="过期时间"
            is-link
            :value="formatDate(form.expire_date) || '请选择'"
            @click="showCalendar = true"
          >
            <template #right-icon>
              <span class="expire-right">
                <van-icon
                  v-if="form.expire_date"
                  name="clear"
                  class="clear-icon"
                  @click.stop="clearExpire"
                />
                <van-icon name="arrow" />
              </span>
            </template>
          </van-cell>
          <van-field
            v-model="form.description"
            rows="2"
            autosize
            type="textarea"
            label="描述"
            placeholder="请输入描述"
          />
          <van-cell title="已过期" center>
            <template #right-icon>
              <van-switch v-model="form.is_expired" size="22" />
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
  </van-popup>

  <van-calendar
    v-model:show="showCalendar"
    :min-date="new Date(2000, 0, 1)"
    :max-date="new Date(2100, 11, 31)"
    @confirm="onPick"
  />
</template>

<style scoped>
.form-popup {
  display: flex;
  flex-direction: column;
  max-height: 78vh;
}

.form-body {
  overflow-y: auto;
  padding-bottom: 24px;
}

.price-symbol {
  margin-right: 4px;
  color: var(--van-text-color-2);
}

.expire-right {
  display: flex;
  align-items: center;
  color: var(--van-text-color-3);
}

.expire-right .clear-icon {
  margin-right: 8px;
  color: var(--van-text-color-2);
}
</style>
