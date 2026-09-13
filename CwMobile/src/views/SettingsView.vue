<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { showSuccessToast, showFailToast } from 'vant'
import { useSettingsStore } from '@/stores/settings'
import { useServerConfigStore } from '@/stores/serverConfig'
import { useThemeStore } from '@/stores/theme'
import { connectionApi } from '@/services/api'

const store = useSettingsStore()
const serverConfigStore = useServerConfigStore()
const themeStore = useThemeStore()

const testing = ref(false)
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
    showSuccessToast('配置已保存')
  } catch {
    showFailToast('保存失败，请重试')
  }
}

async function handleTestConnection() {
  testing.value = true
  try {
    await connectionApi.test()
    showSuccessToast('连接成功')
  } catch {
    showFailToast('连接失败，请检查地址和端口')
  } finally {
    testing.value = false
  }
}
</script>

<template>
  <div class="st">
    <van-nav-bar title="设置" />
    <div class="page-body">
    <div class="card">
      <div class="card-title">外观</div>
      <van-cell-group inset>
        <van-cell title="深色模式" center>
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
      <div class="card-title">服务器配置</div>
      <van-cell-group inset>
        <van-field v-model="hostStr" label="服务器地址" placeholder="localhost" />
        <van-field v-model="portStr" type="number" label="端口" placeholder="11222" />
      </van-cell-group>
      <div class="actions">
        <van-button
          size="small"
          plain
          type="primary"
          :loading="testing"
          @click="handleTestConnection"
        >
          测试连接
        </van-button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">模型供应商配置</div>
      <van-cell-group inset>
        <van-field
          v-model="store.aiConfig.api_key"
          type="password"
          label="API Key"
          placeholder="输入 API Key"
        />
        <van-field
          v-model="store.aiConfig.base_url"
          label="Base URL"
          placeholder="https://api.anthropic.com"
        />
        <van-field
          v-model="store.aiConfig.model_name"
          label="模型名称"
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
          保存配置
        </van-button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">插件功能</div>
      <van-cell-group inset>
        <van-cell title="AI 分类建议" center>
          <template #right-icon>
            <van-switch v-model="store.pluginConfig.ai_category_suggestion" size="20" />
          </template>
        </van-cell>
        <van-cell title="智能补全" center>
          <template #right-icon>
            <van-switch v-model="store.pluginConfig.smart_autocomplete" size="20" />
          </template>
        </van-cell>
        <van-cell title="描述生成" center>
          <template #right-icon>
            <van-switch v-model="store.pluginConfig.description_generation" size="20" />
          </template>
        </van-cell>
        <van-cell title="语音输入" center>
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
          保存配置
        </van-button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">版本信息</div>
      <van-cell-group inset>
        <van-cell title="应用名称" :value="store.version?.app_name ?? '-'" />
        <van-cell title="版本号" :value="'v' + (store.version?.version ?? '-')" />
        <van-cell title="描述" :value="store.version?.description ?? '-'" />
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
