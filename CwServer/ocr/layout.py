from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from ocr.types import BBox, TextLine

# ---------- 调参常量 ----------
LINE_DILATE_W = 15        # 横向膨胀核宽：把同一行的字粘连成块
LINE_DILATE_H = 3         # 纵向膨胀核高：保持行间不粘连
LINE_DILATE_ITER = 2      # 膨胀次数
LINE_MIN_HEIGHT = 6       # 文本行最小高度，滤掉噪点
LINE_MIN_WIDTH = 8        # 文本行最小宽度
TABLE_KERNEL_RATIO = 0.2  # 表格线核长 = 图像宽/高 * 该比例
TABLE_KERNEL_MIN = 30     # 表格线核长下限
TABLE_MASK_DILATE_ITER = 2  # 排除表格线时掩码的膨胀次数（盖住交点残角）
ROW_OVERLAP_RATIO = 0.5   # y 重叠超过较矮框高度的该比例即视为同一行
COL_GAP_RATIO = 0.6       # 列切分阈值 = 行高 * 该比例
HEADER_BAND = 0.22        # 无表格线时，抬头区占纵向比例
FOOTER_BAND = 0.82        # 无表格线时，落款区起始的纵向比例


@dataclass
class Region:
    """版面区域。

    kind 取值：header（抬头）/ body（明细表体）/ footer（合计与落款）。
    """

    kind: str
    bbox: BBox
    line_indices: list[int] = field(default_factory=list)


def _contour_boxes(mask: np.ndarray) -> list[BBox]:
    """取 mask 中所有外轮廓的外接框。"""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cv2.boundingRect(c) for c in contours]


def _v_overlap(a: BBox, b: BBox) -> float:
    """两个框在 y 方向的交集长度。"""
    top, bottom = max(a[1], b[1]), min(a[1] + a[3], b[1] + b[3])
    return float(max(0, bottom - top))


def _union_bbox(boxes: list[BBox], indices: list[int]) -> BBox:
    """求若干框的并集外接框。"""
    x1 = min(boxes[i][0] for i in indices)
    y1 = min(boxes[i][1] for i in indices)
    x2 = max(boxes[i][0] + boxes[i][2] for i in indices)
    y2 = max(boxes[i][1] + boxes[i][3] for i in indices)
    return (x1, y1, x2 - x1, y2 - y1)


def table_line_masks(binary: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """返回 (横线掩码, 竖线掩码)。

    做法：分别用「细长核」做形态学开运算。核长取图像尺寸的固定比例，
    因此只有明显长于单个文字的线段能存活，文字笔画不会被误判为线。
    """
    h, w = binary.shape[:2]
    hk = max(TABLE_KERNEL_MIN, int(w * TABLE_KERNEL_RATIO))
    vk = max(TABLE_KERNEL_MIN, int(h * TABLE_KERNEL_RATIO))
    horiz = cv2.morphologyEx(binary, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (hk, 1)))
    vert = cv2.morphologyEx(binary, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, vk)))
    return horiz, vert


def detect_table_lines(binary: np.ndarray) -> tuple[list[BBox], list[BBox]]:
    """检测表格线，返回 (横线框列表, 竖线框列表)。"""
    horiz, vert = table_line_masks(binary)
    return _contour_boxes(horiz), _contour_boxes(vert)


def detect_text_lines(binary: np.ndarray) -> list[BBox]:
    """检测文本行外接框。

    先剔除表格线（否则长线段会被当成一整行文本），再横向膨胀把同一行的字粘连成块，
    取外接框后滤掉过小噪点，按先上后左排序。
    """
    horiz, vert = table_line_masks(binary)
    lines_mask = cv2.bitwise_or(horiz, vert)
    # 横竖线交点处会残留几像素（线端角），不盖住会被当成小文本块，故排除前稍作膨胀。
    lines_mask = cv2.dilate(lines_mask, np.ones((3, 3), np.uint8), iterations=TABLE_MASK_DILATE_ITER)
    src = cv2.bitwise_and(binary, cv2.bitwise_not(lines_mask))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (LINE_DILATE_W, LINE_DILATE_H))
    merged = cv2.dilate(src, kernel, iterations=LINE_DILATE_ITER)
    kept = [b for b in _contour_boxes(merged) if b[3] >= LINE_MIN_HEIGHT and b[2] >= LINE_MIN_WIDTH]
    return sorted(kept, key=lambda b: (b[1], b[0]))


def group_rows(boxes: list[BBox]) -> list[list[int]]:
    """按 y 方向重叠把框聚成「行」，返回每行的框下标（行内按 x 排序）。"""
    rows: list[list[int]] = []
    for idx in sorted(range(len(boxes)), key=lambda i: (boxes[i][1], boxes[i][0])):
        for row in rows:
            ref = boxes[row[0]]
            threshold = ROW_OVERLAP_RATIO * min(boxes[idx][3], ref[3])
            if _v_overlap(boxes[idx], ref) >= threshold:
                row.append(idx)
                break
        else:
            rows.append([idx])
    for row in rows:
        row.sort(key=lambda i: boxes[i][0])
    return rows


def group_columns(indices: list[int], boxes: list[BBox]) -> list[list[int]]:
    """把同一行内的框按 x 间隔聚成「列」，返回每列的框下标。

    用于 OCR 按单元格返回多个文本框时还原列结构；间隔阈值取行高的固定比例。
    """
    if not indices:
        return []
    ordered = sorted(indices, key=lambda i: boxes[i][0])
    gap = max(1.0, max(boxes[i][3] for i in ordered) * COL_GAP_RATIO)
    cols: list[list[int]] = [[ordered[0]]]
    for idx in ordered[1:]:
        prev = boxes[cols[-1][-1]]
        if boxes[idx][0] - (prev[0] + prev[2]) > gap:
            cols.append([idx])
        else:
            cols[-1].append(idx)
    return cols


def split_regions(boxes: list[BBox], horiz_boxes: list[BBox] | None = None) -> list[Region]:
    """把版面切成 抬头 / 表体 / 落款 三段。

    有表格横线时以首末横线为界；否则按纵向比例（HEADER_BAND / FOOTER_BAND）退化切分。
    返回的 Region 只包含非空区域，line_indices 为 `boxes` 的下标。
    """
    rows = group_rows(boxes)
    if not rows:
        return []
    if horiz_boxes:
        ys = sorted(b[1] for b in horiz_boxes)
        top_edge, bottom_edge = float(ys[0]), float(ys[-1])
    else:
        bottom = float(max(b[1] + b[3] for b in boxes))
        top_edge, bottom_edge = bottom * HEADER_BAND, bottom * FOOTER_BAND

    buckets: dict[str, list[int]] = {"header": [], "body": [], "footer": []}
    for row in rows:
        center = boxes[row[0]][1] + boxes[row[0]][3] / 2.0
        kind = "header" if center < top_edge else ("footer" if center > bottom_edge else "body")
        buckets[kind].extend(row)

    regions = []
    for kind in ("header", "body", "footer"):
        if buckets[kind]:
            regions.append(Region(kind, _union_bbox(boxes, buckets[kind]), buckets[kind]))
    return regions


def group_lines_into_rows(lines: list[TextLine]) -> list[list[TextLine]]:
    """把 OCR 文本行聚成「表格行」，行内按 x 从左到右排序。

    PaddleOCR 可能把整行明细识别成一条文本（"花椒 2 12.50 25.00"），
    也可能按列切成多条；本函数统一成「行 = 若干条文本」，列拆分交给 parser。
    """
    return [[lines[i] for i in row] for row in group_rows([ln.bbox for ln in lines])]
