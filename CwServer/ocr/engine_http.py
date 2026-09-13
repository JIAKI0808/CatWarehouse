from __future__ import annotations

import base64
import json
import logging
import urllib.error
import urllib.request

from ocr.base import OcrEngine
from ocr.response import lines_from_response
from ocr.settings import OcrSettings, load_settings
from ocr.types import TextLine, UpstreamRejectedError

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = ["image/png", "image/jpeg", "image/jpg", "image/bmp", "image/webp"]
FILE_TYPE_IMAGE = 1      # PaddleX serving 的 fileType：1 = 图片
ERROR_BODY_LIMIT = 200   # 报错时最多回显多少字符的响应体


class HttpOcrEngine(OcrEngine):
    """调用远程 PaddleX / PaddleOCR serving 的引擎。

    与 `PaddleOcrEngine`（本地自部署模型）互为替代，接口完全一致。
    **不需要安装 paddleocr/paddlepaddle**，只用标准库 `urllib`，
    因此在 Python 3.13 这类装不上 paddlepaddle 的环境里同样可用。

    请求：`POST {OCR_API_BASE}{OCR_API_PATH}`，JSON 体 `{"file": <base64>, "fileType": 1}`
    响应：形如
        {"result": {"ocrResults": [{"prunedResult": {
            "rec_texts": [...], "rec_scores": [...], "rec_polys": [...]}}]}}
    嵌套层数**不写死**，按结构递归找带 `rec_texts` 的节点，换版本不用改代码。

    配置见 `ocr/settings.py`（全部来自环境变量）。
    """

    def __init__(self, settings: OcrSettings | None = None) -> None:
        self._settings = settings or load_settings()

    def get_supported_formats(self) -> list[str]:
        return list(SUPPORTED_FORMATS)

    def _build_request(self, image: bytes) -> urllib.request.Request:
        """构造 serving 请求（base64 图片 + 可选 Bearer 鉴权）。"""
        payload = json.dumps({
            "file": base64.b64encode(image).decode("ascii"),
            "fileType": FILE_TYPE_IMAGE,
        }).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._settings.api_key:
            headers["Authorization"] = f"Bearer {self._settings.api_key}"
        return urllib.request.Request(self._settings.api_url, data=payload, headers=headers)

    def _post(self, image: bytes) -> dict:
        """发请求并解析 JSON，把网络/HTTP/JSON 错误统一转成可读的 RuntimeError。

        4xx 与 5xx **分级**（与 `voice/http_util.post_bytes` 口径一致）：
        上游说「这张图我处理不了」时抛 `UpstreamRejectedError`，端点据此回 400；
        服务自身出问题才是 503。
        """
        request = self._build_request(image)
        try:
            with urllib.request.urlopen(request, timeout=self._settings.api_timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:ERROR_BODY_LIMIT]
            message = f"OCR 服务返回 HTTP {exc.code}: {detail}"
            if 400 <= exc.code < 500:
                raise UpstreamRejectedError(message) from exc
            raise RuntimeError(message) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"无法连接 OCR 服务 {self._settings.api_url}: {exc.reason}。"
                "请确认服务已启动，且 OCR_API_BASE 正确。"
            ) from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"OCR 服务返回的不是合法 JSON: {exc}") from exc

    def recognize_lines(self, image: bytes) -> list[TextLine]:
        """调用远程服务，返回带 bbox / 置信度的文本行。

        Raises:
            RuntimeError: 连接失败、服务报错，或返回内容无法解析。
        """
        return lines_from_response(self._post(image))

    def recognize(self, image: bytes) -> str:
        """识别整图文本，按行以换行符拼接。"""
        return "\n".join(line.text for line in self.recognize_lines(image))
