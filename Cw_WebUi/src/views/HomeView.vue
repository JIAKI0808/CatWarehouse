<script setup lang="ts">
import { NLayout, NLayoutSider, NLayoutContent } from 'naive-ui'
import { useItemStore } from '@/stores/item'
import CategoryTree from '@/components/CategoryTree.vue'
import ItemTable from '@/components/ItemTable.vue'
import ItemCard from '@/components/ItemCard.vue'
import ViewToggle from '@/components/ViewToggle.vue'

const itemStore = useItemStore()
</script>

<template>
  <NLayout has-sider class="h-screen">
    <NLayoutSider bordered :width="280">
      <CategoryTree />
    </NLayoutSider>
    <NLayoutContent>
      <div class="p-4 h-full flex flex-col">
        <div class="mb-4 flex justify-end">
          <ViewToggle />
        </div>
        <div class="flex-1 overflow-hidden">
          <ItemTable v-if="itemStore.viewMode === 'table'" />
          <ItemCard v-else />
        </div>
      </div>
    </NLayoutContent>
  </NLayout>
</template>
