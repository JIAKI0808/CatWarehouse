<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { showSuccessToast, showFailToast } from 'vant'
import { useI18n } from 'vue-i18n'
import {
  DEFAULT_LOCALE,
  LOCALE_LABELS,
  SUPPORTED_LOCALES,
  currentLocale,
  hasStoredLocale,
  isSupportedLocale,
  setLocale,
  translateBackendMessage,
} from '@/i18n'
import { useSettingsStore } from '@/stores/settings'
import { useServerConfigStore } from '@/stores/serverConfig'
import { useThemeStore } from '@/stores/theme'
import { connectionApi, currencyApi, i18nApi } from '@/services/api'
import { useCurrencyStore } from '@/stores/currency'

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

// 语言选择器。**收纳型控件**：平时只占一行 van-cell，点开才是动作面板，
// 不往设置页里堆一排语言按钮。
const showLangSheet = ref(false)
// 显式 `ref<string>`：动作面板回调给的是 `string | undefined`，
// 若让它推断成 `AppLocale`，赋值处会因收窄不上而报 TS2322。
const langValue = ref<string>(currentLocale())
const langActions = SUPPORTED_LOCALES.map((value) => ({
  name: LOCALE_LABELS[value],
  value,
}))

// 走一次 `isSupportedLocale` 收窄，模板里才能安全索引 `LOCALE_LABELS`。
const langLabel = computed(() =>
  isSupportedLocale(langValue.value)
    ? LOCALE_LABELS[langValue.value]
    : LOCALE_LABELS[DEFAULT_LOCALE]
)

// 货币：同样是**收纳型** —— 一行 cell + 一个动作面板，不新增区块。
// 选项来自后端 `GET /api/currencies`（不在前端写死清单）。
const currencyStore = useCurrencyStore()
const showCurrencySheet = ref(false)
const currencyActions = ref<{ name: string; value: string }[]>([])

async function loadCurrencyActions() {
  try {
    const list = await currencyApi.getAll()
    currencyActions.value = list.map((c) => ({
      name: `${c.symbol} ${c.code}`,
      value: c.code,
    }))
  } catch {
    // 离线：面板为空，切换会走 handleCurrencySelect 的失败分支
  }
}

/** 切货币：本机立即生效（不等待网络），再尽力同步给后端。 */
async function handleCurrencySelect(action: { value?: string }) {
  showCurrencySheet.value = false
  if (!action.value) return
  try {
    const applied = await currencyApi.updatePreference(action.value)
    currencyStore.code = applied.code
    currencyStore.symbol = applied.symbol
  } catch {
    showFailToast(t('app.settingsPage.currencySyncFailed'))
  }
}

onMounted(() => {
  store.fetchSettings()
  store.fetchVersion()
  syncLocaleFromServer()
  loadCurrencyActions()
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
    langValue.value = currentLocale()
  } catch {
    // 离线 / 连不上：保持本机设置，且**不提示** —— 这不是错误
  }
}

/** 切语言：本机立即生效（不等待网络），再尽力同步给后端。 */
async function handleLocaleSelect(action: { value?: string }) {
  showLangSheet.value = false
  const next = action.value ?? DEFAULT_LOCALE
  langValue.value = next
  const applied = setLocale(next)
  try {
    await i18nApi.updatePreference(applied)
  } catch {
    showFailToast(t('app.settingsPage.languageSyncFailed'))
  }
}

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
        <!-- 语言：收纳型 —— 平时一行 cell，点开才是动作面板 -->
        <van-cell
          :title="t('app.settingsPage.language')"
          :value="langLabel"
          is-link
          @click="showLangSheet = true"
        />
        <!-- 货币：与「语言」并排的第二行，同一个卡片内的收纳型入口 -->
        <van-cell
          :title="t('app.settingsPage.currency')"
          :value="currencyStore.code"
          is-link
          @click="showCurrencySheet = true"
        />
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

    <van-action-sheet
      v-model:show="showLangSheet"
      :actions="langActions"
      :cancel-text="t('app.common.cancel')"
      @select="handleLocaleSelect"
    />

    <van-action-sheet
      v-model:show="showCurrencySheet"
      :actions="currencyActions"
      :cancel-text="t('app.common.cancel')"
      @select="handleCurrencySelect"
    />
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
