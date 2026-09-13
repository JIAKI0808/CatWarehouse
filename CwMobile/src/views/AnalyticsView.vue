<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import { useI18n } from 'vue-i18n'
import { useCurrencyStore } from '@/stores/currency'

const currencyStore = useCurrencyStore()
const { t } = useI18n()
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from 'echarts/components'
import { useCategoryStore } from '@/stores/category'
import { useSubCategoryStore } from '@/stores/subCategory'
import { useThemeStore } from '@/stores/theme'
import { analyticsApi } from '@/services/api'
import CascaderPicker from '@/components/CascaderPicker.vue'
import type {
  TrendData,
  AnalyticsOverview,
  CategoryStat,
  MonthlyCompare,
} from '@/types'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
])

const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()
const themeStore = useThemeStore()

const selectedCategoryId = ref<number | null>(null)
const selectedSubCategoryId = ref<number | null>(null)
const trendData = ref<TrendData | null>(null)
const overview = ref<AnalyticsOverview | null>(null)
const categoryStats = ref<CategoryStat[]>([])
const monthlyCompare = ref<MonthlyCompare[]>([])
const loading = ref(false)

const showPicker = ref(false)
const trendTab = ref('trend')

const dark = () => themeStore.isDark
function chartPalette() {
  return {
    text: dark() ? '#d8d8dd' : '#666',
    line: dark() ? '#3a3a3d' : '#e2e2e2',
    split: dark() ? '#2a2a2d' : '#f2f3f5',
  }
}

const pickerCategories = computed(() =>
  categoryStore.categories.map((c) => ({ text: c.name, value: c.id }))
)

function pickerSubsOf(catId: number) {
  return (subCategoryStore.subCategoriesByCategory[catId] ?? []).map((s) => ({
    text: s.name,
    value: s.id,
  }))
}

const selectionLabel = computed(() => {
  const cat = categoryStore.categories.find((c) => c.id === selectedCategoryId.value)
  const list = selectedCategoryId.value
    ? (subCategoryStore.subCategoriesByCategory[selectedCategoryId.value] ?? [])
    : []
  const sub = list.find((s) => s.id === selectedSubCategoryId.value)
  if (cat && sub) return `${cat.name} / ${sub.name}`
  if (cat) return cat.name
  return t('app.analytics.pickCategory')
})

const hasData = computed(
  () => !!trendData.value && trendData.value.data.length > 0
)

onMounted(async () => {
  categoryStore.fetchAll()
  try {
    const [o, cs, mc] = await Promise.all([
      analyticsApi.getOverview(),
      analyticsApi.getCategoryStats(),
      analyticsApi.getMonthlyCompare(),
    ])
    overview.value = o
    categoryStats.value = cs
    monthlyCompare.value = mc
  } catch {
    /* 概览加载失败保持空 */
  }
})

watch(selectedSubCategoryId, async (id) => {
  if (!id) {
    trendData.value = null
    return
  }
  loading.value = true
  try {
    trendData.value = await analyticsApi.getTrend(id)
  } catch {
    trendData.value = null
  } finally {
    loading.value = false
  }
})

async function openPicker() {
  await Promise.all(
    categoryStore.categories.map((c) => subCategoryStore.fetchByCategory(c.id))
  )
  showPicker.value = true
}

function onPickerConfirm(r: { categoryId: number; subId: number | null }) {
  selectedCategoryId.value = r.categoryId
  selectedSubCategoryId.value = r.subId
}

function baseGrid() {
  return { left: '12%', right: '6%', bottom: '12%', top: '16%' }
}

function titled(text: string) {
  return { text, left: 'center', textStyle: { fontSize: 13 } }
}

function xAxis(data: string[]) {
  const p = chartPalette()
  return {
    type: 'category',
    data,
    axisLabel: { color: p.text, fontSize: 10 },
    axisLine: { lineStyle: { color: p.line } },
  }
}

function yAxis(name: string) {
  const p = chartPalette()
  return {
    type: 'value',
    name,
    nameTextStyle: { color: p.text, fontSize: 10 },
    axisLabel: { color: p.text, fontSize: 10 },
    splitLine: { lineStyle: { color: p.split } },
  }
}

function lineSerie(name: string, data: number[], color: string) {
  return {
    name,
    type: 'line',
    data,
    smooth: true,
    areaStyle: { opacity: 0.3 },
    itemStyle: { color },
  }
}

function quantityLineOption() {
  if (!trendData.value) return {}
  const d = trendData.value.data
  return {
    title: titled(t('app.analytics.chart.quantityTrend')),
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: xAxis(d.map((t) => t.date)),
    yAxis: yAxis(t('app.analytics.axis.quantity', { unit: trendData.value.unit })),
    series: [
      lineSerie(t('app.analytics.metric.quantity'), d.map((t) => t.quantity), '#1989fa'),
    ],
  }
}

function priceLineOption() {
  if (!trendData.value) return {}
  const d = trendData.value.data
  return {
    title: titled(t('app.analytics.chart.priceTrend')),
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: xAxis(d.map((t) => t.date)),
    yAxis: yAxis(t('app.analytics.axis.price', { symbol: currencyStore.symbol })),
    series: [lineSerie(t('app.analytics.metric.price'), d.map((t) => t.price), '#f59e0b')],
  }
}

function totalPriceLineOption() {
  if (!trendData.value) return {}
  const d = trendData.value.data
  return {
    title: titled(t('app.analytics.chart.totalPriceTrend')),
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: xAxis(d.map((t) => t.date)),
    yAxis: yAxis(t('app.analytics.axis.totalPrice', { symbol: currencyStore.symbol })),
    series: [
      lineSerie(t('app.analytics.metric.totalPrice'), d.map((t) => t.total_price), '#10b981'),
    ],
  }
}

function unitPriceLineOption() {
  if (!trendData.value) return {}
  const d = trendData.value.data
  return {
    title: titled(t('app.analytics.chart.unitPriceTrend')),
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: xAxis(d.map((t) => t.date)),
    yAxis: yAxis(t('app.analytics.axis.unitPrice', { symbol: currencyStore.symbol })),
    series: [
      lineSerie(t('app.analytics.metric.unitPrice'), d.map((t) => t.unit_price), '#8b5cf6'),
    ],
  }
}

function quantityPieOption() {
  if (!trendData.value) return {}
  const p = chartPalette()
  return {
    title: titled(t('app.analytics.chart.quantityDistribution')),
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { type: 'scroll', bottom: 0, textStyle: { color: p.text, fontSize: 10 } },
    series: [
      {
        name: t('app.analytics.metric.quantity'),
        type: 'pie',
        radius: ['40%', '68%'],
        center: ['50%', '46%'],
        data: trendData.value.data.map((t) => ({ name: t.date, value: t.quantity })),
      },
    ],
  }
}

function priceBarOption() {
  if (!trendData.value) return {}
  const d = trendData.value.data
  return {
    title: titled(t('app.analytics.chart.priceComparison')),
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: xAxis(d.map((t) => t.date)),
    yAxis: yAxis(t('app.analytics.axis.price', { symbol: currencyStore.symbol })),
    series: [
      {
        name: t('app.analytics.metric.price'),
        type: 'bar',
        data: d.map((t) => t.price),
        itemStyle: { color: '#f59e0b' },
      },
    ],
  }
}

function categoryPieOption() {
  const p = chartPalette()
  return {
    title: titled(t('app.analytics.chart.categoryStockShare')),
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { type: 'scroll', bottom: 0, textStyle: { color: p.text, fontSize: 10 } },
    series: [
      {
        name: t('app.analytics.metric.stock'),
        type: 'pie',
        radius: ['40%', '68%'],
        center: ['50%', '46%'],
        data: categoryStats.value.map((s) => ({ name: s.name, value: s.value })),
      },
    ],
  }
}

function monthlyCompareOption() {
  const p = chartPalette()
  return {
    title: titled(t('app.analytics.chart.monthlyCompare')),
    tooltip: { trigger: 'axis' },
    legend: { top: 28, textStyle: { color: p.text, fontSize: 11 } },
    grid: { left: '12%', right: '6%', bottom: '12%', top: '72px' },
    xAxis: xAxis(monthlyCompare.value.map((m) => m.month)),
    yAxis: yAxis(t('app.analytics.axis.amount', { symbol: currencyStore.symbol })),
    series: [
      {
        name: t('app.ledger.typeIncome'),
        type: 'bar',
        data: monthlyCompare.value.map((m) => m.income),
        itemStyle: { color: '#10b981' },
      },
      {
        name: t('app.ledger.typeExpense'),
        type: 'bar',
        data: monthlyCompare.value.map((m) => m.expense),
        itemStyle: { color: '#ef4444' },
      },
    ],
  }
}

function fmt(v: number): string {
  return v.toFixed(0)
}
</script>

<template>
  <div class="page">
    <van-nav-bar :title="t('app.analytics.title')" />
    <div class="page-body">
    <div class="ov-grid">
      <div class="ov-card">
        <div class="ov-label">{{ t('app.analytics.totalItems') }}</div>
        <div class="ov-value blue">{{ overview ? fmt(overview.total_items) : '-' }}</div>
      </div>
      <div class="ov-card">
        <div class="ov-label">{{ t('app.analytics.totalValue') }}</div>
        <div class="ov-value amber">
          {{ overview ? currencyStore.symbol + fmt(overview.total_value) : '-' }}
        </div>
      </div>
      <div class="ov-card">
        <div class="ov-label">{{ t('app.analytics.totalIncome') }}</div>
        <div class="ov-value green">
          {{ overview ? currencyStore.symbol + fmt(overview.total_income) : '-' }}
        </div>
      </div>
      <div class="ov-card">
        <div class="ov-label">{{ t('app.analytics.totalExpense') }}</div>
        <div class="ov-value red">
          {{ overview ? currencyStore.symbol + fmt(overview.total_expense) : '-' }}
        </div>
      </div>
    </div>

    <div v-if="categoryStats.length" class="chart-card">
      <VChart :option="categoryPieOption()" autoresize class="chart" />
    </div>

    <div v-if="monthlyCompare.length" class="chart-card">
      <VChart :option="monthlyCompareOption()" autoresize class="chart" />
    </div>

    <div class="sel-bar" @click="openPicker">
      <van-icon name="apps-o" size="16" color="var(--van-primary-color)" />
      <span class="sel-label">{{ selectionLabel }}</span>
      <van-icon name="arrow-down" size="14" color="var(--van-text-color-2)" />
    </div>

    <div class="trend">
      <van-loading v-if="loading" class="tip" vertical>
        {{ t('app.common.loading') }}
      </van-loading>
      <van-empty
        v-else-if="!hasData && selectedSubCategoryId"
        :description="t('app.analytics.emptyData')"
      />
      <van-empty
        v-else-if="!hasData"
        :description="t('app.analytics.emptyTrend')"
      />
      <template v-else>
        <van-tabs v-model:active="trendTab" shrink>
          <van-tab :title="t('app.analytics.tabTrend')" name="trend">
            <div class="chart-card">
              <VChart :option="quantityLineOption()" autoresize class="chart" />
            </div>
            <div class="chart-card">
              <VChart :option="priceLineOption()" autoresize class="chart" />
            </div>
            <div class="chart-card">
              <VChart :option="totalPriceLineOption()" autoresize class="chart" />
            </div>
            <div class="chart-card">
              <VChart :option="unitPriceLineOption()" autoresize class="chart" />
            </div>
          </van-tab>
          <van-tab :title="t('app.analytics.tabDistribution')" name="dist">
            <div class="chart-card">
              <VChart :option="quantityPieOption()" autoresize class="chart" />
            </div>
            <div class="chart-card">
              <VChart :option="priceBarOption()" autoresize class="chart" />
            </div>
          </van-tab>
        </van-tabs>
      </template>
    </div>
    </div>

    <CascaderPicker
      v-model:show="showPicker"
      :title="t('app.analytics.pickCategory')"
      :categories="pickerCategories"
      :subs-of="pickerSubsOf"
      :initial-category-id="selectedCategoryId ?? undefined"
      :initial-sub-id="selectedSubCategoryId ?? undefined"
      @confirm="onPickerConfirm"
    />
  </div>
</template>

<style scoped>
.page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 12px var(--tabbar-height);
}

.ov-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.ov-card {
  background: var(--van-background-2);
  border-radius: 10px;
  padding: 12px;
}

.ov-label {
  color: var(--van-text-color-2);
  font-size: 12px;
}

.ov-value {
  font-size: 20px;
  font-weight: 700;
  margin-top: 6px;
}

.blue {
  color: #1989fa;
}

.amber {
  color: #f59e0b;
}

.green {
  color: #10b981;
}

.red {
  color: #ef4444;
}

.chart-card {
  margin-top: 12px;
  background: var(--van-background-2);
  border-radius: 10px;
  padding: 8px 4px 4px;
}

.chart {
  height: 230px;
}

.sel-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: var(--van-background-2);
  border-radius: 10px;
  cursor: pointer;
}

.sel-label {
  flex: 1;
  font-size: 14px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.trend {
  margin-top: 4px;
}

.tip {
  padding-top: 60px;
}
</style>
