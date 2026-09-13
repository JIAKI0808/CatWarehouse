<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  NLayoutSider, NIcon, NTooltip, NMessageProvider, NConfigProvider, darkTheme, useDialog,
  zhCN as naiveZhCN, dateZhCN as naiveDateZhCN, enUS as naiveEnUS, dateEnUS as naiveDateEnUS,
} from 'naive-ui'
import { useI18n } from 'vue-i18n'
import {
  WalletOutline,
  AnalyticsOutline,
  SettingsOutline,
  CashOutline,
  PricetagOutline,
} from '@vicons/ionicons5'
import { useRouter } from 'vue-router'
import { useCurrencyStore } from '@/stores/currency'
import { useUnitStore } from '@/stores/units'
import MenuBar from './components/MenuBar.vue'
import IntroAnimation from './animations/IntroAnimation.vue'

const router = useRouter()
const currencyStore = useCurrencyStore()
const unitStore = useUnitStore()
const { t, locale } = useI18n()
const isDark = ref(false)
const showIntro = ref(true)

const theme = computed(() => isDark.value ? darkTheme : null)

// naive-ui 自带组件（日期选择器、分页、空状态…）的文案要单独喂语言包，
// 它**不**走 vue-i18n。不接这两个 prop 的话，切到英文后这些组件仍是中文。
const naiveLocale = computed(() => locale.value === 'en-US' ? naiveEnUS : naiveZhCN)
const naiveDateLocale = computed(() => locale.value === 'en-US' ? naiveDateEnUS : naiveDateZhCN)

onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved === 'dark') isDark.value = true
  else if (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches) isDark.value = true
  updateDarkClass()

  window.addEventListener('keydown', handleKeydown)

  // 计价货币只管一次：符号全局共用，失败静默保持默认 `¥`（见 stores/currency.ts）。
  currencyStore.fetchPreference()
  // 单位字典同理：拿不到就退回接入前的写死默认值 `个`（见 stores/units.ts）。
  unitStore.fetchUnits()
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

function handleIntroComplete() {
  showIntro.value = false
}

// computed 而非 const：文案必须随语言切换而重算。模板里 v-for 会自动解包，用法不变。
const navItems = computed(() => [
  { path: '/', label: t('app.nav.inventory'), icon: WalletOutline },
  { path: '/analytics', label: t('app.nav.analytics'), icon: AnalyticsOutline },
  { path: '/ledger', label: t('app.nav.ledger'), icon: CashOutline },
  { path: '/pricing', label: t('app.nav.pricing'), icon: PricetagOutline },
])
</script>

<template>
  <NConfigProvider :theme="theme" :locale="naiveLocale" :date-locale="naiveDateLocale">
  <NMessageProvider>
  <div class="h-screen flex flex-col">
    <IntroAnimation v-if="showIntro" @complete="handleIntroComplete" />

    <MenuBar v-show="!showIntro" :is-dark="isDark" @toggle-theme="toggleTheme" />

    <div v-show="!showIntro" class="flex-1 flex overflow-hidden">
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
            {{ t('app.nav.settings') }}
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
