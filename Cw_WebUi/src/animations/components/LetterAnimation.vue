<script setup lang="ts">
defineProps<{
  letter: string
}>()
</script>

<template>
  <span
    class="inline-block text-6xl font-bold cursor-default select-none"
    :class="letter === 'C' || letter === 'W' ? 'text-amber-500' : 'text-blue-500'"
    style="text-shadow: 2px 2px 4px rgba(0,0,0,0.15);"
  >
    {{ letter }}
  </span>
</template>
