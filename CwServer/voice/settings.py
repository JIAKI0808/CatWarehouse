from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

ASR_ENGINE_LOCAL = "local"
ASR_ENGINE_HTTP = "http"
DEFAULT_ASR_ENGINE = ASR_ENGINE_LOCAL

LLM_PROVIDER_OPENAI = "openai"
LLM_PROVIDER_CLAUDE = "claude"
DEFAULT_LLM_PROVIDER = LLM_PROVIDER_OPENAI

DEFAULT_WHISPER_MODEL = "small"
DEFAULT_WHISPER_DEVICE = "cpu"
DEFAULT_WHISPER_COMPUTE = "int8"
DEFAULT_ASR_LANG = "zh"
LANG_AUTO = "auto"
DEFAULT_ASR_PATH = "/audio/transcriptions"
DEFAULT_ASR_MODEL = "whisper-1"
DEFAULT_ASR_TIMEOUT = 60.0

DEFAULT_CLAUDE_BASE = "https://api.anthropic.com"
DEFAULT_CLAUDE_PATH = "/v1/messages"
DEFAULT_CLAUDE_MODEL = "claude-sonnet-5"
DEFAULT_OPENAI_PATH = "/chat/completions"
DEFAULT_LLM_TIMEOUT = 60.0
DEFAULT_LLM_MAX_TOKENS = 1024


def _text(env: Mapping[str, str], key: str, default: str = "") -> str:
    """取字符串配置；未设置或为空时回退默认值。"""
    return (env.get(key) or default).strip()


def _number(env: Mapping[str, str], key: str, default: float) -> float:
    """取数值配置；非法值或非正数回退默认。"""
    try:
        value = float(_text(env, key))
    except ValueError:
        return default
    return value if value > 0 else default


def _flag(env: Mapping[str, str], key: str, default: bool) -> bool:
    """取布尔配置；0/false/no/off 视为假。"""
    value = _text(env, key).lower()
    if not value:
        return default
    return value not in ("0", "false", "no", "off")


def _lang(env: Mapping[str, str]) -> str:
    """取语言提示；填 `auto` 表示交给引擎自动检测（否则中文短句容易识别成别的语种）。"""
    value = _text(env, "VOICE_ASR_LANG", DEFAULT_ASR_LANG)
    return "" if value.lower() == LANG_AUTO else value


@dataclass(frozen=True)
class AsrSettings:
    """语音识别配置，全部来自环境变量。

    环境变量：
        VOICE_ASR_ENGINE   local | http，默认 local（本地自部署 whisper）
        VOICE_WHISPER_MODEL 本地模型名/大小，默认 small
        VOICE_WHISPER_DEVICE / VOICE_WHISPER_COMPUTE  本地推理设备与量化，默认 cpu / int8
        VOICE_ASR_LANG    语言提示，默认 zh；填 auto 交给引擎自动检测
        VOICE_ASR_BASE    http 模式的接口地址，如 http://127.0.0.1:9000
        VOICE_ASR_PATH    接口路径，默认 /audio/transcriptions
        VOICE_ASR_KEY     可选，会以 Authorization: Bearer 发送
        VOICE_ASR_MODEL   http 模式下的模型名，默认 whisper-1
        VOICE_ASR_TIMEOUT 请求超时秒数，默认 60
    """

    engine: str = DEFAULT_ASR_ENGINE
    model: str = DEFAULT_WHISPER_MODEL
    device: str = DEFAULT_WHISPER_DEVICE
    compute: str = DEFAULT_WHISPER_COMPUTE
    lang: str = DEFAULT_ASR_LANG
    api_base: str = ""
    api_path: str = DEFAULT_ASR_PATH
    api_key: str = ""
    api_model: str = DEFAULT_ASR_MODEL
    api_timeout: float = DEFAULT_ASR_TIMEOUT

    @property
    def api_url(self) -> str:
        """拼好的语音接口地址（容忍两侧多余斜杠）。"""
        if not self.api_base:
            return ""
        return f"{self.api_base.rstrip('/')}/{self.api_path.lstrip('/')}"

    def use_http(self) -> bool:
        """是否走远程语音接口。

        `VOICE_ASR_ENGINE=http` 但没配 `VOICE_ASR_BASE` 时**自动退回本地**，
        与 `ocr/settings.py` 的策略一致：配置写一半不至于把功能全打死。
        """
        return self.engine == ASR_ENGINE_HTTP and bool(self.api_base)


def load_asr_settings(env: Mapping[str, str] | None = None) -> AsrSettings:
    """从环境变量读取语音识别配置（可传 env 便于测试）。"""
    source = os.environ if env is None else env
    engine = _text(source, "VOICE_ASR_ENGINE", DEFAULT_ASR_ENGINE).lower()
    if engine not in (ASR_ENGINE_LOCAL, ASR_ENGINE_HTTP):
        engine = DEFAULT_ASR_ENGINE
    return AsrSettings(
        engine=engine,
        model=_text(source, "VOICE_WHISPER_MODEL", DEFAULT_WHISPER_MODEL),
        device=_text(source, "VOICE_WHISPER_DEVICE", DEFAULT_WHISPER_DEVICE),
        compute=_text(source, "VOICE_WHISPER_COMPUTE", DEFAULT_WHISPER_COMPUTE),
        lang=_lang(source),
        api_base=_text(source, "VOICE_ASR_BASE"),
        api_path=_text(source, "VOICE_ASR_PATH", DEFAULT_ASR_PATH),
        api_key=_text(source, "VOICE_ASR_KEY"),
        api_model=_text(source, "VOICE_ASR_MODEL", DEFAULT_ASR_MODEL),
        api_timeout=_number(source, "VOICE_ASR_TIMEOUT", DEFAULT_ASR_TIMEOUT),
    )


@dataclass(frozen=True)
class LlmSettings:
    """大模型配置，全部来自环境变量。

    环境变量：
        VOICE_LLM_PROVIDER   openai | claude，默认 openai
        VOICE_LLM_BASE       接口地址；claude 未配时默认 https://api.anthropic.com
        VOICE_LLM_PATH       接口路径；留空则按 provider 取默认
        VOICE_LLM_KEY        API Key（本地 Ollama 这类无需鉴权的服务可留空）
        VOICE_LLM_MODEL      模型名；留空则按 provider 取默认
        VOICE_LLM_TIMEOUT    请求超时秒数，默认 60
        VOICE_LLM_MAX_TOKENS 最大生成长度，默认 1024
        VOICE_LLM_JSON_MODE  1/0，是否发 response_format=json_object，默认 1

    「按 provider 取默认」刻意**不写死在字段默认值上**，而是放在
    `resolved_base()` / `resolved_path()` / `resolved_model()` 里。
    否则直接构造本类（例如走 `create_recognizer(llm_settings=…)`）时，
    `provider=claude` 会漏配成 OpenAI 的 `/chat/completions` 与空模型名
    —— 这个坑在 Phase 3 实测中确实踩到过。
    """

    provider: str = DEFAULT_LLM_PROVIDER
    api_base: str = ""
    api_path: str = ""
    api_key: str = ""
    model: str = ""
    timeout: float = DEFAULT_LLM_TIMEOUT
    max_tokens: int = DEFAULT_LLM_MAX_TOKENS
    json_mode: bool = True

    def use_claude(self) -> bool:
        """是否走 Claude 原生 Messages 接口。"""
        return self.provider == LLM_PROVIDER_CLAUDE

    def resolved_base(self) -> str:
        """接口地址；未配置时 Claude 用官方地址。

        OpenAI 兼容侧**不给默认**：那可能是任意自建服务，猜不如让调用方显式配，
        未配时 `post_bytes` 会给出「未配置 VOICE_LLM_BASE」的明确报错。
        """
        if self.api_base:
            return self.api_base
        return DEFAULT_CLAUDE_BASE if self.use_claude() else ""

    def resolved_path(self) -> str:
        """接口路径；未显式配置时按 provider 取默认。"""
        if self.api_path:
            return self.api_path
        return DEFAULT_CLAUDE_PATH if self.use_claude() else DEFAULT_OPENAI_PATH

    def resolved_model(self) -> str:
        """模型名；未显式配置时按 provider 取默认（OpenAI 兼容侧无默认可言，仍为空）。"""
        if self.model:
            return self.model
        return DEFAULT_CLAUDE_MODEL if self.use_claude() else ""

    @property
    def api_url(self) -> str:
        """拼好的大模型接口地址（容忍两侧多余斜杠）。"""
        base = self.resolved_base()
        if not base:
            return ""
        return f"{base.rstrip('/')}/{self.resolved_path().lstrip('/')}"


def load_llm_settings(env: Mapping[str, str] | None = None) -> LlmSettings:
    """从环境变量读取大模型配置（可传 env 便于测试）。

    只负责读环境变量，**不在这里算 provider 默认值** ——
    那是 `resolved_base/path/model()` 的职责，避免默认值散落成两份。
    """
    source = os.environ if env is None else env
    provider = _text(source, "VOICE_LLM_PROVIDER", DEFAULT_LLM_PROVIDER).lower()
    if provider not in (LLM_PROVIDER_OPENAI, LLM_PROVIDER_CLAUDE):
        provider = DEFAULT_LLM_PROVIDER
    return LlmSettings(
        provider=provider,
        api_base=_text(source, "VOICE_LLM_BASE"),
        api_path=_text(source, "VOICE_LLM_PATH"),
        api_key=_text(source, "VOICE_LLM_KEY"),
        model=_text(source, "VOICE_LLM_MODEL"),
        timeout=_number(source, "VOICE_LLM_TIMEOUT", DEFAULT_LLM_TIMEOUT),
        max_tokens=int(_number(source, "VOICE_LLM_MAX_TOKENS", DEFAULT_LLM_MAX_TOKENS)),
        json_mode=_flag(source, "VOICE_LLM_JSON_MODE", True),
    )
