<script setup lang="ts">
import { ref } from 'vue'
import { NLayout, NLayoutSider, NLayoutContent, NIcon, NTooltip } from 'naive-ui'
import {
  WalletOutline,
  AnalyticsOutline,
  SettingsOutline,
} from '@vicons/ionicons5'
import MenuBar from './components/MenuBar.vue'

const activeView = ref('inventory')

const navItems = [
  { key: 'inventory', label: '库存', icon: WalletOutline },
  { key: 'analytics', label: '数据分析', icon: AnalyticsOutline },
]

function handleNavigate(view: string) {
  activeView.value = view
}
</script>

<template>
  <div class="h-screen flex flex-col">
    <MenuBar @navigate="handleNavigate" />

    <div class="flex-1 flex overflow-hidden">
      <NLayoutSider
        bordered
        :width="64"
        :native-scrollbar="false"
        class="flex flex-col"
      >
        <div class="flex-1 flex flex-col items-center py-4 gap-2">
          <NTooltip v-for="item in navItems" :key="item.key" placement="right">
            <template #trigger>
              <div
                class="w-10 h-10 rounded-lg flex items-center justify-center cursor-pointer transition-all duration-200"
                :class="activeView === item.key
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-500 hover:bg-gray-100'"
                @click="activeView = item.key"
              >
                <NIcon :size="22">
                  <component :is="item.icon" />
                </NIcon>
              </div>
            </template>
            {{ item.label }}
          </NTooltip>
        </div>

        <div class="flex flex-col items-center pb-4">
          <NTooltip placement="right">
            <template #trigger>
              <div
                class="w-10 h-10 rounded-lg flex items-center justify-center cursor-pointer transition-all duration-200"
                :class="activeView === 'settings'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-500 hover:bg-gray-100'"
                @click="activeView = 'settings'"
              >
                <NIcon :size="22">
                  <SettingsOutline />
                </NIcon>
              </div>
            </template>
            设置
          </NTooltip>
        </div>
      </NLayoutSider>

      <NLayoutContent :native-scrollbar="false">
        <RouterView v-if="activeView === 'inventory'" />
        <div v-else-if="activeView === 'analytics'" class="p-6">
          <h1 class="text-2xl font-bold mb-4">数据分析</h1>
          <p class="text-gray-500">功能开发中...</p>
        </div>
        <div v-else-if="activeView === 'settings'" class="p-6">
          <h1 class="text-2xl font-bold mb-4">设置</h1>
          <p class="text-gray-500">功能开发中...</p>
        </div>
      </NLayoutContent>
    </div>
  </div>
</template>
