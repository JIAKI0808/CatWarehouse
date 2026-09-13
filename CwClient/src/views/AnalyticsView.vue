<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import AnalyticsCharts from '@/components/AnalyticsCharts.vue'

const { t } = useI18n()
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">{{ t('app.analytics.title') }}</h1>
    <AnalyticsCharts />
  </div>
</template>
