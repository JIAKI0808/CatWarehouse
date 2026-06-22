<script setup lang="ts">
import { ref } from 'vue'
import { NLayoutSider, NIcon, NTooltip } from 'naive-ui'
import {
  WalletOutline,
  AnalyticsOutline,
  SettingsOutline,
} from '@vicons/ionicons5'
import MenuBar from './components/MenuBar.vue'
import HomeView from './views/HomeView.vue'
import AnalyticsView from './views/AnalyticsView.vue'
import SettingsView from './views/SettingsView.vue'

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
        class="flex flex-col relative"
      >
        <div class="flex flex-col items-center py-4 gap-2">
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

        <div class="absolute bottom-4 left-0 right-0 flex flex-col items-center">
          <div class="w-8 border-t border-gray-300 mb-4" />
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

      <div class="flex-1 overflow-hidden">
        <HomeView v-if="activeView === 'inventory'" />
        <AnalyticsView v-else-if="activeView === 'analytics'" />
        <SettingsView v-else-if="activeView === 'settings'" />
      </div>
    </div>
  </div>
</template>
