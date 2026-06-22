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
