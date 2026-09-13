<script setup lang="ts">
import { ref, watch } from 'vue'
import { showToast } from 'vant'
import type { Ledger } from '@/types'

interface FormData {
  amount: number
  date: number
  platform: string
  description: string
  notes: string
  person: string
  type: 'income' | 'expense'
}

const props = defineProps<{
  visible: boolean
  editData?: Ledger | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: FormData): void
}>()

function blank(): FormData {
  return {
    amount: 0,
    date: Date.now(),
    platform: '',
    description: '',
    notes: '',
    person: '',
    type: 'expense',
  }
}

const form = ref<FormData>(blank())
const showCalendar = ref(false)

watch(
  () => props.visible,
  (val) => {
    if (val && props.editData) {
      form.value = {
        amount: props.editData.amount,
        date: new Date(props.editData.date).getTime(),
        platform: props.editData.platform,
        description: props.editData.description,
        notes: props.editData.notes,
        person: props.editData.person,
        type: props.editData.type,
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
  form.value.date = date.getTime()
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
  const amount = Number(form.value.amount)
  if (Number.isNaN(amount) || amount <= 0) {
    showToast('请输入正确的金额')
    return
  }
  emit('submit', { ...form.value, amount })
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
        :title="editData ? '编辑账单' : '新增账单'"
        left-text="取消"
        right-text="保存"
        @click-left="close"
        @click-right="submit"
      />
      <div class="form-body">
        <van-cell-group inset>
          <van-field
            v-model="form.amount"
            type="number"
            label="金额"
            placeholder="0.00"
          >
            <template #left-icon><span class="sym">¥</span></template>
          </van-field>

          <van-field name="type" label="类型">
            <template #input>
              <van-radio-group v-model="form.type" direction="horizontal">
                <van-radio name="expense" checked-color="#ee0a24">
                  支出
                </van-radio>
                <van-radio name="income" checked-color="#07c160">
                  收入
                </van-radio>
              </van-radio-group>
            </template>
          </van-field>

          <van-cell
            title="日期"
            is-link
            :value="formatDate(form.date)"
            @click="showCalendar = true"
          />

          <van-field
            v-model="form.platform"
            label="平台"
            placeholder="支付宝/微信/银行等"
          />
          <van-field
            v-model="form.description"
            label="描述"
            placeholder="消费描述"
          />
          <van-field v-model="form.person" label="记账人" placeholder="谁记的" />
          <van-field
            v-model="form.notes"
            rows="2"
            autosize
            type="textarea"
            label="备注"
            placeholder="备注"
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
