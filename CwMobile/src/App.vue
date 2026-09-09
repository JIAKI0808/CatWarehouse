<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()

onMounted(() => theme.apply())
</script>

<template>
  <van-config-provider :theme="theme.isDark ? 'dark' : 'light'">
    <div class="app-main">
      <router-view />
    </div>
    <van-tabbar route safe-area-inset-bottom placeholder>
      <van-tabbar-item replace to="/inventory" icon="shop-o">库存</van-tabbar-item>
      <van-tabbar-item replace to="/analytics" icon="chart-trending-o">数据</van-tabbar-item>
      <van-tabbar-item replace to="/ledger" icon="balance-list-o">账本</van-tabbar-item>
      <van-tabbar-item replace to="/pricing" icon="label-o">售价</van-tabbar-item>
      <van-tabbar-item replace to="/settings" icon="setting-o">设置</van-tabbar-item>
    </van-tabbar>
  </van-config-provider>
</template>
