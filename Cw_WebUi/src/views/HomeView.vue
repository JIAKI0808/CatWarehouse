<script setup lang="ts">
import { ref } from 'vue'
import { NButton, NIcon, NDrawer, NDrawerContent } from 'naive-ui'
import { MenuOutline } from '@vicons/ionicons5'
import { useItemStore } from '@/stores/item'
import CategoryTree from '@/components/CategoryTree.vue'
import ItemTable from '@/components/ItemTable.vue'

const itemStore = useItemStore()
const showDrawer = ref(false)
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="h-10 border-b bg-white flex items-center px-4 gap-4">
      <NButton text @click="showDrawer = true">
        <template #icon>
          <NIcon :size="20"><MenuOutline /></NIcon>
        </template>
      </NButton>
      <span class="text-sm font-medium text-gray-600">库存管理</span>
    </div>

    <div class="flex-1 overflow-hidden bg-gray-50">
      <ItemTable />
    </div>

    <NDrawer v-model:show="showDrawer" placement="left" :width="280">
      <NDrawerContent>
        <CategoryTree />
      </NDrawerContent>
    </NDrawer>
  </div>
</template>
