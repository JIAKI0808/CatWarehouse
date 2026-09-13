import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useMessage } from '@/composables/useMessage'
import type { AIConfig, PluginConfig, VersionResponse } from '@/types'
import { settingsApi } from '@/services/api'
import { translate } from '@/i18n'

export const useSettingsStore = defineStore('settings', () => {
  const aiConfig = ref<AIConfig>({
    api_key: '',
    base_url: 'https://api.anthropic.com',
    model_name: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
  })
  const pluginConfig = ref<PluginConfig>({
    ai_category_suggestion: true,
    smart_autocomplete: true,
    description_generation: true,
    voice_input: false,
  })
  const version = ref<VersionResponse | null>(null)
  const loading = ref(false)
  const saving = ref(false)

  async function fetchSettings() {
    loading.value = true
    try {
      const data = await settingsApi.get()
      aiConfig.value = data.ai_config
      pluginConfig.value = data.plugin_config
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.fetchSettingsFailed'))
    } finally {
      loading.value = false
    }
  }

  async function saveSettings() {
    saving.value = true
    try {
      const data = await settingsApi.update({
        ai_config: aiConfig.value,
        plugin_config: pluginConfig.value,
      })
      aiConfig.value = data.ai_config
      pluginConfig.value = data.plugin_config
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.saveSettingsFailed'))
    } finally {
      saving.value = false
    }
  }

  async function fetchVersion() {
    try {
      version.value = await settingsApi.getVersion()
    } catch (e: any) {
      useMessage().error(e.message || translate('app.stores.fetchVersionFailed'))
    }
  }

  return {
    aiConfig,
    pluginConfig,
    version,
    loading,
    saving,
    fetchSettings,
    saveSettings,
    fetchVersion,
  }
})
