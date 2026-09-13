<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { showConfirmDialog } from 'vant'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from 'echarts/components'
import { useI18n } from 'vue-i18n'
import { useLedgerStore } from '@/stores/ledger'
import { useBudgetStore } from '@/stores/budget'
import { useThemeStore } from '@/stores/theme'
import type { Ledger, LedgerCreate, LedgerUpdate } from '@/types'
import LedgerForm from '@/components/LedgerForm.vue'

use([CanvasRenderer, BarChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])

const store = useLedgerStore()
const budgetStore = useBudgetStore()
const themeStore = useThemeStore()

const showForm = ref(false)
const editingItem = ref<Ledger | null>(null)
const range = ref('month')
const selectedDate = ref(Date.now())
const showCalendar = ref(false)
const searchQuery = ref('')
const filterType = ref('')

const { t } = useI18n()

const rangeOptions = computed(() => [
  { label: t('app.ledger.scopeDay'), value: 'day' },
  { label: t('app.ledger.scopeWeek'), value: 'week' },
  { label: t('app.ledger.scopeMonth'), value: 'month' },
  { label: t('app.ledger.scopeYear'), value: 'year' },
])

const currentMonth = computed(() => {
  const d = new Date(selectedDate.value)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
})

const dateLabel = computed(() => {
  const d = new Date(selectedDate.value)
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
})

const daySummary = computed(() => {
  const map: Record<string, { income: number; expense: number }> = {}
  for (const i of store.items) {
    const key = i.date.slice(0, 10)
    const e = map[key] ?? (map[key] = { income: 0, expense: 0 })
    if (i.type === 'income') e.income += i.amount
    else e.expense += i.amount
  }
  return map
})

function calendarFormatter(item: { date?: Date }) {
  const day = item.date
  if (!day) return {}
  const mm = String(day.getMonth() + 1).padStart(2, '0')
  const dd = String(day.getDate()).padStart(2, '0')
  const key = `${day.getFullYear()}-${mm}-${dd}`
  const s = daySummary.value[key]
  if (!s) return {}
  const parts: string[] = []
  if (s.income) parts.push(`+${s.income.toFixed(0)}`)
  if (s.expense) parts.push(`-${s.expense.toFixed(0)}`)
  return { bottomInfo: parts.join(' ') }
}

const filteredItems = computed(() => {
  const base = new Date(selectedDate.value)
  return store.items.filter((item) => {
    const d = new Date(item.date)
    if (range.value === 'day') return d.toDateString() === base.toDateString()
    if (range.value === 'week') {
      const start = new Date(base)
      start.setDate(base.getDate() - base.getDay())
      const end = new Date(start)
      end.setDate(start.getDate() + 6)
      return d >= start && d <= end
    }
    if (range.value === 'month') {
      return (
        d.getFullYear() === base.getFullYear() &&
        d.getMonth() === base.getMonth()
      )
    }
    return d.getFullYear() === base.getFullYear()
  })
})

onMounted(() => {
  store.fetchAll()
  store.fetchStats(range.value)
  budgetStore.fetchAll(currentMonth.value)
})

watch(range, (val) => store.fetchStats(val))
watch(currentMonth, (month) => budgetStore.fetchAll(month))
watch([searchQuery, filterType], () => {
  store.fetchAll({
    q: searchQuery.value || undefined,
    type: filterType.value || undefined,
  })
})

function navMonth(delta: number) {
  const d = new Date(selectedDate.value)
  d.setMonth(d.getMonth() + delta)
  selectedDate.value = d.getTime()
}

function openCalendar() {
  showCalendar.value = true
}

function onCalendarConfirm(date: Date) {
  selectedDate.value = date.getTime()
  showCalendar.value = false
}

function handleAdd() {
  editingItem.value = null
  showForm.value = true
}

function handleEdit(item: Ledger) {
  editingItem.value = item
  showForm.value = true
}

async function askDelete(item: Ledger) {
  try {
    await showConfirmDialog({
      title: t('app.ledger.deleteTitle'),
      message: t('app.ledger.deleteConfirm'),
      confirmButtonText: t('app.common.remove'),
      confirmButtonColor: '#ee0a24',
    })
  } catch {
    return
  }
  await store.remove(item.id)
  store.fetchStats(range.value)
}

async function handleSubmit(data: {
  amount: number
  date: number
  platform: string
  description: string
  notes: string
  person: string
  type: 'income' | 'expense'
}) {
  if (editingItem.value) {
    await store.update(
      editingItem.value.id,
      data as unknown as LedgerUpdate
    )
  } else {
    await store.create(data as unknown as LedgerCreate)
  }
  store.fetchStats(range.value)
}

function chartPalette() {
  return {
    text: themeStore.isDark ? '#d8d8dd' : '#666',
    line: themeStore.isDark ? '#3a3a3d' : '#e2e2e2',
    split: themeStore.isDark ? '#2a2a2d' : '#f2f3f5',
  }
}

function getChartOption() {
  const p = chartPalette()
  return {
    title: {
      text: t('app.ledger.chartTitle'),
      left: 'center',
      textStyle: { fontSize: 14, color: p.text },
    },
    tooltip: { trigger: 'axis' },
    legend: { top: 30, textStyle: { color: p.text } },
    grid: { left: '12%', right: '6%', bottom: '12%', top: '80px' },
    xAxis: {
      type: 'category',
      data: store.stats.map((s) => s.period),
      axisLabel: { color: p.text, fontSize: 10 },
      axisLine: { lineStyle: { color: p.line } },
    },
    yAxis: {
      type: 'value',
      name: t('app.ledger.chartAmountAxis'),
      nameTextStyle: { color: p.text, fontSize: 10 },
      axisLabel: { color: p.text, fontSize: 10 },
      splitLine: { lineStyle: { color: p.split } },
    },
    series: [
      {
        name: t('app.ledger.typeIncome'),
        type: 'bar',
        data: store.stats.map((s) => s.income),
        itemStyle: { color: '#10b981' },
        barGap: '20%',
      },
      {
        name: t('app.ledger.typeExpense'),
        type: 'bar',
        data: store.stats.map((s) => s.expense),
        itemStyle: { color: '#ef4444' },
      },
    ],
  }
}

function shortDate(s: string): string {
  return new Date(s).toLocaleDateString()
}

// 形参改名 `kind`：原来叫 `t`，会把 i18n 的 `t` 遮住，改完就取不到译文了。
function typeTag(kind: string): string {
  return kind === 'income' ? t('app.ledger.typeIncome') : t('app.ledger.typeExpense')
}
</script>

<template>
  <div class="ledger">
    <van-nav-bar :title="t('app.ledger.title')">
      <template #right>
        <van-icon name="plus" class="plus" @click="handleAdd" />
      </template>
    </van-nav-bar>

    <div class="page-body">
    <div class="range-row">
      <van-icon name="arrow-left" class="arrow" @click="navMonth(-1)" />
      <div class="date-label" @click="openCalendar">
        {{ dateLabel }} <van-icon name="arrow-down" size="12" color="var(--van-text-color-2)" />
      </div>
      <van-icon name="arrow" class="arrow" @click="navMonth(1)" />
    </div>

    <van-tabs
      v-model:active="range"
      shrink
      class="range-tabs"
      @change="store.fetchStats(range)"
    >
      <van-tab
        v-for="r in rangeOptions"
        :key="r.value"
        :name="r.value"
        :title="r.label"
      />
    </van-tabs>

    <div v-if="store.stats.length" class="chart-card">
      <VChart :option="getChartOption()" autoresize class="chart" />
    </div>

    <div v-if="budgetStore.items.length" class="budget">
      <div class="budget-title">{{ t('app.ledger.budgetOverview') }}</div>
      <div v-for="b in budgetStore.items" :key="b.id" class="budget-row">
        <span class="b-name">{{ b.category_name }}</span>
        <van-progress
          :percentage="Math.min(Math.round((b.spent / b.amount) * 100), 100)"
          :color="b.spent > b.amount ? '#ee0a24' : '#07c160'"
          :stroke-width="6"
          :show-pivot="false"
          class="b-bar"
        />
        <span class="b-num">
          ¥{{ b.spent.toFixed(0) }} / ¥{{ b.amount.toFixed(0) }}
        </span>
      </div>
    </div>

    <div class="toolbar">
      <van-field
        v-model="searchQuery"
        clearable
        :placeholder="t('app.ledger.searchPlaceholder')"
        class="search"
      />
      <div class="type-chips">
        <van-tag
          round
          :color="filterType === '' ? '#1989fa' : 'transparent'"
          :text-color="filterType === '' ? '#fff' : '#646566'"
          :plain="filterType !== ''"
          class="chip"
          @click="filterType = ''"
        >
          {{ t('app.ledger.typeAll') }}
        </van-tag>
        <van-tag
          round
          :color="filterType === 'income' ? '#07c160' : 'transparent'"
          :text-color="filterType === 'income' ? '#fff' : '#646566'"
          :plain="filterType !== 'income'"
          class="chip"
          @click="filterType = 'income'"
        >
          {{ t('app.ledger.typeIncome') }}
        </van-tag>
        <van-tag
          round
          :color="filterType === 'expense' ? '#ee0a24' : 'transparent'"
          :text-color="filterType === 'expense' ? '#fff' : '#646566'"
          :plain="filterType !== 'expense'"
          class="chip"
          @click="filterType = 'expense'"
        >
          {{ t('app.ledger.typeExpense') }}
        </van-tag>
      </div>
    </div>

    <div class="list">
      <van-empty
        v-if="!store.loading && !filteredItems.length"
        :description="t('app.ledger.noEntries')"
      />
      <div v-else class="ledger-cards">
        <van-swipe-cell
          v-for="item in filteredItems"
          :key="item.id"
          class="card-swipe"
        >
          <van-cell
            :title="item.description || item.platform || t('app.ledger.unnamed')"
            :label="`${shortDate(item.date)} · ${item.platform || '-'} · ${item.person || '-'}`"
            clickable
            @click="handleEdit(item)"
          >
            <template #icon>
              <van-tag
                :type="item.type === 'income' ? 'success' : 'danger'"
                class="type-tag"
              >
                {{ typeTag(item.type) }}
              </van-tag>
            </template>
            <template #value>
              <span
                class="amount"
                :class="item.type === 'income' ? 'in' : 'out'"
              >
                {{ item.type === 'income' ? '+' : '-' }}¥{{ item.amount.toFixed(2) }}
              </span>
            </template>
          </van-cell>
          <template #right>
            <van-button
              square
              type="danger"
              :text="t('app.common.remove')"
              class="del-btn"
              @click="askDelete(item)"
            />
          </template>
        </van-swipe-cell>
      </div>
    </div>
    </div>

    <LedgerForm
      v-model:visible="showForm"
      :edit-data="editingItem"
      @submit="handleSubmit"
    />

    <van-calendar
      v-model:show="showCalendar"
      :default-date="new Date(selectedDate)"
      :min-date="new Date(2000, 0, 1)"
      :max-date="new Date(2100, 11, 31)"
      :formatter="calendarFormatter"
      @confirm="onCalendarConfirm"
    />
  </div>
</template>

<style scoped>
.ledger {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 12px var(--tabbar-height);
}

.plus {
  font-size: 22px;
  color: var(--van-primary-color);
}

.range-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin: 10px 0 0;
}

.arrow {
  font-size: 16px;
  color: var(--van-text-color-2);
  padding: 6px;
}

.date-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 16px;
  font-weight: 600;
}

.range-tabs {
  margin: 6px 0 2px;
}

.chart-card {
  margin-top: 8px;
  background: var(--van-background-2);
  border-radius: 10px;
  padding: 8px 4px 4px;
}

.chart {
  height: 220px;
}

.budget {
  margin-top: 10px;
  background: var(--van-background-2);
  border-radius: 10px;
  padding: 10px 12px;
}

.budget-title {
  font-size: 13px;
  color: var(--van-text-color-2);
  margin-bottom: 8px;
}

.budget-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.b-name {
  width: 72px;
  font-size: 13px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.b-bar {
  flex: 1;
}

.b-num {
  width: 92px;
  text-align: right;
  font-size: 11px;
  color: var(--van-text-color-2);
}

.toolbar {
  margin: 12px 0 4px;
}

.search {
  margin-bottom: 8px;
}

.type-chips {
  display: flex;
  gap: 8px;
}

.chip {
  padding: 6px 12px;
  border: 1px solid var(--van-border-color);
}

.list {
  margin-top: 8px;
}

.type-tag {
  margin-right: 10px;
}

.ledger-cards {
  padding: 0 12px;
}

.card-swipe {
  margin-bottom: 8px;
  border-radius: 10px;
  overflow: hidden;
}

.del-btn {
  height: 100%;
}

.amount {
  font-weight: 600;
  font-size: 14px;
}

.in {
  color: var(--van-success-color);
}

.out {
  color: var(--van-danger-color);
}

</style>
