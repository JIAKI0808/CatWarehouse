import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AIConfig, PluginConfig, VersionResponse } from '@/types'
import { settingsApi } from '@/services/api'

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
    } finally {
      saving.value = false
    }
  }

  async function fetchVersion() {
    version.value = await settingsApi.getVersion()
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
