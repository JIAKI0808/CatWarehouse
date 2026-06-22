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
          <h1 class="text-2xl font-bold mb-6">设置</h1>

          <div class="max-w-2xl space-y-6">
            <div class="bg-white rounded-lg p-4 border">
              <h2 class="text-lg font-semibold mb-3">关于</h2>
              <div class="space-y-2 text-sm text-gray-600">
                <div class="flex justify-between">
                  <span>应用名称</span>
                  <span class="font-medium">CatWarehouse</span>
                </div>
                <div class="flex justify-between">
                  <span>版本号</span>
                  <span class="font-medium">v0.1.0</span>
                </div>
                <div class="flex justify-between">
                  <span>描述</span>
                  <span class="font-medium">三级分类库存管理系统</span>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-4 border">
              <h2 class="text-lg font-semibold mb-3">技术栈</h2>
              <div class="space-y-2 text-sm text-gray-600">
                <div class="flex justify-between">
                  <span>前端框架</span>
                  <span class="font-medium">Vue 3 + TypeScript</span>
                </div>
                <div class="flex justify-between">
                  <span>UI 库</span>
                  <span class="font-medium">Naive UI</span>
                </div>
                <div class="flex justify-between">
                  <span>状态管理</span>
                  <span class="font-medium">Pinia</span>
                </div>
                <div class="flex justify-between">
                  <span>动画</span>
                  <span class="font-medium">GSAP</span>
                </div>
                <div class="flex justify-between">
                  <span>构建工具</span>
                  <span class="font-medium">Vite</span>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg p-4 border">
              <h2 class="text-lg font-semibold mb-3">API 配置</h2>
              <div class="space-y-2 text-sm text-gray-600">
                <div class="flex justify-between">
                  <span>后端地址</span>
                  <span class="font-medium">http://localhost:11222</span>
                </div>
                <div class="flex justify-between">
                  <span>API 前缀</span>
                  <span class="font-medium">/api</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </NLayoutContent>
    </div>
  </div>
</template>
