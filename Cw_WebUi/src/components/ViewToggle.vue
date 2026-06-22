<script setup lang="ts">
import { NButtonGroup, NButton } from 'naive-ui'
import { GridOutline, CardsOutline } from '@vicons/ionicons5'
import { useItemStore } from '@/stores/item'
import type { ViewMode } from '@/types'

const itemStore = useItemStore()

const options = [
  { label: '表格', value: 'table', icon: GridOutline },
  { label: '卡片', value: 'card', icon: CardsOutline },
]

function handleChange(mode: ViewMode) {
  itemStore.setViewMode(mode)
}
</script>

<template>
  <NButtonGroup>
    <NButton
      v-for="option in options"
      :key="option.value"
      :type="itemStore.viewMode === option.value ? 'primary' : 'default'"
      @click="handleChange(option.value)"
    >
      <component :is="option.icon" class="mr-1" />
      {{ option.label }}
    </NButton>
  </NButtonGroup>
</template>
