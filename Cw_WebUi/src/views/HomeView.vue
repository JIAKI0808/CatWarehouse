<script setup lang="ts">
import { NTabs, NTabPane } from 'naive-ui'
import { useItemStore } from '@/stores/item'
import CategoryTree from '@/components/CategoryTree.vue'
import ItemTable from '@/components/ItemTable.vue'
import ItemCard from '@/components/ItemCard.vue'
import ViewToggle from '@/components/ViewToggle.vue'

const itemStore = useItemStore()
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="h-10 border-b bg-white flex items-center px-4 gap-4">
      <div class="flex-1" />
      <ViewToggle />
    </div>

    <div class="flex-1 flex overflow-hidden">
      <div class="w-64 border-r bg-white">
        <CategoryTree />
      </div>

      <div class="flex-1 overflow-hidden bg-gray-50">
        <NTabs type="segment" class="p-4 h-full flex flex-col">
          <NTabPane name="list" tab="列表视图">
            <div class="flex-1 overflow-auto">
              <ItemTable />
            </div>
          </NTabPane>
          <NTabPane name="card" tab="卡片视图">
            <div class="flex-1 overflow-auto">
              <ItemCard />
            </div>
          </NTabPane>
        </NTabs>
      </div>
    </div>
  </div>
</template>
