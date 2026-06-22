<script setup lang="ts">
</script>

<template>
  <div class="p-6">
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
</template>
