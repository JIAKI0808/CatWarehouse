<script setup lang="ts">
import { ref, watch } from 'vue'
import { showToast } from 'vant'
import { useI18n } from 'vue-i18n'
import { useCurrencyStore } from '@/stores/currency'
import { useUnitStore } from '@/stores/units'
import type { Item } from '@/types'

const currencyStore = useCurrencyStore()
const unitStore = useUnitStore()
const { t } = useI18n()

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
    // 在**建表单时**取默认单位（字典是异步拉的；store 内部在拿不到时退回 `个`）
    unit: unitStore.defaultUnit,
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
        unit: props.item.unit || unitStore.defaultUnit,
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
    showToast(t('app.common.inputName'))
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
        :title="item ? t('app.inventory.editItem') : t('app.inventory.addItem')"
        :left-text="t('app.common.cancel')"
        :right-text="t('app.common.save')"
        @click-left="close"
        @click-right="submit"
      />
      <div class="form-body">
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            :label="t('app.common.name')"
            :placeholder="t('app.common.inputName')"
          />
          <van-field
            v-model="form.price"
            type="number"
            :label="t('app.common.price')"
            placeholder="0.00"
          >
            <template #left-icon>
              <span class="price-symbol">{{ currencyStore.symbol }}</span>
            </template>
          </van-field>
          <van-field
            v-model="form.quantity"
            type="number"
            :label="t('app.common.quantity')"
            placeholder="0"
          />
          <van-field
            v-model="form.unit"
            :label="t('app.common.unit')"
            :placeholder="t('app.common.inputUnit')"
          />
          <!-- 单位字典：字段正下方一行 chips，点一下填入；
               不替换输入框 —— 字典外的单位仍可手打（「选或自由输入」）。 -->
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
            v-model="form.recorder"
            :label="t('app.common.recorder')"
            :placeholder="t('app.common.inputRecorder')"
          />
          <van-cell
            :title="t('app.common.expiresAt')"
            is-link
            :value="formatDate(form.expire_date) || t('app.common.selectPlaceholder')"
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
            :label="t('app.common.description')"
            :placeholder="t('app.common.inputDescription')"
          />
          <van-cell :title="t('app.common.expired')" center>
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
