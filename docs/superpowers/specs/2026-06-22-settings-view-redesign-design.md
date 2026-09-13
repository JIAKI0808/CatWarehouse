# SettingsView 重设计 Spec

## 概述

将现有的静态 SettingsView 改造为可交互的长页面设置页，包含三个模块：模型供应商配置、插件开关、版本信息。设置数据通过后端 API 持久化存储。

## 当前状态

- `Cw_WebUi/src/views/SettingsView.vue` 是纯静态展示页，无任何交互
- 后端无设置相关 API 和数据模型
- 前端使用 Vue 3 + TypeScript + Naive UI + Tailwind CSS + Pinia

## 方案：单行 JSON 存储

数据库中用一个 `settings` 表存一行数据，用 JSON 字段承载所有配置。加新配置只需改前端，后端不用动。

## 后端设计

### 数据模型

新增 `CwServer/models/settings.py`：

```python
class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, default=1)
    ai_config = Column(JSON, default={})
    plugin_config = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Schema

新增 `CwServer/schemas/settings.py`：

```python
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

class SettingsUpdate(BaseModel):
    ai_config: AIConfig | None = None
    plugin_config: PluginConfig | None = None

class VersionResponse(BaseModel):
    app_name: str
    version: str
    description: str
    start_time: str
```

### API 接口

在 `CwServer/api/router.py` 中新增：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/settings | 获取全部设置 |
| PUT | /api/settings | 更新全部设置 |
| GET | /api/settings/version | 获取版本信息 |

版本信息接口返回：
- `app_name`: "CatWarehouse"
- `version`: 从 `Cw_WebUi/package.json` 读取
- `description`: "三级分类库存管理系统"
- `start_time`: 服务启动时间

## 前端设计

### 页面布局

长页面，三个模块依次排列，使用 Naive UI 组件：

1. **模型供应商配置**
   - `n-input`（password）: API Key
   - `n-input`: Base URL
   - `n-input`: 模型名称
   - `n-input-number`: Max Tokens
   - `n-button`: 保存配置

2. **插件功能**
   - `n-switch` × 4: AI 分类建议、智能补全、描述生成、语音输入
   - `n-button`: 保存配置

3. **版本信息**
   - 静态展示: 应用名称、版本号、描述

### 状态管理

新增 `Cw_WebUi/src/stores/settings.ts` Pinia store：

```typescript
interface SettingsState {
  ai_config: AIConfig
  plugin_config: PluginConfig
  version: VersionInfo | null
  loading: boolean
}
```

提供 actions：
- `fetchSettings()` — GET /api/settings
- `saveSettings()` — PUT /api/settings
- `fetchVersion()` — GET /api/settings/version

### API 层

在 `Cw_WebUi/src/services/api.ts` 中新增 `settingsApi`：

```typescript
export const settingsApi = {
  get: () => request<SettingsResponse>('/api/settings'),
  update: (data: SettingsUpdate) => request<SettingsResponse>('/api/settings', { method: 'PUT', body: JSON.stringify(data) }),
  getVersion: () => request<VersionResponse>('/api/settings/version'),
}
```

### 组件结构

```
SettingsView.vue
├── 模型供应商配置区块
├── 插件功能区块
└── 版本信息区块
```

保持单文件组件，不拆分子组件（三个区块逻辑简单，无需过度拆分）。

## 交互流程

1. 页面加载 → 调用 `GET /api/settings` 和 `GET /api/settings/version`
2. 用户修改配置 → 更新 Pinia store 状态
3. 用户点击保存 → 调用 `PUT /api/settings` → 显示成功提示
4. 版本信息只读展示

## 约束

- 单个函数不超过 50 行
- 单行不超过 120 字符
- 不影响现有功能
- 使用 Naive UI 组件库
