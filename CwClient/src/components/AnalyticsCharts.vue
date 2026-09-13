<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { NSelect, NSpin, NEmpty, NGrid, NGridItem, NCard } from 'naive-ui'
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
import { useI18n } from 'vue-i18n'
import { useCategoryStore } from '@/stores/category'
import { useSubCategoryStore } from '@/stores/subCategory'
import { analyticsApi } from '@/services/api'
import type { TrendData, AnalyticsOverview, CategoryStat, MonthlyCompare } from '@/types'

use([CanvasRenderer, LineChart, PieChart, BarChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])

const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()
const { t } = useI18n()

const selectedCategoryId = ref<number | null>(null)
const selectedSubCategoryId = ref<number | null>(null)
const trendData = ref<TrendData | null>(null)
const overview = ref<AnalyticsOverview | null>(null)
const categoryStats = ref<CategoryStat[]>([])
const monthlyCompare = ref<MonthlyCompare[]>([])
const loading = ref(false)

const categoryOptions = ref<{ label: string; value: number }[]>([])
const subCategoryOptions = ref<{ label: string; value: number }[]>([])

onMounted(async () => {
  try {
    [overview.value, categoryStats.value, monthlyCompare.value] = await Promise.all([
      analyticsApi.getOverview(),
      analyticsApi.getCategoryStats(),
      analyticsApi.getMonthlyCompare(),
    ])
  } catch {}
})

watch(() => categoryStore.categories, (cats) => {
  categoryOptions.value = cats.map(c => ({ label: c.name, value: c.id }))
}, { immediate: true })

watch(selectedCategoryId, (catId) => {
  selectedSubCategoryId.value = null
  trendData.value = null
  if (catId) {
    subCategoryStore.fetchByCategory(catId)
  }
})

watch(() => subCategoryStore.subCategoriesByCategory, (map) => {
  if (selectedCategoryId.value && map[selectedCategoryId.value]) {
    const subs = map[selectedCategoryId.value]
    subCategoryOptions.value = subs.map(s => ({ label: s.name, value: s.id }))
  }
}, { deep: true })

watch(selectedSubCategoryId, async (subId) => {
  if (!subId) {
    trendData.value = null
    return
  }
  loading.value = true
  try {
    trendData.value = await analyticsApi.getTrend(subId)
  } catch {
    trendData.value = null
  } finally {
    loading.value = false
  }
})

function baseGrid() {
  return { left: '10%', right: '10%', bottom: '15%', top: '15%' }
}

function quantityLineOption() {
  if (!trendData.value) return {}
  return {
    title: { text: t('app.analytics.chart.quantityTrend'), left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: trendData.value.data.map(d => d.date) },
    yAxis: {
      type: 'value',
      name: t('app.analytics.axis.quantity', { unit: trendData.value.unit }),
    },
    series: [{
      name: t('app.analytics.metric.quantity'), type: 'line', data: trendData.value.data.map(d => d.quantity),
      smooth: true, areaStyle: { opacity: 0.3 },
    }],
  }
}

function priceLineOption() {
  if (!trendData.value) return {}
  return {
    title: { text: t('app.analytics.chart.priceTrend'), left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: trendData.value.data.map(d => d.date) },
    yAxis: { type: 'value', name: t('app.analytics.axis.price') },
    series: [{
      name: t('app.analytics.metric.price'), type: 'line', data: trendData.value.data.map(d => d.price),
      smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#f59e0b' },
    }],
  }
}

function totalPriceLineOption() {
  if (!trendData.value) return {}
  return {
    title: { text: t('app.analytics.chart.totalPriceTrend'), left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: trendData.value.data.map(d => d.date) },
    yAxis: { type: 'value', name: t('app.analytics.axis.totalPrice') },
    series: [{
      name: t('app.analytics.metric.totalPrice'), type: 'line', data: trendData.value.data.map(d => d.total_price),
      smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#10b981' },
    }],
  }
}

function unitPriceLineOption() {
  if (!trendData.value) return {}
  return {
    title: { text: t('app.analytics.chart.unitPriceTrend'), left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: trendData.value.data.map(d => d.date) },
    yAxis: { type: 'value', name: t('app.analytics.axis.unitPrice') },
    series: [{
      name: t('app.analytics.metric.unitPrice'), type: 'line', data: trendData.value.data.map(d => d.unit_price),
      smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#8b5cf6' },
    }],
  }
}

function quantityPieOption() {
  if (!trendData.value) return {}
  return {
    title: { text: t('app.analytics.chart.quantityDistribution'), left: 'center' },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      name: t('app.analytics.metric.quantity'), type: 'pie', radius: ['40%', '70%'],
      data: trendData.value.data.map(d => ({ name: d.date, value: d.quantity })),
    }],
  }
}

function priceBarOption() {
  if (!trendData.value) return {}
  return {
    title: { text: t('app.analytics.chart.priceComparison'), left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: trendData.value.data.map(d => d.date) },
    yAxis: { type: 'value', name: t('app.analytics.axis.price') },
    series: [{
      name: t('app.analytics.metric.price'), type: 'bar', data: trendData.value.data.map(d => d.price),
      itemStyle: { color: '#f59e0b' },
    }],
  }
}

function categoryPieOption() {
  return {
    title: { text: t('app.analytics.chart.categoryStockShare'), left: 'center' },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      name: t('app.analytics.metric.stock'), type: 'pie', radius: ['40%', '70%'],
      data: categoryStats.value.map(s => ({ name: s.name, value: s.value })),
    }],
  }
}

function monthlyCompareOption() {
  return {
    title: { text: t('app.analytics.chart.monthlyCompare'), left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { top: 30 },
    grid: { left: '12%', right: '12%', bottom: '15%', top: '60px' },
    xAxis: { type: 'category', data: monthlyCompare.value.map(m => m.month) },
    yAxis: { type: 'value', name: t('app.analytics.axis.amount') },
    series: [
      {
        name: t('app.ledger.typeIncome'),
        type: 'bar', data: monthlyCompare.value.map(m => m.income),
        itemStyle: { color: '#10b981' },
      },
      {
        name: t('app.ledger.typeExpense'),
        type: 'bar', data: monthlyCompare.value.map(m => m.expense),
        itemStyle: { color: '#ef4444' },
      },
    ],
  }
}

const hasData = () => trendData.value && trendData.value.data.length > 0
</script>

<template>
  <div class="space-y-6">
    <NGrid v-if="overview" :cols="4" :x-gap="16">
      <NGridItem>
        <NCard size="small" :title="t('app.analytics.totalItems')">
          <div class="text-2xl font-bold text-blue-500">{{ overview.total_items }}</div>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard size="small" :title="t('app.analytics.totalValue')">
          <div class="text-2xl font-bold text-amber-500">¥{{ overview.total_value.toFixed(0) }}</div>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard size="small" :title="t('app.analytics.totalIncome')">
          <div class="text-2xl font-bold text-green-500">¥{{ overview.total_income.toFixed(0) }}</div>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard size="small" :title="t('app.analytics.totalExpense')">
          <div class="text-2xl font-bold text-red-500">¥{{ overview.total_expense.toFixed(0) }}</div>
        </NCard>
      </NGridItem>
    </NGrid>

    <div class="chart-grid">
      <VChart v-if="categoryStats.length" :option="categoryPieOption()" class="chart-cell" />
      <VChart v-if="monthlyCompare.length" :option="monthlyCompareOption()" class="chart-cell" />
    </div>

    <div class="flex gap-4">
      <NSelect
        v-model:value="selectedCategoryId"
        :options="categoryOptions"
        :placeholder="t('app.analytics.selectCategory')"
        style="width: 200px"
      />
      <NSelect
        v-model:value="selectedSubCategoryId"
        :options="subCategoryOptions"
        :placeholder="t('app.analytics.selectSubCategory')"
        :disabled="!selectedCategoryId"
        style="width: 200px"
      />
    </div>

    <NSpin :show="loading">
      <div v-if="hasData()" class="chart-grid">
        <VChart :option="quantityLineOption()" class="chart-cell" />
        <VChart :option="priceLineOption()" class="chart-cell" />
        <VChart :option="totalPriceLineOption()" class="chart-cell" />
        <VChart :option="unitPriceLineOption()" class="chart-cell" />
        <VChart :option="quantityPieOption()" class="chart-cell" />
        <VChart :option="priceBarOption()" class="chart-cell" />
      </div>
      <NEmpty
        v-else-if="!loading && selectedSubCategoryId"
        :description="t('app.common.noData')"
      />
      <NEmpty v-else-if="!loading" :description="t('app.analytics.emptyTrend')" />
    </NSpin>
  </div>
</template>

<style scoped>
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.chart-cell {
  height: 320px;
}
</style>
