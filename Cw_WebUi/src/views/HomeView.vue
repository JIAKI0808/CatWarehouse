<script setup lang="ts">
import { NLayout, NLayoutSider, NLayoutContent, NSplit } from 'naive-ui'
import { useItemStore } from '@/stores/item'
import CategoryTree from '@/components/CategoryTree.vue'
import ItemTable from '@/components/ItemTable.vue'
import ItemCard from '@/components/ItemCard.vue'
import ViewToggle from '@/components/ViewToggle.vue'

const itemStore = useItemStore()
</script>

<template>
  <div class="h-full flex">
    <div class="w-64 border-r bg-white flex flex-col">
      <CategoryTree />
    </div>
    <div class="flex-1 flex flex-col">
      <div class="p-4 border-b bg-white flex justify-between items-center">
        <h2 class="text-lg font-bold">库存管理</h2>
        <ViewToggle />
      </div>
      <div class="flex-1 overflow-hidden">
        <ItemTable v-if="itemStore.viewMode === 'table'" />
        <ItemCard v-else />
      </div>
    </div>
  </div>
</template>
