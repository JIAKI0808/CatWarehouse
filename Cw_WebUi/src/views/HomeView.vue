<script setup lang="ts">
import { ref } from 'vue'
import { NIcon } from 'naive-ui'
import { ChevronForwardOutline, ChevronBackOutline } from '@vicons/ionicons5'
import { useItemStore } from '@/stores/item'
import CategoryTree from '@/components/CategoryTree.vue'
import ItemTable from '@/components/ItemTable.vue'
import ItemCard from '@/components/ItemCard.vue'

const itemStore = useItemStore()
const panelExpanded = ref(true)
</script>

<template>
  <div class="h-full flex">
    <!-- 左侧分类面板 -->
    <div
      class="border-r bg-white flex flex-col transition-all duration-300"
      :class="panelExpanded ? 'w-64' : 'w-10'"
    >
      <!-- 折叠按钮 -->
      <div
        class="h-10 border-b flex items-center justify-center cursor-pointer hover:bg-gray-100"
        @click="panelExpanded = !panelExpanded"
      >
        <NIcon :size="16" class="text-gray-500">
          <ChevronBackOutline v-if="panelExpanded" />
          <ChevronForwardOutline v-else />
        </NIcon>
      </div>

      <!-- 分类树 -->
      <div
        v-show="panelExpanded"
        class="flex-1 overflow-hidden"
      >
        <CategoryTree />
      </div>
    </div>

    <!-- 右侧内容区域 -->
    <div class="flex-1 overflow-hidden bg-gray-50">
      <ItemTable v-if="itemStore.viewMode === 'table'" />
      <ItemCard v-else />
    </div>
  </div>
</template>
