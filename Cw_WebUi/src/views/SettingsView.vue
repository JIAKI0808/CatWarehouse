<script setup lang="ts">
import { onMounted } from 'vue'
import {
  NInput,
  NInputNumber,
  NSwitch,
  NButton,
  NSpin,
  useMessage,
} from 'naive-ui'
import { useSettingsStore } from '@/stores/settings'

const store = useSettingsStore()
const message = useMessage()

onMounted(async () => {
  await Promise.all([store.fetchSettings(), store.fetchVersion()])
})

async function handleSave() {
  try {
    await store.saveSettings()
    message.success('配置已保存')
  } catch {
    message.error('保存失败，请重试')
  }
}
</script>

<template>
  <div class="p-6 max-w-2xl mx-auto space-y-8">
    <h1 class="text-2xl font-bold">设置</h1>

    <NSpin :show="store.loading">
      <!-- 模型供应商配置 -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold">模型供应商配置</h2>
        <div class="space-y-3">
          <div>
            <label class="block text-sm text-gray-600 mb-1">API Key</label>
            <NInput
              v-model:value="store.aiConfig.api_key"
              type="password"
              placeholder="输入 Anthropic API Key"
              show-password-on="click"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Base URL</label>
            <NInput
              v-model:value="store.aiConfig.base_url"
              placeholder="https://api.anthropic.com"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">模型名称</label>
            <NInput
              v-model:value="store.aiConfig.model_name"
              placeholder="claude-sonnet-4-20250514"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Max Tokens</label>
            <NInputNumber
              v-model:value="store.aiConfig.max_tokens"
              :min="1"
              :max="200000"
              class="w-full"
            />
          </div>
        </div>
        <div class="flex justify-end">
          <NButton
            type="primary"
            :loading="store.saving"
            @click="handleSave"
          >
            保存配置
          </NButton>
        </div>
      </section>

      <hr class="my-6 border-gray-200" />

      <!-- 插件功能 -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold">插件功能</h2>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm">AI 分类建议</span>
            <NSwitch v-model:value="store.pluginConfig.ai_category_suggestion" />
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm">智能补全</span>
            <NSwitch v-model:value="store.pluginConfig.smart_autocomplete" />
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm">描述生成</span>
            <NSwitch v-model:value="store.pluginConfig.description_generation" />
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm">语音输入</span>
            <NSwitch v-model:value="store.pluginConfig.voice_input" />
          </div>
        </div>
        <div class="flex justify-end">
          <NButton
            type="primary"
            :loading="store.saving"
            @click="handleSave"
          >
            保存配置
          </NButton>
        </div>
      </section>

      <hr class="my-6 border-gray-200" />

      <!-- 版本信息 -->
      <section class="space-y-2">
        <h2 class="text-lg font-semibold">版本信息</h2>
        <div class="text-sm text-gray-600 space-y-1">
          <div class="flex justify-between">
            <span>应用名称</span>
            <span class="font-medium">{{ store.version?.app_name ?? '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span>版本号</span>
            <span class="font-medium">v{{ store.version?.version ?? '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span>描述</span>
            <span class="font-medium">{{ store.version?.description ?? '-' }}</span>
          </div>
        </div>
      </section>
    </NSpin>
  </div>
</template>
