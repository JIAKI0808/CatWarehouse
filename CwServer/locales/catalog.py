"""语言包的发现、归一化与加载。

设计要点：

1. **按文件名自动发现**，不维护语言清单常量 —— 新增语言只需丢一个 JSON 文件进来。
2. **归一化语言标签**：`zh` / `zh_CN` / `ZH-cn` 都归到 `zh-CN`。
   归一化是必需的，因为 `Accept-Language`、浏览器 `navigator.language`、
   以及各端 localStorage 里存的历史值，写法都不统一。
3. **加载结果缓存**：语言包是只读的静态资源，每个请求都读盘没有意义。
   代价是**改了 JSON 要重启服务才生效**（开发期注意事项，已写进 docstring）。
4. 找不到语言包时**抛异常而不是回退到默认语言** —— 回退会让调用方以为拿到了译文，
   实际拿到的是另一种语言。404 比静默的错误内容好。
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent

#: 语言包缺失或语言标签认不出时使用；必须存在于 LOCALES_DIR 下。
DEFAULT_LOCALE = "zh-CN"

#: 短码 / 非标准写法 → 本目录下的规范标签。仅当目标语言包**确实存在**时才生效。
_ALIASES = {
    "zh": "zh-CN",
    "zh-hans": "zh-CN",
    "zh-sg": "zh-CN",
    "en": "en-US",
    "en-gb": "en-US",
}


class UnknownLocaleError(LookupError):
    """语言包不存在，或语言标签无法归一化。"""


@lru_cache(maxsize=1)
def _index() -> dict[str, Path]:
    """locale → 语言包路径。扫描目录得到，不写死清单。"""
    return {path.stem: path for path in sorted(LOCALES_DIR.glob("*.json"))}


def available_locales() -> list[str]:
    """本目录下实际存在的全部 locale，已排序。"""
    return sorted(_index())


def default_locale() -> str:
    """默认 locale；若 DEFAULT_LOCALE 的文件不在，退到排序后的第一个。"""
    known = _index()
    if DEFAULT_LOCALE in known:
        return DEFAULT_LOCALE
    remaining = sorted(known)
    if not remaining:
        raise UnknownLocaleError(f"no locale files under {LOCALES_DIR}")
    return remaining[0]


def normalize(locale: str | None) -> str | None:
    """把任意写法的语言标签归一成可用 locale；认不出返回 None。

    只返回**确实存在语言包**的标签 —— 别名表指向不存在的语言时同样返回 None，
    否则调用方会拿到一个下一秒就 404 的标签。
    """
    if not locale or not locale.strip():
        return None
    known = _index()
    key = locale.strip().replace("_", "-").lower()
    for candidate in known:
        if candidate.lower() == key:
            return candidate
    alias = _ALIASES.get(key)
    return alias if alias in known else None


@lru_cache(maxsize=None)
def load_messages(locale: str) -> dict:
    """读取某个 locale 的语言包（含 `_meta`）。

    缓存由 `lru_cache` 负责，故**改了 JSON 需要重启服务**才生效。
    """
    resolved = normalize(locale)
    if resolved is None:
        raise UnknownLocaleError(f"unknown locale: {locale!r}")
    try:
        raw = _index()[resolved].read_text(encoding="utf-8")
        return json.loads(raw)
    except (OSError, ValueError) as exc:
        raise UnknownLocaleError(f"{resolved} is unreadable: {exc}") from exc


def lookup(locale: str, backend_message: str) -> str | None:
    """把后端原文（如 `Category not found`）译成目标语言；没有译文返回 None。

    调用方拿到 None 时应当**回退显示原文**，而不是显示空串 ——
    后端文案没进语言包是常见情形（新增端点时容易漏），原文总比空白强。
    """
    messages = load_messages(locale)
    table = messages.get("backend_messages")
    if not isinstance(table, dict):
        return None
    translated = table.get(backend_message)
    return translated if isinstance(translated, str) else None
