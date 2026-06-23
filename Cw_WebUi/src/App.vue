<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { NLayoutSider, NIcon, NTooltip, NMessageProvider, NConfigProvider, darkTheme, useDialog } from 'naive-ui'
import {
  WalletOutline,
  AnalyticsOutline,
  SettingsOutline,
  CashOutline,
  PricetagOutline,
} from '@vicons/ionicons5'
import { useRouter } from 'vue-router'
import MenuBar from './components/MenuBar.vue'

const router = useRouter()
const isDark = ref(false)

const theme = computed(() => isDark.value ? darkTheme : null)

onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved === 'dark') isDark.value = true
  else if (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches) isDark.value = true
  updateDarkClass()

  window.addEventListener('keydown', handleKeydown)
})

function updateDarkClass() {
  document.documentElement.classList.toggle('dark', isDark.value)
}

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

function handleKeydown(e: KeyboardEvent) {
  if (e.ctrlKey && e.key === 'n') {
    e.preventDefault()
    window.dispatchEvent(new CustomEvent('shortcut-add'))
  }
  if (e.ctrlKey && e.key === 'f') {
    e.preventDefault()
    window.dispatchEvent(new CustomEvent('shortcut-search'))
  }
  if (e.key === 'Escape') {
    window.dispatchEvent(new CustomEvent('shortcut-escape'))
  }
}

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  updateDarkClass()
}

const navItems = [
  { path: '/', label: '库存', icon: WalletOutline },
  { path: '/analytics', label: '数据分析', icon: AnalyticsOutline },
  { path: '/ledger', label: '账本', icon: CashOutline },
  { path: '/pricing', label: '售价管理', icon: PricetagOutline },
]
</script>

<template>
  <NConfigProvider :theme="theme">
  <NMessageProvider>
  <div class="h-screen flex flex-col">
    <MenuBar :is-dark="isDark" @toggle-theme="toggleTheme" />

    <div class="flex-1 flex overflow-hidden">
      <NLayoutSider
        bordered
        :width="64"
        :native-scrollbar="false"
        class="flex flex-col relative"
      >
        <div class="flex flex-col items-center py-4 gap-2">
          <NTooltip v-for="item in navItems" :key="item.path" placement="right">
            <template #trigger>
              <router-link
                :to="item.path"
                class="w-10 h-10 rounded-lg flex items-center justify-center cursor-pointer transition-all duration-200"
                active-class="bg-blue-500 text-white"
                exact-active-class="bg-blue-500 text-white"
              >
                <NIcon :size="22" class="text-gray-500 group-hover:text-white">
                  <component :is="item.icon" />
                </NIcon>
              </router-link>
            </template>
            {{ item.label }}
          </NTooltip>
        </div>

        <div class="absolute bottom-4 left-0 right-0 flex flex-col items-center">
          <div class="w-8 border-t border-gray-300 mb-4" />
          <NTooltip placement="right">
            <template #trigger>
              <router-link
                to="/settings"
                class="w-10 h-10 rounded-lg flex items-center justify-center cursor-pointer transition-all duration-200"
                active-class="bg-blue-500 text-white"
              >
                <NIcon :size="22" class="text-gray-500">
                  <SettingsOutline />
                </NIcon>
              </router-link>
            </template>
            设置
          </NTooltip>
        </div>
      </NLayoutSider>

      <div class="flex-1 overflow-auto">
        <router-view />
      </div>
    </div>
  </div>
  </NMessageProvider>
  </NConfigProvider>
</template>
