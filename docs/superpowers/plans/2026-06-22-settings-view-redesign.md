# SettingsView 重设计 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将静态 SettingsView 改造为可交互的长页面设置页，包含模型供应商配置、插件开关、版本信息三个模块，通过后端 API 持久化。

**Architecture:** 后端新增 Settings 模型（单行 JSON 存储）+ API 接口；前端新增 Pinia store + SettingsView 组件重写。遵循现有项目模式：SQLAlchemy Column 风格、Pydantic BaseModel with from_attributes、Naive UI 组件。

**Tech Stack:** FastAPI, SQLAlchemy (async), Pydantic v2, Vue 3 Composition API, Naive UI, Pinia, Tailwind CSS

## Global Constraints

- 单个函数不超过 50 行
- 单行不超过 120 字符
- 不影响现有功能
- 使用 Naive UI 组件库
- 遵循现有代码模式（SQLAlchemy Column 风格、Pydantic BaseModel）

## File Structure

### Backend (CwServer/)

| 文件 | 操作 | 职责 |
|------|------|------|
| `CwServer/models/settings.py` | 新建 | Settings 数据模型 |
| `CwServer/schemas/settings.py` | 新建 | Settings Pydantic schema |
| `CwServer/api/settings_router.py` | 新建 | Settings API 路由 |
| `CwServer/models/__init__.py` | 修改 | 注册 Settings 模型 |
| `CwServer/api/router.py` | 修改 | 引入 settings_router |
| `CwServer/catWarehouse_server.py` | 修改 | 启动时初始化默认设置 |

### Frontend (Cw_WebUi/)

| 文件 | 操作 | 职责 |
|------|------|------|
| `Cw_WebUi/src/types/index.ts` | 修改 | 新增 Settings 类型 |
| `Cw_WebUi/src/services/api.ts` | 修改 | 新增 settingsApi |
| `Cw_WebUi/src/stores/settings.ts` | 新建 | Settings Pinia store |
| `Cw_WebUi/src/views/SettingsView.vue` | 修改 | 重写为交互式长页面 |

---

### Task 1: 后端 Settings 数据模型

**Files:**
- Create: `CwServer/models/settings.py`
- Modify: `CwServer/models/__init__.py:9-11`

**Interfaces:**
- Produces: `Settings` SQLAlchemy model（供后续 API 路由使用）

- [ ] **Step 1: 创建 Settings 模型文件**

```python
# CwServer/models/settings.py
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.dialects.sqlite import JSON

from models import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, default=1)
    ai_config = Column(JSON, default=dict)
    plugin_config = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
```

- [ ] **Step 2: 注册模型到 __init__.py**

在 `CwServer/models/__init__.py` 末尾添加：

```python
from models.settings import Settings  # noqa: E402, F401
```

- [ ] **Step 3: 验证模型可导入**

Run: `cd CwServer && python -c "from models.settings import Settings; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add CwServer/models/settings.py CwServer/models/__init__.py
git commit -m "feat: add Settings model with JSON config storage"
```

---

### Task 2: 后端 Settings Schema

**Files:**
- Create: `CwServer/schemas/settings.py`

**Interfaces:**
- Produces: `AIConfig`, `PluginConfig`, `SettingsResponse`, `SettingsUpdate`, `VersionResponse`（供 API 路由使用）

- [ ] **Step 1: 创建 Schema 文件**

```python
# CwServer/schemas/settings.py
from datetime import datetime

from pydantic import BaseModel


class AIConfig(BaseModel):
    api_key: str = ""
    base_url: str = "https://api.anthropic.com"
    model_name: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096


class PluginConfig(BaseModel):
    ai_category_suggestion: bool = True
    smart_autocomplete: bool = True
    description_generation: bool = True
    voice_input: bool = False


class SettingsResponse(BaseModel):
    ai_config: AIConfig
    plugin_config: PluginConfig

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    ai_config: AIConfig | None = None
    plugin_config: PluginConfig | None = None


class VersionResponse(BaseModel):
    app_name: str
    version: str
    description: str
    start_time: str
```

- [ ] **Step 2: 验证 Schema 可导入**

Run: `cd CwServer && python -c "from schemas.settings import AIConfig, PluginConfig, SettingsResponse; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add CwServer/schemas/settings.py
git commit -m "feat: add Settings Pydantic schemas"
```

---

### Task 3: 后端 Settings API 路由

**Files:**
- Create: `CwServer/api/settings_router.py`
- Modify: `CwServer/api/router.py:1`
- Modify: `CwServer/catWarehouse_server.py:14-18`

**Interfaces:**
- Consumes: `Settings` model, `AIConfig`, `PluginConfig`, `SettingsResponse`, `SettingsUpdate`, `VersionResponse` schemas
- Produces: `GET /api/settings`, `PUT /api/settings`, `GET /api/settings/version` 接口

- [ ] **Step 1: 创建 settings_router.py**

```python
# CwServer/api/settings_router.py
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.settings import Settings
from schemas.settings import (
    AIConfig,
    PluginConfig,
    SettingsResponse,
    SettingsUpdate,
    VersionResponse,
)

router = APIRouter(prefix="/settings", tags=["settings"])

APP_VERSION = "0.1.0"
APP_NAME = "CatWarehouse"
APP_DESCRIPTION = "三级分类库存管理系统"
_start_time: str = ""


def set_start_time(t: str) -> None:
    global _start_time
    _start_time = t


async def _get_or_create_settings(db: AsyncSession) -> Settings:
    result = await db.execute(select(Settings).where(Settings.id == 1))
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = Settings(id=1, ai_config={}, plugin_config={})
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.get("", response_model=SettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    settings = await _get_or_create_settings(db)
    return SettingsResponse(
        ai_config=AIConfig(**(settings.ai_config or {})),
        plugin_config=PluginConfig(**(settings.plugin_config or {})),
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
):
    settings = await _get_or_create_settings(db)
    if data.ai_config is not None:
        settings.ai_config = data.ai_config.model_dump()
    if data.plugin_config is not None:
        settings.plugin_config = data.plugin_config.model_dump()
    await db.commit()
    await db.refresh(settings)
    return SettingsResponse(
        ai_config=AIConfig(**(settings.ai_config or {})),
        plugin_config=PluginConfig(**(settings.plugin_config or {})),
    )


@router.get("/version", response_model=VersionResponse)
async def get_version():
    return VersionResponse(
        app_name=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        start_time=_start_time,
    )
```

- [ ] **Step 2: 在主路由中引入 settings_router**

修改 `CwServer/api/router.py`，在已有 import 后添加：

```python
from api.settings_router import router as settings_router
```

在文件末尾（`router` 定义之后）添加：

```python
router.include_router(settings_router)
```

- [ ] **Step 3: 在启动时记录启动时间并设置版本号**

修改 `CwServer/catWarehouse_server.py`：

在 `lifespan` 函数中，`setup_logging()` 之后添加：

```python
from api.settings_router import set_start_time
from datetime import datetime
set_start_time(datetime.now().isoformat())
```

读取 package.json 版本号，在 `lifespan` 函数开头添加：

```python
import json
from pathlib import Path

pkg = json.loads(
    (Path(__file__).parent.parent / "Cw_WebUi" / "package.json").read_text()
)
from api.settings_router import APP_VERSION
import api.settings_router as sr
sr.APP_VERSION = pkg.get("version", "0.1.0")
```

- [ ] **Step 4: 验证 API 可启动**

Run: `cd CwServer && python -c "from api.settings_router import router; print('OK')"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add CwServer/api/settings_router.py CwServer/api/router.py CwServer/catWarehouse_server.py
git commit -m "feat: add settings API endpoints"
```

---

### Task 4: 前端 Types 与 API 层

**Files:**
- Modify: `Cw_WebUi/src/types/index.ts`
- Modify: `Cw_WebUi/src/services/api.ts`

**Interfaces:**
- Produces: `AIConfig`, `PluginConfig`, `SettingsResponse`, `SettingsUpdate`, `VersionResponse` types, `settingsApi`（供 store 和组件使用）

- [ ] **Step 1: 在 types/index.ts 末尾添加 Settings 类型**

```typescript
export interface AIConfig {
  api_key: string
  base_url: string
  model_name: string
  max_tokens: number
}

export interface PluginConfig {
  ai_category_suggestion: boolean
  smart_autocomplete: boolean
  description_generation: boolean
  voice_input: boolean
}

export interface SettingsResponse {
  ai_config: AIConfig
  plugin_config: PluginConfig
}

export interface SettingsUpdate {
  ai_config?: AIConfig
  plugin_config?: PluginConfig
}

export interface VersionResponse {
  app_name: string
  version: string
  description: string
  start_time: string
}
```

- [ ] **Step 2: 在 services/api.ts 末尾添加 settingsApi**

```typescript
export const settingsApi = {
  get: () => request<SettingsResponse>('/api/settings'),
  update: (data: SettingsUpdate) =>
    request<SettingsResponse>('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  getVersion: () => request<VersionResponse>('/api/settings/version'),
}
```

- [ ] **Step 3: Commit**

```bash
git add Cw_WebUi/src/types/index.ts Cw_WebUi/src/services/api.ts
git commit -m "feat: add Settings types and API layer"
```

---

### Task 5: 前端 Settings Store

**Files:**
- Create: `Cw_WebUi/src/stores/settings.ts`

**Interfaces:**
- Consumes: `settingsApi`, `AIConfig`, `PluginConfig`, `VersionResponse`
- Produces: `useSettingsStore`（供 SettingsView 使用）

- [ ] **Step 1: 创建 settings store**

```typescript
// Cw_WebUi/src/stores/settings.ts
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
```

- [ ] **Step 2: Commit**

```bash
git add Cw_WebUi/src/stores/settings.ts
git commit -m "feat: add settings Pinia store"
```

---

### Task 6: 前端 SettingsView 组件重写

**Files:**
- Modify: `Cw_WebUi/src/views/SettingsView.vue`

**Interfaces:**
- Consumes: `useSettingsStore`

- [ ] **Step 1: 重写 SettingsView.vue**

完整替换为：

```vue
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
```

- [ ] **Step 2: Commit**

```bash
git add Cw_WebUi/src/views/SettingsView.vue
git commit -m "feat: rewrite SettingsView as interactive settings page"
```
