<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  NInput,
  NInputNumber,
  NSwitch,
  NButton,
  NSpin,
  NCard,
  useMessage,
} from 'naive-ui'
import { useSettingsStore } from '@/stores/settings'
import { useServerConfigStore } from '@/stores/serverConfig'
import { connectionApi } from '@/services/api'

const store = useSettingsStore()
const serverConfigStore = useServerConfigStore()
const message = useMessage()
const testing = ref(false)

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

async function handleTestConnection() {
  testing.value = true
  try {
    await connectionApi.test()
    message.success('连接成功')
  } catch {
    message.error('连接失败，请检查地址和端口')
  } finally {
    testing.value = false
  }
}
</script>

<template>
  <div class="h-full overflow-y-auto bg-gray-50">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-6">
      <h1 class="text-2xl font-bold text-center">设置</h1>

      <NSpin :show="store.loading">
        <!-- 模型供应商配置 -->
        <NCard title="模型供应商配置" :bordered="false" class="shadow-sm">
          <div class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                API Key
              </label>
              <NInput
                v-model:value="store.aiConfig.api_key"
                type="password"
                placeholder="输入 Anthropic API Key"
                show-password-on="click"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Base URL
              </label>
              <NInput
                v-model:value="store.aiConfig.base_url"
                placeholder="https://api.anthropic.com"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                模型名称
              </label>
              <NInput
                v-model:value="store.aiConfig.model_name"
                placeholder="claude-sonnet-4-20250514"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Max Tokens
              </label>
              <NInputNumber
                v-model:value="store.aiConfig.max_tokens"
                :min="1"
                :max="200000"
                class="w-full"
              />
            </div>
          </div>
          <template #footer>
            <div class="flex justify-end">
              <NButton
                type="primary"
                :loading="store.saving"
                @click="handleSave"
              >
                保存配置
              </NButton>
            </div>
          </template>
        </NCard>

        <div class="border-t border-gray-200" />

        <!-- 服务器配置 -->
        <NCard title="服务器配置" :bordered="false" class="shadow-sm">
          <div class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                服务器地址
              </label>
              <NInput
                v-model:value="serverConfigStore.config.host"
                placeholder="localhost"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                端口
              </label>
              <NInputNumber
                v-model:value="serverConfigStore.config.port"
                :min="1"
                :max="65535"
                class="w-full"
              />
            </div>
          </div>
          <template #footer>
            <div class="flex justify-end gap-2">
              <NButton :loading="testing" @click="handleTestConnection">
                测试连接
              </NButton>
            </div>
          </template>
        </NCard>

        <div class="border-t border-gray-200" />

        <!-- 插件功能 -->
        <NCard title="插件功能" :bordered="false" class="shadow-sm">
          <div>
            <div class="flex items-center justify-between py-3">
              <span class="text-sm font-medium text-gray-700">AI 分类建议</span>
              <NSwitch v-model:value="store.pluginConfig.ai_category_suggestion" />
            </div>
            <div class="flex items-center justify-between py-3">
              <span class="text-sm font-medium text-gray-700">智能补全</span>
              <NSwitch v-model:value="store.pluginConfig.smart_autocomplete" />
            </div>
            <div class="flex items-center justify-between py-3">
              <span class="text-sm font-medium text-gray-700">描述生成</span>
              <NSwitch v-model:value="store.pluginConfig.description_generation" />
            </div>
            <div class="flex items-center justify-between py-3">
              <span class="text-sm font-medium text-gray-700">语音输入</span>
              <NSwitch v-model:value="store.pluginConfig.voice_input" />
            </div>
          </div>
          <template #footer>
            <div class="flex justify-end">
              <NButton
                type="primary"
                :loading="store.saving"
                @click="handleSave"
              >
                保存配置
              </NButton>
            </div>
          </template>
        </NCard>

        <div class="border-t border-gray-200" />

        <!-- 版本信息 -->
        <NCard title="版本信息" :bordered="false" class="shadow-sm">
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">应用名称</span>
              <span class="text-sm font-medium">
                {{ store.version?.app_name ?? '-' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">版本号</span>
              <span class="text-sm font-medium">
                v{{ store.version?.version ?? '-' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">描述</span>
              <span class="text-sm font-medium">
                {{ store.version?.description ?? '-' }}
              </span>
            </div>
          </div>
        </NCard>
      </NSpin>
    </div>
  </div>
</template>
