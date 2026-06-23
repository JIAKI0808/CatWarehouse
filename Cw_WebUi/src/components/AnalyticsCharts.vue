<script setup lang="ts">
import { ref, watch } from 'vue'
import { NSelect, NSpin, NEmpty } from 'naive-ui'
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
import { analyticsApi } from '@/services/api'
import type { TrendData } from '@/types'

use([CanvasRenderer, LineChart, PieChart, BarChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])

const categoryStore = useCategoryStore()
const subCategoryStore = useSubCategoryStore()

const selectedCategoryId = ref<number | null>(null)
const selectedSubCategoryId = ref<number | null>(null)
const trendData = ref<TrendData | null>(null)
const loading = ref(false)

const categoryOptions = ref<{ label: string; value: number }[]>([])
const subCategoryOptions = ref<{ label: string; value: number }[]>([])

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
    title: { text: '数量趋势', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: trendData.value.data.map(d => d.date) },
    yAxis: { type: 'value', name: `数量 (${trendData.value.unit})` },
    series: [{
      name: '数量', type: 'line', data: trendData.value.data.map(d => d.quantity),
      smooth: true, areaStyle: { opacity: 0.3 },
    }],
  }
}

function priceLineOption() {
  if (!trendData.value) return {}
  return {
    title: { text: '价格趋势', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: trendData.value.data.map(d => d.date) },
    yAxis: { type: 'value', name: '价格 (¥)' },
    series: [{
      name: '价格', type: 'line', data: trendData.value.data.map(d => d.price),
      smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#f59e0b' },
    }],
  }
}

function totalPriceLineOption() {
  if (!trendData.value) return {}
  return {
    title: { text: '总价趋势', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: trendData.value.data.map(d => d.date) },
    yAxis: { type: 'value', name: '总价 (¥)' },
    series: [{
      name: '总价', type: 'line', data: trendData.value.data.map(d => d.total_price),
      smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#10b981' },
    }],
  }
}

function unitPriceLineOption() {
  if (!trendData.value) return {}
  return {
    title: { text: '单价趋势', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: trendData.value.data.map(d => d.date) },
    yAxis: { type: 'value', name: '单价 (¥)' },
    series: [{
      name: '单价', type: 'line', data: trendData.value.data.map(d => d.unit_price),
      smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#8b5cf6' },
    }],
  }
}

function quantityPieOption() {
  if (!trendData.value) return {}
  return {
    title: { text: '数量分布', left: 'center' },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      name: '数量', type: 'pie', radius: ['40%', '70%'],
      data: trendData.value.data.map(d => ({ name: d.date, value: d.quantity })),
    }],
  }
}

function priceBarOption() {
  if (!trendData.value) return {}
  return {
    title: { text: '价格对比', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: baseGrid(),
    xAxis: { type: 'category', data: trendData.value.data.map(d => d.date) },
    yAxis: { type: 'value', name: '价格 (¥)' },
    series: [{
      name: '价格', type: 'bar', data: trendData.value.data.map(d => d.price),
      itemStyle: { color: '#f59e0b' },
    }],
  }
}

const hasData = () => trendData.value && trendData.value.data.length > 0
</script>

<template>
  <div class="space-y-4">
    <div class="flex gap-4">
      <NSelect
        v-model:value="selectedCategoryId"
        :options="categoryOptions"
        placeholder="选择大类"
        style="width: 200px"
      />
      <NSelect
        v-model:value="selectedSubCategoryId"
        :options="subCategoryOptions"
        placeholder="选择子类"
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
      <NEmpty v-else-if="!loading && selectedSubCategoryId" description="暂无数据" />
      <NEmpty v-else-if="!loading" description="请选择大类和子类查看趋势" />
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
