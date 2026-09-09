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
const calYear = ref(new Date().getFullYear())
const calMonth = ref(new Date().getMonth())

const rangeOptions = [
  { label: '按天', value: 'day' },
  { label: '按周', value: 'week' },
  { label: '按月', value: 'month' },
  { label: '按年', value: 'year' },
]

const weekDays = ['日', '一', '二', '三', '四', '五', '六']

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

interface CalDay {
  day: number
  income: number
  expense: number
  isCurrent: boolean
}

const calendarDays = computed<CalDay[]>(() => {
  const y = calYear.value
  const m = calMonth.value
  const firstDay = new Date(y, m, 1).getDay()
  const daysInMonth = new Date(y, m + 1, 0).getDate()
  const cells: CalDay[] = []
  for (let i = 0; i < firstDay; i++) {
    cells.push({ day: 0, income: 0, expense: 0, isCurrent: false })
  }
  const today = new Date()
  for (let d = 1; d <= daysInMonth; d++) {
    const prefix = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const dayItems = store.items.filter((i) => i.date.startsWith(prefix))
    const income = dayItems
      .filter((i) => i.type === 'income')
      .reduce((s, i) => s + i.amount, 0)
    const expense = dayItems
      .filter((i) => i.type === 'expense')
      .reduce((s, i) => s + i.amount, 0)
    const isCurrent =
      today.getFullYear() === y && today.getMonth() === m && today.getDate() === d
    cells.push({ day: d, income, expense, isCurrent })
  }
  return cells
})

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
  syncCalendar()
})

watch(range, (val) => store.fetchStats(val))
watch(currentMonth, (month) => budgetStore.fetchAll(month))
watch([searchQuery, filterType], () => {
  store.fetchAll({
    q: searchQuery.value || undefined,
    type: filterType.value || undefined,
  })
})

function syncCalendar() {
  const d = new Date(selectedDate.value)
  calYear.value = d.getFullYear()
  calMonth.value = d.getMonth()
}

function navMonth(delta: number) {
  const d = new Date(selectedDate.value)
  d.setMonth(d.getMonth() + delta)
  selectedDate.value = d.getTime()
  syncCalendar()
}

function selectDay(day: number) {
  if (day === 0) return
  const d = new Date(calYear.value, calMonth.value, day)
  selectedDate.value = d.getTime()
  showCalendar.value = false
}

function openCalendar() {
  syncCalendar()
  showCalendar.value = true
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
      title: '删除账单',
      message: '确定要删除这条账单吗？',
      confirmButtonText: '删除',
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
    title: { text: '收支统计', left: 'center', textStyle: { fontSize: 14, color: p.text } },
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
      name: '金额 (¥)',
      nameTextStyle: { color: p.text, fontSize: 10 },
      axisLabel: { color: p.text, fontSize: 10 },
      splitLine: { lineStyle: { color: p.split } },
    },
    series: [
      { name: '收入', type: 'bar', data: store.stats.map((s) => s.income), itemStyle: { color: '#10b981' }, barGap: '20%' },
      { name: '支出', type: 'bar', data: store.stats.map((s) => s.expense), itemStyle: { color: '#ef4444' } },
    ],
  }
}

function shortDate(s: string): string {
  return new Date(s).toLocaleDateString()
}

function typeTag(t: string): string {
  return t === 'income' ? '收入' : '支出'
}
</script>

<template>
  <div class="ledger">
    <div class="ledger-head">
      <div class="ledger-title">账本</div>
      <van-icon name="plus" class="plus" @click="handleAdd" />
    </div>

    <div class="range-row">
      <van-icon name="arrow-left" class="arrow" @click="navMonth(-1)" />
      <div class="date-label" @click="openCalendar">
        {{ dateLabel }} <van-icon name="arrow-down" size="12" color="#969799" />
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
      <div class="budget-title">预算概览</div>
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
        placeholder="搜索描述/平台/记账人"
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
          全部
        </van-tag>
        <van-tag
          round
          :color="filterType === 'income' ? '#07c160' : 'transparent'"
          :text-color="filterType === 'income' ? '#fff' : '#646566'"
          :plain="filterType !== 'income'"
          class="chip"
          @click="filterType = 'income'"
        >
          收入
        </van-tag>
        <van-tag
          round
          :color="filterType === 'expense' ? '#ee0a24' : 'transparent'"
          :text-color="filterType === 'expense' ? '#fff' : '#646566'"
          :plain="filterType !== 'expense'"
          class="chip"
          @click="filterType = 'expense'"
        >
          支出
        </van-tag>
      </div>
    </div>

    <div class="list">
      <van-empty
        v-if="!store.loading && !filteredItems.length"
        description="暂无账单记录"
      />
      <van-cell-group v-else inset>
        <van-cell
          v-for="item in filteredItems"
          :key="item.id"
          :title="item.description || item.platform || '未命名'"
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
            <div class="amount-wrap">
              <span
                class="amount"
                :class="item.type === 'income' ? 'in' : 'out'"
              >
                {{ item.type === 'income' ? '+' : '-' }}¥{{ item.amount.toFixed(2) }}
              </span>
              <van-icon
                name="delete-o"
                class="del"
                @click.stop="askDelete(item)"
              />
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <LedgerForm
      v-model:visible="showForm"
      :edit-data="editingItem"
      @submit="handleSubmit"
    />

    <van-popup v-model:show="showCalendar" position="bottom" round>
      <div class="cal">
        <div class="cal-head">
          <div class="cal-nav">
            <van-icon name="arrow-left" class="arrow" @click="calMonth--" />
            <span class="cal-month-label">
              {{ calYear }} 年 {{ calMonth + 1 }} 月
            </span>
            <van-icon name="arrow" class="arrow" @click="calMonth++" />
          </div>
          <div class="cal-weekdays">
            <div v-for="w in weekDays" :key="w" class="cal-wd">{{ w }}</div>
          </div>
          <div class="cal-grid">
            <div
              v-for="(d, i) in calendarDays"
              :key="i"
              class="cal-cell"
              :class="{ empty: d.day === 0, today: d.isCurrent }"
              @click="selectDay(d.day)"
            >
              <template v-if="d.day > 0">
                <div class="cal-day">{{ d.day }}</div>
                <div v-if="d.income > 0" class="cal-income">+{{ d.income.toFixed(0) }}</div>
                <div v-if="d.expense > 0" class="cal-expense">-{{ d.expense.toFixed(0) }}</div>
              </template>
            </div>
          </div>
          <van-button block plain type="primary" @click="showCalendar = false">
            完成
          </van-button>
          <div class="pad" />
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.ledger {
  padding: 12px 12px 90px;
}

.ledger-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ledger-title {
  font-size: 20px;
  font-weight: 700;
}

.plus {
  font-size: 22px;
  color: #1989fa;
  padding: 4px;
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
  color: #969799;
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
  background: #fff;
  border-radius: 10px;
  padding: 8px 4px 4px;
}

html.dark .chart-card {
  background: #1c1c1e;
}

.chart {
  height: 220px;
}

.budget {
  margin-top: 10px;
  background: #fff;
  border-radius: 10px;
  padding: 10px 12px;
}

html.dark .budget {
  background: #1c1c1e;
}

.budget-title {
  font-size: 13px;
  color: #969799;
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
  color: #969799;
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
  border: 1px solid #e2e2e2;
}

html.dark .chip {
  border-color: #3a3a3d;
}

.list {
  margin-top: 8px;
}

.type-tag {
  margin-right: 10px;
}

.amount-wrap {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.amount {
  font-weight: 600;
  font-size: 14px;
}

.in {
  color: #07c160;
}

.out {
  color: #ee0a24;
}

.del {
  color: #c8c9cc;
  font-size: 17px;
}

.cal {
  padding: 16px 14px 0;
}

.cal-head {
  text-align: center;
}

.cal-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  margin-bottom: 10px;
}

.cal-month-label {
  font-weight: 600;
  min-width: 110px;
}

.cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  font-size: 12px;
  color: #969799;
}

.cal-wd {
  padding: 4px 0;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-bottom: 12px;
}

.cal-cell {
  min-height: 52px;
  padding: 2px;
  text-align: center;
  font-size: 11px;
  line-height: 1.15;
  border-radius: 4px;
}

.cal-cell:not(.empty) {
  cursor: pointer;
}

.cal-cell:not(.empty):active {
  background: #f2f3f5;
}

.cal-day {
  font-size: 13px;
  font-weight: 500;
}

.cal-income {
  color: #07c160;
  font-size: 9px;
  overflow: hidden;
}

.cal-expense {
  color: #ee0a24;
  font-size: 9px;
  overflow: hidden;
}

.cal-cell.today {
  background: #e6f7ff;
}

html.dark .cal-cell.today {
  background: rgba(25, 137, 250, 0.15);
}

.pad {
  height: 16px;
}
</style>
