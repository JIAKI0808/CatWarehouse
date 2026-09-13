<script setup lang="ts">
import { ref } from 'vue'
import { NIcon } from 'naive-ui'
import { ChevronForwardOutline, ChevronBackOutline } from '@vicons/ionicons5'
import { usePricingStore } from '@/stores/pricing'
import PricingCategoryTree from '@/components/PricingCategoryTree.vue'
import PricingTable from '@/components/PricingTable.vue'

const pricingStore = usePricingStore()
const panelExpanded = ref(true)

function handleSelectCategory(catId: number | null) {
  if (catId) {
    pricingStore.fetchAll()
  } else {
    pricingStore.fetchAll()
  }
}

function handleSelectSubCategory(subId: number | null) {
  if (subId) {
    pricingStore.fetchAll({ sub_category_id: subId })
  } else {
    pricingStore.fetchAll()
  }
}
</script>

<template>
  <div class="h-full flex">
    <div
      class="border-r flex flex-col transition-all duration-300"
      :class="panelExpanded ? 'w-64' : 'w-10'"
    >
      <div
        class="h-10 border-b flex items-center justify-center cursor-pointer hover:bg-gray-100"
        @click="panelExpanded = !panelExpanded"
      >
        <NIcon :size="16" class="text-gray-500">
          <ChevronBackOutline v-if="panelExpanded" />
          <ChevronForwardOutline v-else />
        </NIcon>
      </div>
      <div v-show="panelExpanded" class="flex-1 overflow-hidden">
        <PricingCategoryTree
          @select-category="handleSelectCategory"
          @select-sub-category="handleSelectSubCategory"
        />
      </div>
    </div>

    <div class="flex-1 overflow-hidden">
      <PricingTable />
    </div>
  </div>
</template>
