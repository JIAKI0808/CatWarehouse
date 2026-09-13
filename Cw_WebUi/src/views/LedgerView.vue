<script setup lang="ts">
import { ref, computed, h, onMounted, watch } from 'vue'
import { NButton, NDataTable, NSelect, NSpace, NModal, NIcon, NPopover, NProgress, NInput } from 'naive-ui'
import { AddOutline, CalendarOutline, ChevronBackOutline, ChevronForwardOutline } from '@vicons/ionicons5'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { useI18n } from 'vue-i18n'
import { useLedgerStore } from '@/stores/ledger'
import { useBudgetStore } from '@/stores/budget'
import LedgerForm from '@/components/LedgerForm.vue'
import type { Ledger, LedgerCreate } from '@/types'

use([CanvasRenderer, BarChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])

const store = useLedgerStore()
const budgetStore = useBudgetStore()
// tm() 取「原始消息」而不是编译后的译文 —— 月份/星期这类**数组**只能这样拿。
const { t, tm } = useI18n()

const showForm = ref(false)
const editingItem = ref<Ledger | null>(null)
const range = ref('month')
const selectedDate = ref(Date.now())
const showCalendar = ref(false)
const showDeleteConfirm = ref(false)
const itemToDelete = ref<number | null>(null)
const searchQuery = ref('')
const filterType = ref('')

const rangeOptions = computed(() => [
  { label: t('app.ledger.scopeDay'), value: 'day' },
  { label: t('app.ledger.scopeWeek'), value: 'week' },
  { label: t('app.ledger.scopeMonth'), value: 'month' },
  { label: t('app.ledger.scopeYear'), value: 'year' },
])

const typeOptions = computed(() => [
  { label: t('app.ledger.typeAll'), value: '' },
  { label: t('app.ledger.typeIncome'), value: 'income' },
  { label: t('app.ledger.typeExpense'), value: 'expense' },
])

const calYear = computed(() => new Date(selectedDate.value).getFullYear())
const calMonth = computed(() => new Date(selectedDate.value).getMonth())

const yearOptions = computed(() => {
  const y = new Date().getFullYear()
  return Array.from({ length: 11 }, (_, i) => ({
    label: t('app.ledger.yearLabel', { year: y - 5 + i }),
    value: y - 5 + i,
  }))
})

const monthOptions = computed(() =>
  (tm('app.ledger.months') as string[]).map((label, value) => ({ label, value }))
)

const weekDays = computed(() => tm('app.ledger.weekdays') as string[])

const calendarDays = computed(() => {
  const y = calYear.value
  const m = calMonth.value
  const firstDay = new Date(y, m, 1).getDay()
  const daysInMonth = new Date(y, m + 1, 0).getDate()
  const days: { day: number; income: number; expense: number; isCurrent: boolean }[] = []

  for (let i = 0; i < firstDay; i++) {
    days.push({ day: 0, income: 0, expense: 0, isCurrent: false })
  }

  const today = new Date()
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const dayItems = store.items.filter(i => i.date.startsWith(dateStr))
    const income = dayItems.filter(i => i.type === 'income').reduce((s, i) => s + i.amount, 0)
    const expense = dayItems.filter(i => i.type === 'expense').reduce((s, i) => s + i.amount, 0)
    const isCurrent = today.getFullYear() === y && today.getMonth() === m && today.getDate() === d
    days.push({ day: d, income, expense, isCurrent })
  }
  return days
})

const dateLabel = computed(() => {
  const d = new Date(selectedDate.value)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
})

const currentMonth = computed(() => {
  const d = new Date(selectedDate.value)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
})

const filteredItems = computed(() => {
  const d = new Date(selectedDate.value)
  return store.items.filter(item => {
    const itemDate = new Date(item.date)
    if (range.value === 'day') {
      return itemDate.toDateString() === d.toDateString()
    }
    if (range.value === 'week') {
      const start = new Date(d)
      start.setDate(d.getDate() - d.getDay())
      const end = new Date(start)
      end.setDate(start.getDate() + 6)
      return itemDate >= start && itemDate <= end
    }
    if (range.value === 'month') {
      return itemDate.getFullYear() === d.getFullYear() && itemDate.getMonth() === d.getMonth()
    }
    return itemDate.getFullYear() === d.getFullYear()
  })
})

const columns = computed(() => [
  { title: t('app.ledger.date'), key: 'date', width: 100, render: (row: Ledger) => new Date(row.date).toLocaleDateString() },
  {
    title: t('app.ledger.type'),
    key: 'type',
    width: 70,
    render: (row: Ledger) =>
      row.type === 'income' ? t('app.ledger.typeIncome') : t('app.ledger.typeExpense'),
  },
  { title: t('app.ledger.amount'), key: 'amount', width: 100, render: (row: Ledger) => `¥${row.amount.toFixed(2)}` },
  { title: t('app.ledger.platform'), key: 'platform', width: 100 },
  { title: t('app.common.description'), key: 'description', width: 150 },
  { title: t('app.ledger.person'), key: 'person', width: 80 },
  {
    title: t('app.common.actions'), key: 'actions', width: 120,
    render: (row: Ledger) => {
      return h('div', { class: 'flex gap-1' }, [
        h(NButton, { size: 'tiny', onClick: () => handleEdit(row) }, () => t('app.common.edit')),
        h(NButton, { size: 'tiny', type: 'error', onClick: () => handleDelete(row.id) }, () => t('app.common.remove')),
      ])
    },
  },
])

onMounted(() => {
  store.fetchAll()
  store.fetchStats(range.value)
  budgetStore.fetchAll(currentMonth.value)
})

watch(range, (val) => store.fetchStats(val))

watch([searchQuery, filterType], () => {
  store.fetchAll({
    q: searchQuery.value || undefined,
    type: filterType.value || undefined,
  })
})

function changeMonth(delta: number) {
  const d = new Date(selectedDate.value)
  d.setMonth(d.getMonth() + delta)
  selectedDate.value = d.getTime()
}

function setMonth(m: number) {
  const d = new Date(selectedDate.value)
  d.setMonth(m)
  selectedDate.value = d.getTime()
}

function setYear(y: number) {
  const d = new Date(selectedDate.value)
  d.setFullYear(y)
  selectedDate.value = d.getTime()
}

function selectDay(day: number) {
  if (day === 0) return
  const d = new Date(calYear.value, calMonth.value, day)
  selectedDate.value = d.getTime()
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

function handleDelete(id: number) {
  itemToDelete.value = id
  showDeleteConfirm.value = true
}

async function handleDeleteConfirm() {
  if (itemToDelete.value) {
    await store.remove(itemToDelete.value)
    showDeleteConfirm.value = false
    itemToDelete.value = null
    store.fetchStats(range.value)
  }
}

async function handleSubmit(data: LedgerCreate) {
  if (editingItem.value) {
    await store.update(editingItem.value.id, data)
  } else {
    await store.create(data)
  }
  store.fetchStats(range.value)
}

function getChartOption() {
  return {
    title: { text: t('app.ledger.chartTitle'), left: 'center', top: 10 },
    tooltip: { trigger: 'axis' },
    legend: { top: 45 },
    grid: { left: '12%', right: '12%', bottom: '18%', top: '80px' },
    xAxis: {
      type: 'category',
      data: store.stats.map(s => s.period),
      axisLabel: { margin: 15 },
    },
    yAxis: { type: 'value', name: t('app.ledger.chartAmountAxis'), nameGap: 20 },
    series: [
      { name: t('app.ledger.typeIncome'), type: 'bar', data: store.stats.map(s => s.income), itemStyle: { color: '#10b981' }, barGap: '20%' },
      { name: t('app.ledger.typeExpense'), type: 'bar', data: store.stats.map(s => s.expense), itemStyle: { color: '#ef4444' } },
    ],
  }
}
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">{{ t('app.ledger.title') }}</h1>
      <NSpace>
        <NPopover v-model:show="showCalendar" trigger="click" placement="bottom">
          <template #trigger>
            <NButton>
              <template #icon><NIcon><CalendarOutline /></NIcon></template>
              {{ dateLabel }}
            </NButton>
          </template>
          <div class="cal-popup">
            <div class="cal-header">
              <NSelect :value="calYear" :options="yearOptions" size="tiny" style="width: 90px" @update:value="setYear" />
              <NSelect :value="calMonth" :options="monthOptions" size="tiny" style="width: 70px" @update:value="setMonth" />
              <div class="cal-nav">
                <NButton size="tiny" quaternary @click="changeMonth(-1)"><NIcon :size="14"><ChevronBackOutline /></NIcon></NButton>
                <NButton size="tiny" quaternary @click="changeMonth(1)"><NIcon :size="14"><ChevronForwardOutline /></NIcon></NButton>
              </div>
            </div>
            <div class="cal-weekdays">
              <div v-for="w in weekDays" :key="w" class="cal-wd">{{ w }}</div>
            </div>
            <div class="cal-grid">
              <div
                v-for="(d, i) in calendarDays"
                :key="i"
                class="cal-cell"
                :class="{ 'cal-empty': d.day === 0, 'cal-today': d.isCurrent }"
                @click="selectDay(d.day)"
              >
                <template v-if="d.day > 0">
                  <div class="cal-day">{{ d.day }}</div>
                  <div v-if="d.income > 0" class="cal-income">+{{ d.income.toFixed(0) }}</div>
                  <div v-if="d.expense > 0" class="cal-expense">-{{ d.expense.toFixed(0) }}</div>
                </template>
              </div>
            </div>
          </div>
        </NPopover>
        <NSelect v-model:value="range" :options="rangeOptions" style="width: 120px" />
        <NButton type="primary" @click="handleAdd">
          <template #icon><NIcon><AddOutline /></NIcon></template>
          {{ t('app.ledger.create') }}
        </NButton>
      </NSpace>
    </div>

    <VChart :option="getChartOption()" style="height: 300px" />

    <div v-if="budgetStore.items.length > 0" class="space-y-3">
      <h3 class="text-sm font-semibold text-gray-600">{{ t('app.ledger.budgetOverview') }}</h3>
      <div v-for="b in budgetStore.items" :key="b.id" class="flex items-center gap-4">
        <span class="w-24 text-sm truncate">{{ b.category_name }}</span>
        <NProgress
          type="line"
          :percentage="Math.min((b.spent / b.amount) * 100, 100)"
          :status="b.spent > b.amount ? 'error' : 'success'"
          :show-indicator="true"
          style="flex: 1"
        />
        <span class="w-20 text-xs text-right">¥{{ b.spent.toFixed(0) }} / ¥{{ b.amount.toFixed(0) }}</span>
      </div>
    </div>

    <div class="flex gap-4 items-center">
      <NInput
        v-model:value="searchQuery"
        :placeholder="t('app.ledger.searchPlaceholder')"
        clearable
        style="width: 250px"
      />
      <NSelect v-model:value="filterType" :options="typeOptions" style="width: 120px" />
    </div>

    <NDataTable :columns="columns" :data="filteredItems" :loading="store.loading" />

    <LedgerForm
      v-model:visible="showForm"
      :edit-data="editingItem"
      @submit="handleSubmit"
    />

    <NModal
      v-model:show="showDeleteConfirm"
      preset="dialog"
      :title="t('app.inventory.confirmDeleteTitle')"
      :content="t('app.ledger.deleteConfirm')"
      :positive-text="t('app.common.remove')"
      :negative-text="t('app.common.cancel')"
      type="error"
      @positive-click="handleDeleteConfirm"
      @negative-click="showDeleteConfirm = false"
    />
  </div>
</template>

<style scoped>
.cal-popup { width: 280px; }
.cal-header { display: flex; align-items: center; gap: 4px; margin-bottom: 8px; }
.cal-nav { display: flex; gap: 0; margin-left: auto; }
.cal-weekdays { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-size: 11px; color: #999; margin-bottom: 4px; }
.cal-wd { padding: 2px 0; }
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 1px; }
.cal-cell { min-height: 36px; padding: 2px; border-radius: 4px; cursor: pointer; text-align: center; font-size: 11px; line-height: 1.2; }
.cal-cell:hover:not(.cal-empty) { background: #f5f5f5; }
.cal-empty { cursor: default; }
.cal-today { background: #e6f7ff; }
.cal-day { font-size: 12px; font-weight: 500; }
.cal-income { color: #10b981; font-size: 10px; }
.cal-expense { color: #ef4444; font-size: 10px; }
</style>
