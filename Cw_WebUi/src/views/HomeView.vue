<script setup lang="ts">
import { NSplit, NTabs, NTabPane } from 'naive-ui'
import { useItemStore } from '@/stores/item'
import { useSubCategoryStore } from '@/stores/subCategory'
import CategoryTree from '@/components/CategoryTree.vue'
import ItemTable from '@/components/ItemTable.vue'
import ItemCard from '@/components/ItemCard.vue'
import ViewToggle from '@/components/ViewToggle.vue'

const itemStore = useItemStore()
const subCategoryStore = useSubCategoryStore()
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="h-48 border-b bg-white flex">
      <div class="w-64 border-r">
        <CategoryTree />
      </div>
      <div class="flex-1 p-4">
        <div class="flex justify-between items-center mb-3">
          <h2 class="text-sm font-semibold text-gray-600">分类信息</h2>
          <ViewToggle />
        </div>
        <div class="text-sm text-gray-500" v-if="subCategoryStore.selectedId">
          <p>当前选中: {{ subCategoryStore.subCategories.find(s => s.id === subCategoryStore.selectedId)?.name || '无' }}</p>
        </div>
        <div class="text-sm text-gray-400" v-else>
          请在左侧选择一个子分类
        </div>
      </div>
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
</template>
