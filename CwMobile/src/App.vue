<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Locale } from 'vant'
import vantZhCN from 'vant/es/locale/lang/zh-CN'
import vantEnUS from 'vant/es/locale/lang/en-US'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
const { t, locale } = useI18n()

// Vant 自带组件的文案要单独喂语言包，它**不**走 vue-i18n。
//
// ⚠️ **两条线都要接，只接 `:locale` 是不够的**（实测）：
// Vant 的 `ConfigProvider` 只做了 `provide(CONFIG_PROVIDER_KEY, props)`，
// 而 `Picker` 工具栏的「取消/确认」读的是模块级**全局** `Locale`（默认 `zh-CN`）。
// 只绑 `:locale` 时，picker 的按钮在 en-US 下**仍然是中文**（本次实测踩到）。
//
// - `Locale.use(...)`：切全局语言，覆盖 Picker/日历这类读全局的组件；
// - `:locale` prop：给走 provide/inject 的组件用，保留以防将来版本改动。
const vantLocale = computed(() => (locale.value === 'en-US' ? vantEnUS : vantZhCN))

function applyVantLocale(value: string) {
  Locale.use(value === 'en-US' ? 'en-US' : 'zh-CN', value === 'en-US' ? vantEnUS : vantZhCN)
}

watch(locale, applyVantLocale, { immediate: true })

onMounted(() => theme.apply())
</script>

<template>
  <van-config-provider :theme="theme.isDark ? 'dark' : 'light'" :locale="vantLocale">
    <div class="app-shell">
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </div>
    <van-tabbar route safe-area-inset-bottom>
      <van-tabbar-item replace to="/inventory" icon="shop-o">
        {{ t('app.nav.inventory') }}
      </van-tabbar-item>
      <van-tabbar-item replace to="/analytics" icon="chart-trending-o">
        {{ t('app.nav.analytics') }}
      </van-tabbar-item>
      <van-tabbar-item replace to="/ledger" icon="balance-list-o">
        {{ t('app.nav.ledger') }}
      </van-tabbar-item>
      <van-tabbar-item replace to="/pricing" icon="label-o">
        {{ t('app.nav.pricing') }}
      </van-tabbar-item>
      <van-tabbar-item replace to="/settings" icon="setting-o">
        {{ t('app.nav.settings') }}
      </van-tabbar-item>
    </van-tabbar>
  </van-config-provider>
</template>
