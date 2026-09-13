<script setup lang="ts">
import { computed } from 'vue'

interface Option {
  text: string
  value: number
}

interface TreeNode extends Option {
  children?: Option[]
}

const props = defineProps<{
  show: boolean
  title: string
  categories: Option[]
  subsOf: (catId: number) => Option[]
  initialCategoryId?: number
  initialSubId?: number
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'confirm', value: { categoryId: number; subId: number | null }): void
}>()

const columns = computed<TreeNode[]>(() =>
  props.categories.map((c) => ({
    text: c.text,
    value: c.value,
    children: props.subsOf(c.value),
  }))
)

const defaultIndex = computed<number[]>(() => {
  const catIdx = props.categories.findIndex(
    (c) => c.value === props.initialCategoryId
  )
  const base = catIdx >= 0 ? catIdx : 0
  const cat = props.categories[base]
  const subs = cat ? props.subsOf(cat.value) : []
  const subIdx = subs.findIndex((s) => s.value === props.initialSubId)
  return [base, subIdx >= 0 ? subIdx : 0]
})

function onConfirm(e: { selectedValues: (string | number)[] }) {
  emit('confirm', {
    categoryId: Number(e.selectedValues[0] ?? 0),
    subId: e.selectedValues[1] != null ? Number(e.selectedValues[1]) : null,
  })
  emit('update:show', false)
}
</script>

<template>
  <van-popup
    :show="show"
    position="bottom"
    round
    @update:show="emit('update:show', $event)"
  >
    <van-picker
      v-if="show"
      :columns="columns"
      :title="title"
      :default-index="defaultIndex"
      @confirm="onConfirm"
      @cancel="emit('update:show', false)"
    />
  </van-popup>
</template>
