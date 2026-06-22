<script setup lang="ts">
defineProps<{
  msg: string
}>()
</script>

<template>
  <div class="text-center py-10">
    <h1 class="text-4xl font-bold text-green-600 mb-4">{{ msg }}</h1>
    <h3 class="text-xl text-gray-500">Inventory Management System</h3>
  </div>
</template>
