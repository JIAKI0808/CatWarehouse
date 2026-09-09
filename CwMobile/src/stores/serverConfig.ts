import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEY = 'catwarehouse-server-config'

interface ServerConfig {
  host: string
  port: number
}

function loadConfig(): ServerConfig {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return { host: 'localhost', port: 11222 }
}

export const useServerConfigStore = defineStore('serverConfig', () => {
  const config = ref<ServerConfig>(loadConfig())

  watch(config, (val) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
  }, { deep: true })

  function getBaseUrl(): string {
    return `http://${config.value.host}:${config.value.port}`
  }

  return { config, getBaseUrl }
})
