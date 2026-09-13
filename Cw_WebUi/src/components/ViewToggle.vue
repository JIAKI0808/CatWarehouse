<script setup lang="ts">
import { computed } from 'vue'
import { NButtonGroup, NButton } from 'naive-ui'
import { GridOutline, CardOutline } from '@vicons/ionicons5'
import { useI18n } from 'vue-i18n'
import { useItemStore } from '@/stores/item'
import type { ViewMode } from '@/types'

const itemStore = useItemStore()
const { t } = useI18n()

// computed 而非 const：文案必须随语言切换重算（模板里 v-for 会自动解包）。
const options = computed(() => [
  { label: t('app.inventory.viewTable'), value: 'table', icon: GridOutline },
  { label: t('app.inventory.viewCard'), value: 'card', icon: CardOutline },
])

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
