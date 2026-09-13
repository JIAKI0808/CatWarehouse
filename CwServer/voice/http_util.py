from __future__ import annotations

import json
import urllib.error
import urllib.request

from voice.types import UpstreamRejectedError

ERROR_BODY_LIMIT = 200


def preview(payload: object) -> str:
    """把响应对象截断成可读的一小段，用于错误信息里回显。"""
    return json.dumps(payload, ensure_ascii=False)[:ERROR_BODY_LIMIT]


def post_bytes(url: str, body: bytes, headers: dict, timeout: float,
               service: str, base_key: str) -> dict:
    """POST 一段请求体并解析 JSON 响应。

    本模块是**三处 HTTP 调用点（语音识别 / OpenAI 兼容 / Claude）共用的出口**，
    把三类失败统一转成可读的 `RuntimeError`，使三处的报错口径一致：

      - 没配地址      -> 明说缺哪个环境变量
      - 上游 4xx       -> `UpstreamRejectedError`（**素材无效**，调用方应回 400）
      - 上游 5xx       -> `RuntimeError`（**服务出问题**，调用方应回 503）
      - 连不上/超时     -> `RuntimeError`，含服务名、实际地址与排查提示
      - 响应不是 JSON   -> `RuntimeError`

    调用方只需 `except RuntimeError` 就能兜住除 4xx 外的全部失败
    （`UpstreamRejectedError` 也继承它，故端点的 `except` 顺序要把它放在前面）。

    Args:
        service:  错误文案里的服务名，如「语音服务」「大模型接口」。
        base_key: 对应地址的环境变量名，如 `VOICE_ASR_BASE`，用于排查提示。
    """
    if not url:
        raise RuntimeError(f"未配置 {base_key}，无法调用{service}")
    request = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:ERROR_BODY_LIMIT]
        message = f"{service}返回 HTTP {exc.code}: {detail}"
        if 400 <= exc.code < 500:
            # 上游说「你给的素材我处理不了」——是输入问题，不是服务故障
            raise UpstreamRejectedError(message) from exc
        raise RuntimeError(message) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"无法连接{service} {url}: {exc.reason}。请确认服务已启动，且 {base_key} 正确。"
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{service}返回的不是合法 JSON: {exc}") from exc
