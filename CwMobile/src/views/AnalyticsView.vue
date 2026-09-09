<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
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
const pickerMode = ref<'category' | 'sub'>('category')
const pickerTitle = ref('')

const dark = () => themeStore.isDark
function chartPalette() {
  return {
    text: dark() ? '#d8d8dd' : '#666',
    line: dark() ? '#3a3a3d' : '#e2e2e2',
    split: dark() ? '#2a2a2d' : '#f2f3f5',
  }
}

const categoryOptions = computed(() =>
  categoryStore.categories.map((c) => ({ label: c.name, value: c.id }))
)

const subOptions = computed(() => {
  const catId = selectedCategoryId.value
  if (catId === null) return []
  const list = subCategoryStore.subCategoriesByCategory[catId] ?? []
  return list.map((s) => ({ label: s.name, value: s.id }))
})

const currentCatName = computed(() => {
  const cat = categoryStore.categories.find((c) => c.id === selectedCategoryId.value)
  return cat ? cat.name : '选择大类'
})

const currentSubName = computed(() => {
  const opt = subOptions.value.find((o) => o.value === selectedSubCategoryId.value)
  return opt ? opt.label : '选择子类'
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

watch(selectedCategoryId, (id) => {
  selectedSubCategoryId.value = null
  trendData.value = null
  if (id) subCategoryStore.fetchByCategory(id)
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

function openCategoryPicker() {
  pickerMode.value = 'category'
  pickerTitle.value = '选择大类'
  showPicker.value = true
}

function openSubPicker() {
  pickerMode.value = 'sub'
  pickerTitle.value = '选择子类'
  showPicker.value = true
}

function onPick(opt: { label: string; value: number }) {
  showPicker.value = false
  if (pickerMode.value === 'category') {
    selectedCategoryId.value = opt.value
  } else {
    selectedSubCategoryId.value = opt.value
  }
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
    title: titled('数量趋势'),
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: xAxis(d.map((t) => t.date)),
    yAxis: yAxis(`数量 (${trendData.value.unit})`),
    series: [lineSerie('数量', d.map((t) => t.quantity), '#1989fa')],
  }
}

function priceLineOption() {
  if (!trendData.value) return {}
  const d = trendData.value.data
  return {
    title: titled('价格趋势'),
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: xAxis(d.map((t) => t.date)),
    yAxis: yAxis('价格 (¥)'),
    series: [lineSerie('价格', d.map((t) => t.price), '#f59e0b')],
  }
}

function totalPriceLineOption() {
  if (!trendData.value) return {}
  const d = trendData.value.data
  return {
    title: titled('总价趋势'),
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: xAxis(d.map((t) => t.date)),
    yAxis: yAxis('总价 (¥)'),
    series: [lineSerie('总价', d.map((t) => t.total_price), '#10b981')],
  }
}

function unitPriceLineOption() {
  if (!trendData.value) return {}
  const d = trendData.value.data
  return {
    title: titled('单价趋势'),
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: xAxis(d.map((t) => t.date)),
    yAxis: yAxis('单价 (¥)'),
    series: [lineSerie('单价', d.map((t) => t.unit_price), '#8b5cf6')],
  }
}

function quantityPieOption() {
  if (!trendData.value) return {}
  const p = chartPalette()
  return {
    title: titled('数量分布'),
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { type: 'scroll', bottom: 0, textStyle: { color: p.text, fontSize: 10 } },
    series: [
      {
        name: '数量',
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
    title: titled('价格对比'),
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: xAxis(d.map((t) => t.date)),
    yAxis: yAxis('价格 (¥)'),
    series: [
      { name: '价格', type: 'bar', data: d.map((t) => t.price), itemStyle: { color: '#f59e0b' } },
    ],
  }
}

function categoryPieOption() {
  const p = chartPalette()
  return {
    title: titled('分类库存占比'),
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { type: 'scroll', bottom: 0, textStyle: { color: p.text, fontSize: 10 } },
    series: [
      {
        name: '库存',
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
    title: titled('月度收支对比'),
    tooltip: { trigger: 'axis' },
    legend: { top: 28, textStyle: { color: p.text, fontSize: 11 } },
    grid: { left: '12%', right: '6%', bottom: '12%', top: '72px' },
    xAxis: xAxis(monthlyCompare.value.map((m) => m.month)),
    yAxis: yAxis('金额 (¥)'),
    series: [
      { name: '收入', type: 'bar', data: monthlyCompare.value.map((m) => m.income), itemStyle: { color: '#10b981' } },
      { name: '支出', type: 'bar', data: monthlyCompare.value.map((m) => m.expense), itemStyle: { color: '#ef4444' } },
    ],
  }
}

function fmt(v: number): string {
  return v.toFixed(0)
}
</script>

<template>
  <div class="page">
    <div class="ov-grid">
      <div class="ov-card">
        <div class="ov-label">总库存数</div>
        <div class="ov-value blue">{{ overview ? fmt(overview.total_items) : '-' }}</div>
      </div>
      <div class="ov-card">
        <div class="ov-label">总库存价值</div>
        <div class="ov-value amber">
          {{ overview ? '¥' + fmt(overview.total_value) : '-' }}
        </div>
      </div>
      <div class="ov-card">
        <div class="ov-label">总收入</div>
        <div class="ov-value green">
          {{ overview ? '¥' + fmt(overview.total_income) : '-' }}
        </div>
      </div>
      <div class="ov-card">
        <div class="ov-label">总支出</div>
        <div class="ov-value red">
          {{ overview ? '¥' + fmt(overview.total_expense) : '-' }}
        </div>
      </div>
    </div>

    <div v-if="categoryStats.length" class="chart-card">
      <VChart :option="categoryPieOption()" autoresize class="chart" />
    </div>

    <div v-if="monthlyCompare.length" class="chart-card">
      <VChart :option="monthlyCompareOption()" autoresize class="chart" />
    </div>

    <van-cell-group inset class="sel">
      <van-field
        readonly
        is-link
        :model-value="currentCatName"
        label="大类"
        @click="openCategoryPicker"
      />
      <van-field
        readonly
        is-link
        :model-value="currentSubName"
        label="子类"
        :disabled="selectedCategoryId === null"
        @click="openSubPicker"
      />
    </van-cell-group>

    <div class="trend">
      <van-loading v-if="loading" class="tip" vertical>加载中</van-loading>
      <van-empty
        v-else-if="!hasData && selectedSubCategoryId"
        description="暂无数据"
      />
      <van-empty
        v-else-if="!hasData"
        description="选择大类和子类查看趋势"
      />
      <template v-else>
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
        <div class="chart-card">
          <VChart :option="quantityPieOption()" autoresize class="chart" />
        </div>
        <div class="chart-card">
          <VChart :option="priceBarOption()" autoresize class="chart" />
        </div>
      </template>
    </div>

    <van-popup v-model:show="showPicker" position="bottom" round>
      <div class="picker">
        <div class="picker-title">{{ pickerTitle }}</div>
        <div class="picker-body">
          <van-cell
            v-for="opt in pickerMode === 'category' ? categoryOptions : subOptions"
            :key="opt.value"
            :title="opt.label"
            is-link
            @click="onPick(opt)"
          />
          <van-empty v-if="pickerMode === 'sub' && !subOptions.length" description="该大类暂无子分类" />
        </div>
        <van-button block plain @click="showPicker = false">取消</van-button>
        <div class="pad" />
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.page {
  padding: 12px 12px 90px;
}

.ov-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.ov-card {
  background: #fff;
  border-radius: 10px;
  padding: 12px;
}

html.dark .ov-card {
  background: #1c1c1e;
}

.ov-label {
  color: #969799;
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
  background: #fff;
  border-radius: 10px;
  padding: 8px 4px 4px;
}

html.dark .chart-card {
  background: #1c1c1e;
}

.chart {
  height: 230px;
}

.sel {
  margin-top: 12px;
}

.trend {
  margin-top: 4px;
}

.tip {
  padding-top: 60px;
}

.picker-title {
  padding: 16px 0;
  text-align: center;
  font-weight: 600;
}

.picker-body {
  max-height: 45vh;
  overflow-y: auto;
}

.pad {
  height: 16px;
}
</style>
