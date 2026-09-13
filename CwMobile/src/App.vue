<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import vantZhCN from 'vant/es/locale/lang/zh-CN'
import vantEnUS from 'vant/es/locale/lang/en-US'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
const { t, locale } = useI18n()

// Vant 自带组件（下拉、日历、Toast 的默认文案…）的文案要单独喂语言包，
// 它**不**走 vue-i18n。不接这个 prop 的话，切到英文后这些组件仍是中文。
const vantLocale = computed(() => (locale.value === 'en-US' ? vantEnUS : vantZhCN))

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
