<script setup lang="ts">
import { ref, watch } from 'vue'
import { showToast } from 'vant'
import { useI18n } from 'vue-i18n'
import type { Pricing } from '@/types'

const { t } = useI18n()

export interface PricingFormData {
  name: string
  cost: number
  suggested_price: number
  discount: number
  description: string
  notes: string
  record_date: number
}

const props = defineProps<{
  visible: boolean
  editData?: Pricing | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: PricingFormData): void
}>()

function blank(): PricingFormData {
  return {
    name: '',
    cost: 0,
    suggested_price: 0,
    discount: 1,
    description: '',
    notes: '',
    record_date: Date.now(),
  }
}

const form = ref<PricingFormData>(blank())
const showCalendar = ref(false)

watch(
  () => props.visible,
  (val) => {
    if (val && props.editData) {
      form.value = {
        name: props.editData.name,
        cost: props.editData.cost,
        suggested_price: props.editData.suggested_price,
        discount: props.editData.discount,
        description: props.editData.description,
        notes: props.editData.notes,
        record_date: props.editData.record_date
          ? new Date(props.editData.record_date).getTime()
          : Date.now(),
      }
    } else if (val) {
      form.value = blank()
    }
  }
)

function close() {
  emit('update:visible', false)
}

function onPick(date: Date) {
  form.value.record_date = date.getTime()
  showCalendar.value = false
}

function pad(n: number) {
  return String(n).padStart(2, '0')
}

function formatDate(ts: number): string {
  const d = new Date(ts)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function submit() {
  if (!form.value.name.trim()) {
    showToast(t('app.pricing.inputProductName'))
    return
  }
  emit('submit', {
    ...form.value,
    name: form.value.name.trim(),
    cost: Number(form.value.cost),
    suggested_price: Number(form.value.suggested_price),
    discount: Number(form.value.discount),
  })
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
        :title="editData ? t('app.pricing.editPricing') : t('app.pricing.addPricing')"
        :left-text="t('app.common.cancel')"
        :right-text="t('app.common.save')"
        @click-left="close"
        @click-right="submit"
      />
      <div class="form-body">
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            :label="t('app.pricing.productName')"
            :placeholder="t('app.pricing.inputProductName')"
          />
          <van-field
            v-model="form.cost"
            type="number"
            :label="t('app.pricing.cost')"
            placeholder="0.00"
          >
            <template #left-icon><span class="sym">¥</span></template>
          </van-field>
          <van-field
            v-model="form.suggested_price"
            type="number"
            :label="t('app.pricing.suggestedPrice')"
            placeholder="0.00"
          >
            <template #left-icon><span class="sym">¥</span></template>
          </van-field>
          <van-field
            v-model="form.discount"
            type="number"
            :label="t('app.pricing.discount')"
            placeholder="1.0"
          />
          <van-field
            v-model="form.description"
            rows="2"
            autosize
            type="textarea"
            :label="t('app.common.description')"
            :placeholder="t('app.common.inputDescription')"
          />
          <van-field
            v-model="form.notes"
            rows="2"
            autosize
            type="textarea"
            :label="t('app.common.notes')"
            :placeholder="t('app.common.inputNotes')"
          />
          <van-cell
            :title="t('app.pricing.recordDate')"
            is-link
            :value="formatDate(form.record_date)"
            @click="showCalendar = true"
          />
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

.sym {
  margin-right: 4px;
  color: var(--van-text-color-2);
}
</style>
