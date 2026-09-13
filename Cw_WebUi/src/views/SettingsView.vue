<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  NInput,
  NInputNumber,
  NSwitch,
  NButton,
  NSpin,
  NCard,
  NCollapse,
  NCollapseItem,
  NSelect,
  useMessage,
} from 'naive-ui'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '@/stores/settings'
import { useServerConfigStore } from '@/stores/serverConfig'
import { connectionApi, i18nApi } from '@/services/api'
import { translateBackendMessage } from '@/i18n'
import {
  LOCALE_LABELS,
  SUPPORTED_LOCALES,
  currentLocale,
  hasStoredLocale,
  isSupportedLocale,
  setLocale,
} from '@/i18n'

const store = useSettingsStore()
const serverConfigStore = useServerConfigStore()
const message = useMessage()
const { t } = useI18n()
const testing = ref(false)

// 选择器绑的是独立 ref，不是 i18n 的 locale：切换必须走 handleLocaleChange 才能同步后端。
const localeValue = ref<string>(currentLocale())
// 选项来自**前端**的语言清单，不是后端的 /api/i18n/locales ——
// 前端只能渲染自己打包了语言包的语言，后端可能支持更多。
const localeOptions = SUPPORTED_LOCALES.map((value) => ({
  label: LOCALE_LABELS[value],
  value,
}))

// 版本描述是**后端**返回的（`/api/settings/version` 的 description），前端不该去改它，
// 而是用 `translateBackendMessage()` 查 `backend.*` 对照表把它显示成当前语言 ——
// 这正是 P1 建那份语言包的用途，也是它的**第一个真实使用者**。
// 放在 computed 里：`currentLocale()` 读的是 i18n 的响应式 locale，换语言会自动重算。
// 查不到就原样显示后端原文（绝不显示空串）。
const versionDescription = computed(() =>
  translateBackendMessage(store.version?.description ?? '-')
)

onMounted(async () => {
  await Promise.all([store.fetchSettings(), store.fetchVersion()])
  await syncLocaleFromServer()
})

/**
 * 从后端拉语言偏好。
 *
 * 采纳规则只有一条，免得「谁覆盖谁」说不清：**本机没显式选过时才采纳后端值**。
 * 用户在本机选过的，不该被别的设备的选择覆盖。
 * 服务器不可达是正常状态 —— 静默跳过，localStorage 始终是唯一真相。
 */
async function syncLocaleFromServer() {
  try {
    const pref = await i18nApi.getPreference()
    if (!hasStoredLocale() && isSupportedLocale(pref.locale)) {
      setLocale(pref.locale)
    }
    localeValue.value = currentLocale()
  } catch {
    // 离线 / 连不上：保持本机设置，且**不提示** —— 这不是错误
  }
}

/** 切语言：本机立即生效（不等待网络），再尽力同步给后端。 */
async function handleLocaleChange(next: string) {
  localeValue.value = next
  const applied = setLocale(next)
  try {
    await i18nApi.updatePreference(applied)
  } catch {
    message.warning(t('app.settingsPage.languageSyncFailed'))
  }
}

async function handleSave() {
  try {
    await store.saveSettings()
    message.success(t('app.settingsPage.saved'))
  } catch {
    message.error(t('app.settingsPage.saveFailed'))
  }
}

async function handleTestConnection() {
  testing.value = true
  try {
    await connectionApi.test()
    message.success(t('app.settingsPage.connectOk'))
  } catch {
    message.error(t('app.settingsPage.connectFailed'))
  } finally {
    testing.value = false
  }
}
</script>

<template>
  <div class="h-full overflow-y-auto bg-gray-50">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-6">
      <h1 class="text-2xl font-bold text-center">{{ t('app.settingsPage.title') }}</h1>

      <NSpin :show="store.loading">
        <!-- 模型供应商配置 -->
        <NCard :title="t('app.settingsPage.aiProvider')" :bordered="false" class="shadow-sm">
          <div class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                API Key
              </label>
              <NInput
                v-model:value="store.aiConfig.api_key"
                type="password"
                :placeholder="t('app.settingsPage.apiKeyPlaceholder')"
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
                {{ t('app.settingsPage.modelName') }}
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
                {{ t('app.settingsPage.saveConfig') }}
              </NButton>
            </div>
          </template>
        </NCard>

        <div class="border-t border-gray-200" />

        <!-- 服务器配置 -->
        <NCard :title="t('app.settingsPage.serverSection')" :bordered="false" class="shadow-sm">
          <div class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                {{ t('app.settingsPage.serverHost') }}
              </label>
              <NInput
                v-model:value="serverConfigStore.config.host"
                placeholder="localhost"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                {{ t('app.settingsPage.port') }}
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
                {{ t('app.settingsPage.testConnection') }}
              </NButton>
            </div>
          </template>
        </NCard>

        <div class="border-t border-gray-200" />

        <!-- 插件功能 -->
        <NCard :title="t('app.settingsPage.pluginsSection')" :bordered="false" class="shadow-sm">
          <div>
            <div class="flex items-center justify-between py-3">
              <span class="text-sm font-medium text-gray-700">
                {{ t('app.settingsPage.pluginAiCategory') }}
              </span>
              <NSwitch v-model:value="store.pluginConfig.ai_category_suggestion" />
            </div>
            <div class="flex items-center justify-between py-3">
              <span class="text-sm font-medium text-gray-700">
                {{ t('app.settingsPage.pluginSmartAutocomplete') }}
              </span>
              <NSwitch v-model:value="store.pluginConfig.smart_autocomplete" />
            </div>
            <div class="flex items-center justify-between py-3">
              <span class="text-sm font-medium text-gray-700">
                {{ t('app.settingsPage.pluginDescriptionGeneration') }}
              </span>
              <NSwitch v-model:value="store.pluginConfig.description_generation" />
            </div>
            <div class="flex items-center justify-between py-3">
              <span class="text-sm font-medium text-gray-700">
                {{ t('app.settingsPage.pluginVoiceInput') }}
              </span>
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
                {{ t('app.settingsPage.saveConfig') }}
              </NButton>
            </div>
          </template>
        </NCard>

        <div class="border-t border-gray-200" />

        <!-- 语言（收纳型控件：默认折叠，不占版面，也不改动既有区块布局） -->
        <NCollapse>
          <NCollapseItem :title="t('app.settingsPage.language')" name="locale">
            <div class="flex flex-wrap items-center gap-x-3 gap-y-2">
              <NSelect
                :value="localeValue"
                :options="localeOptions"
                class="w-40"
                @update:value="handleLocaleChange"
              />
              <span class="text-xs text-gray-500">
                {{ t('app.settingsPage.languageNote') }}
              </span>
            </div>
          </NCollapseItem>
        </NCollapse>

        <div class="border-t border-gray-200" />

        <!-- 版本信息 -->
        <NCard :title="t('app.settingsPage.versionSection')" :bordered="false" class="shadow-sm">
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">{{ t('app.settingsPage.appName') }}</span>
              <span class="text-sm font-medium">
                {{ store.version?.app_name ?? '-' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">{{ t('app.settingsPage.version') }}</span>
              <span class="text-sm font-medium">
                v{{ store.version?.version ?? '-' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">{{ t('app.common.description') }}</span>
              <span class="text-sm font-medium">{{ versionDescription }}</span>
            </div>
          </div>
        </NCard>
      </NSpin>
    </div>
  </div>
</template>
