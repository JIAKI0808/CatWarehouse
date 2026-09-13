<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { showSuccessToast, showFailToast } from 'vant'
import { useI18n } from 'vue-i18n'
import { translateBackendMessage } from '@/i18n'
import { useSettingsStore } from '@/stores/settings'
import { useServerConfigStore } from '@/stores/serverConfig'
import { useThemeStore } from '@/stores/theme'
import { connectionApi } from '@/services/api'

const { t } = useI18n()
const store = useSettingsStore()
const serverConfigStore = useServerConfigStore()
const themeStore = useThemeStore()

const testing = ref(false)

// 版本描述是**后端**返回的（`/api/settings/version` 的 description），前端不该去改它，
// 而是用 `translateBackendMessage()` 查 `backend.*` 对照表显示成当前语言。
// 放在 computed 里：`currentLocale()` 读的是响应式 locale，换语言会自动重算。
const versionDescription = computed(() =>
  translateBackendMessage(store.version?.description ?? '-')
)
const hostStr = ref(serverConfigStore.config.host)
const portStr = ref(String(serverConfigStore.config.port))

watch([hostStr, portStr], () => {
  const port = Number(portStr.value)
  if (Number.isNaN(port) || port <= 0) return
  serverConfigStore.config.host = hostStr.value.trim()
  serverConfigStore.config.port = port
})

onMounted(() => {
  store.fetchSettings()
  store.fetchVersion()
})

async function handleSave() {
  try {
    await store.saveSettings()
    showSuccessToast(t('app.settingsPage.saved'))
  } catch {
    showFailToast(t('app.settingsPage.saveFailed'))
  }
}

async function handleTestConnection() {
  testing.value = true
  try {
    await connectionApi.test()
    showSuccessToast(t('app.settingsPage.connectOk'))
  } catch {
    showFailToast(t('app.settingsPage.connectFailed'))
  } finally {
    testing.value = false
  }
}
</script>

<template>
  <div class="st">
    <van-nav-bar :title="t('app.settingsPage.title')" />
    <div class="page-body">
    <div class="card">
      <div class="card-title">{{ t('app.settingsPage.appearance') }}</div>
      <van-cell-group inset>
        <van-cell :title="t('app.settingsPage.darkMode')" center>
          <template #right-icon>
            <van-switch
              :model-value="themeStore.isDark"
              size="22"
              @update:model-value="themeStore.toggle()"
            />
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <div class="card">
      <div class="card-title">{{ t('app.settingsPage.serverSection') }}</div>
      <van-cell-group inset>
        <van-field
          v-model="hostStr"
          :label="t('app.settingsPage.serverHost')"
          placeholder="localhost"
        />
        <van-field
          v-model="portStr"
          type="number"
          :label="t('app.settingsPage.port')"
          placeholder="11222"
        />
      </van-cell-group>
      <div class="actions">
        <van-button
          size="small"
          plain
          type="primary"
          :loading="testing"
          @click="handleTestConnection"
        >
          {{ t('app.settingsPage.testConnection') }}
        </van-button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">{{ t('app.settingsPage.aiSection') }}</div>
      <van-cell-group inset>
        <van-field
          v-model="store.aiConfig.api_key"
          type="password"
          label="API Key"
          :placeholder="t('app.settingsPage.apiKeyPlaceholder')"
        />
        <van-field
          v-model="store.aiConfig.base_url"
          label="Base URL"
          placeholder="https://api.anthropic.com"
        />
        <van-field
          v-model="store.aiConfig.model_name"
          :label="t('app.settingsPage.modelName')"
          placeholder="claude-sonnet-4-20250514"
        />
        <van-field
          v-model="store.aiConfig.max_tokens"
          type="number"
          label="Max Tokens"
          placeholder="4096"
        />
      </van-cell-group>
      <div class="actions">
        <van-button
          size="small"
          type="primary"
          :loading="store.saving"
          @click="handleSave"
        >
          {{ t('app.settingsPage.saveConfig') }}
        </van-button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">{{ t('app.settingsPage.pluginsSection') }}</div>
      <van-cell-group inset>
        <van-cell :title="t('app.settingsPage.pluginAiCategory')" center>
          <template #right-icon>
            <van-switch v-model="store.pluginConfig.ai_category_suggestion" size="20" />
          </template>
        </van-cell>
        <van-cell :title="t('app.settingsPage.pluginSmartAutocomplete')" center>
          <template #right-icon>
            <van-switch v-model="store.pluginConfig.smart_autocomplete" size="20" />
          </template>
        </van-cell>
        <van-cell :title="t('app.settingsPage.pluginDescriptionGeneration')" center>
          <template #right-icon>
            <van-switch v-model="store.pluginConfig.description_generation" size="20" />
          </template>
        </van-cell>
        <van-cell :title="t('app.settingsPage.pluginVoiceInput')" center>
          <template #right-icon>
            <van-switch v-model="store.pluginConfig.voice_input" size="20" />
          </template>
        </van-cell>
      </van-cell-group>
      <div class="actions">
        <van-button
          size="small"
          type="primary"
          :loading="store.saving"
          @click="handleSave"
        >
          {{ t('app.settingsPage.saveConfig') }}
        </van-button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">{{ t('app.settingsPage.versionSection') }}</div>
      <van-cell-group inset>
        <van-cell :title="t('app.settingsPage.appName')" :value="store.version?.app_name ?? '-'" />
        <van-cell
          :title="t('app.settingsPage.version')"
          :value="'v' + (store.version?.version ?? '-')"
        />
        <van-cell :title="t('app.common.description')" :value="versionDescription" />
      </van-cell-group>
    </div>
    </div>
  </div>
</template>

<style scoped>
.st {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0 var(--tabbar-height);
}

.card {
  margin-bottom: 12px;
}

.card-title {
  font-size: 14px;
  color: var(--van-text-color-2);
  padding: 0 18px 8px;
}

.actions {
  padding: 8px 18px 0;
}
</style>
