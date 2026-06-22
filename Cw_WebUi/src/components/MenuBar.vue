<script setup lang="ts">
import { ref } from 'vue'
import { NMenu, NIcon } from 'naive-ui'
import {
  HomeOutline,
  WalletOutline,
  AnalyticsOutline,
  SettingsOutline,
  HelpCircleOutline,
} from '@vicons/ionicons5'

const emit = defineEmits<{
  (e: 'navigate', view: string): void
}>()

const activeView = ref('inventory')

const menuOptions = [
  {
    label: '文件',
    key: 'file',
    icon: HomeOutline,
    children: [
      { label: '新建', key: 'new' },
      { label: '打开', key: 'open' },
      { label: '保存', key: 'save' },
      { type: 'divider', key: 'd1' },
      { label: '退出', key: 'exit' },
    ],
  },
  {
    label: '视图',
    key: 'view',
    icon: WalletOutline,
    children: [
      { label: '库存管理', key: 'inventory' },
      { label: '数据分析', key: 'analytics' },
      { type: 'divider', key: 'd2' },
      { label: '设置', key: 'settings' },
    ],
  },
  {
    label: '帮助',
    key: 'help',
    icon: HelpCircleOutline,
    children: [
      { label: '关于', key: 'about' },
    ],
  },
]

function handleMenuSelect(key: string) {
  if (['inventory', 'analytics', 'settings'].includes(key)) {
    activeView.value = key
    emit('navigate', key)
  }
}
</script>

<template>
  <div class="h-8 bg-gray-100 border-b flex items-center px-2 select-none">
    <div class="flex items-center gap-1">
      <NIcon :size="16" class="text-blue-500 mr-1">
        <WalletOutline />
      </NIcon>
      <span class="text-xs font-medium text-gray-700">CatWarehouse</span>
    </div>

    <NMenu
      :options="menuOptions"
      mode="horizontal"
      :collapsed-width="64"
      :collapsed-icon-size="20"
      class="ml-4"
      @update:value="handleMenuSelect"
    />

    <div class="flex-1" />
  </div>
</template>
