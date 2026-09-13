from __future__ import annotations

from typing import Any

import numpy as np

from ocr.types import BBox, TextLine


def poly_to_bbox(poly: Any) -> BBox:
    """把四点框（或矩形）统一成轴对齐 (x, y, w, h)。"""
    points = np.asarray(poly, dtype=float).reshape(-1, 2)
    x1, y1 = float(points[:, 0].min()), float(points[:, 1].min())
    x2, y2 = float(points[:, 0].max()), float(points[:, 1].max())
    return (int(x1), int(y1), int(x2 - x1), int(y2 - y1))


def lines_from_rec_dict(node: dict) -> list[TextLine]:
    """解析带 rec_texts / rec_scores / rec_polys 的字典。

    PaddleOCR 3.x 本地结果与 PaddleX serving 的 `prunedResult` 是同一种形状，
    所以本地引擎与 HTTP 引擎共用本函数。
    """
    texts = node.get("rec_texts") or []
    scores = list(node.get("rec_scores") or [])
    polys = list(node.get("rec_polys") or node.get("dt_polys") or [])
    lines: list[TextLine] = []
    for index, text in enumerate(texts):
        bbox = poly_to_bbox(polys[index]) if index < len(polys) else (0, 0, 0, 0)
        confidence = float(scores[index]) if index < len(scores) else 1.0
        lines.append(TextLine(str(text), bbox, confidence))
    return lines


def find_rec_dicts(node: Any) -> list[dict]:
    """递归找出所有带 rec_texts 的字典节点。

    PaddleX serving 把结果埋在 `result.ocrResults[].prunedResult` 里，
    版本间嵌套层数会变，故按**结构**找而不是写死路径 —— 换版本不用改代码。
    """
    found: list[dict] = []
    if isinstance(node, dict):
        if "rec_texts" in node:
            found.append(node)
            return found
        for value in node.values():
            found.extend(find_rec_dicts(value))
    elif isinstance(node, (list, tuple)):
        for value in node:
            found.extend(find_rec_dicts(value))
    return found


def lines_from_page(page: Any) -> list[TextLine]:
    """解析「单页」结果，兼容两种已知形状：

    - 2.x: `[[quad, (text, score)], ...]`
    - 3.x / PaddleX: `{"rec_texts": [...], "rec_scores": [...], "rec_polys": [...]}`
    """
    if isinstance(page, dict):
        return lines_from_rec_dict(page)
    lines: list[TextLine] = []
    for item in page or []:
        try:
            quad, text, confidence = item[0], item[1][0], item[1][1]
        except (TypeError, IndexError, KeyError):
            continue
        lines.append(TextLine(str(text), poly_to_bbox(quad), float(confidence)))
    return lines


def lines_from_response(payload: Any) -> list[TextLine]:
    """解析「整个 HTTP 响应体」，自动定位 rec_texts 所在层级。

    找不到 rec_texts 时退化为按单页列表形状解析（兼容 2.x 风格的接口）。
    """
    if isinstance(payload, dict) and "rec_texts" in payload:
        return lines_from_rec_dict(payload)
    lines = [line for node in find_rec_dicts(payload) for line in lines_from_rec_dict(node)]
    return lines or lines_from_page(payload)
