from __future__ import annotations

import math
from dataclasses import dataclass, field

import cv2
import numpy as np

# ---------- 调参常量（票据场景经验值，均为奇数或比例阈值） ----------
MAX_SIDE = 2400          # 长边上限：超过则等比缩小，控制后续算子耗时
MIN_SIDE = 1000          # 短边下限：不足则等比放大，提升小字识别率
BLUR_KSIZE = 5           # 高斯模糊核
CANNY_LOW = 50           # Canny 低阈值
CANNY_HIGH = 150         # Canny 高阈值
CONTOUR_TOP_N = 8        # 只检查面积最大的前 N 个轮廓，避免逐个 approxPolyDP
QUAD_AREA_RATIO = 0.2    # 文档四边形面积至少占整图的比例，过滤小噪点
QUAD_FRAME_RATIO = 0.75  # 四边形外接框在**宽和高两个方向**都必须覆盖画面的该比例
SKEW_MIN_ANGLE = 0.3     # 倾斜角小于该值视为无需校正（度）
SHADOW_KSIZE = 41        # 去阴影的背景估计核
ADAPTIVE_BLOCK = 31      # 自适应阈值邻域
ADAPTIVE_C = 15          # 自适应阈值常数
OTSU_MIN_RATIO = 0.002   # Otsu 前景占比合理区间下限
OTSU_MAX_RATIO = 0.5     # Otsu 前景占比合理区间上限
MIN_TEXT_PIXELS = 50     # 估计倾斜角所需的最少前景像素


@dataclass
class PreprocessResult:
    """预处理输出。

    image 与 binary 的尺寸严格一致，因此二者坐标空间相同：
    后续 OCR 的 bbox 与版面分析的区域框可直接互相比较。

    Attributes:
        image: 处理后的 BGR 图，供 OCR 引擎使用。
        binary: 前景(文字/线条)=255 的二值图，供版面分析使用。
        meta: 变换元信息（原始尺寸、是否透视矫正、倾斜角、最终尺寸）。
    """

    image: np.ndarray
    binary: np.ndarray
    meta: dict = field(default_factory=dict)


def load_image(data: bytes) -> np.ndarray:
    """把图片字节解码为 BGR ndarray。"""
    if not data:
        raise ValueError("empty image data")
    buf = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("cannot decode image data as an image")
    return img


def to_gray(img: np.ndarray) -> np.ndarray:
    """转灰度；已是单通道则原样返回。"""
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def denoise(gray: np.ndarray) -> np.ndarray:
    """保边去噪。bilateral 比高斯更能保住笔画边缘，利于小字识别。"""
    return cv2.bilateralFilter(gray, 5, 50, 50)


def _normalize_tilt(angle_deg: float) -> float:
    """把任意角度归一到 [-45, 45)，即相对水平线的偏角。"""
    a = float(angle_deg) % 90.0
    if a >= 45.0:
        a -= 90.0
    return a


def estimate_skew_angle(gray: np.ndarray) -> float:
    """估计文本倾斜角（度）。

    正值表示文本相对水平线**顺时针**倾斜了该角度。校正时直接 `rotate(img, angle)`：
    `rotate` 正值=逆时针，恰好抵消顺时针倾斜（负值同理反向抵消）。

    做法：Otsu 反相取前景像素 → minAreaRect 求最小外接矩形的边方向 → 归一化到 [-45,45)。
    """
    thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    pts = cv2.findNonZero(thr)
    if pts is None or len(pts) < MIN_TEXT_PIXELS:
        return 0.0
    box = cv2.boxPoints(cv2.minAreaRect(pts))
    edge = box[1] - box[0]
    return _normalize_tilt(math.degrees(math.atan2(float(edge[1]), float(edge[0]))))


def rotate(img: np.ndarray, angle_deg: float) -> np.ndarray:
    """绕中心旋转（正值=逆时针），扩展画布并以白色填充边缘。"""
    if abs(angle_deg) < SKEW_MIN_ANGLE:
        return img
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle_deg, 1.0)
    cos, sin = abs(m[0, 0]), abs(m[0, 1])
    nw, nh = int(h * sin + w * cos), int(h * cos + w * sin)
    m[0, 2] += nw / 2.0 - w / 2.0
    m[1, 2] += nh / 2.0 - h / 2.0
    border = (255, 255, 255) if img.ndim == 3 else 255
    return cv2.warpAffine(img, m, (nw, nh), borderValue=border)


def spans_frame(quad: np.ndarray, shape: tuple[int, ...]) -> bool:
    """四边形是否在宽、高两个方向都几乎撑满画面。

    只按**面积**判定不够：票据内部的大表格框、页面边框这类「内部大矩形」面积也不小。
    实测一张 1000x720 的送货单，表格外框占画面 31.9%（超 `QUAD_AREA_RATIO`），
    宽度覆盖 90% 但高度只覆盖 35% —— 把它当成文档边界去透视矫正，
    会把整张票据拉成 3.6:1 的长条，OCR 直接失效。
    真正「拍文档」的照片里，文档在两个方向上都会撑满画面，故要求**宽高同时**达标。
    """
    height, width = shape[0], shape[1]
    xs, ys = quad[:, 0], quad[:, 1]
    span_x = (float(xs.max()) - float(xs.min())) / width
    span_y = (float(ys.max()) - float(ys.min())) / height
    return span_x >= QUAD_FRAME_RATIO and span_y >= QUAD_FRAME_RATIO


def find_document_quad(gray: np.ndarray) -> np.ndarray | None:
    """检测票据外接四边形，返回 4x2 的 float32 点集；找不到返回 None。

    只有「在宽高两个方向都几乎撑满画面」的四边形才被当作文档边界，
    否则宁可不做透视矫正 —— 矫正错了会把图毁掉，而不矫正只是保留一点透视，
    代价远小于前者（见 `spans_frame` 的实测说明）。
    """
    blur = cv2.GaussianBlur(gray, (BLUR_KSIZE, BLUR_KSIZE), 0)
    edges = cv2.dilate(cv2.Canny(blur, CANNY_LOW, CANNY_HIGH), np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    area = float(gray.shape[0] * gray.shape[1])
    for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:CONTOUR_TOP_N]:
        if cv2.contourArea(cnt) < area * QUAD_AREA_RATIO:
            break
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            quad = approx.reshape(4, 2).astype(np.float32)
            if spans_frame(quad, gray.shape):
                return quad
    return None


def order_quad_points(quad: np.ndarray) -> np.ndarray:
    """把 4 点排序为 左上 / 右上 / 右下 / 左下。"""
    pts = quad.reshape(4, 2).astype(np.float32)
    total = pts.sum(axis=1)
    diff = pts[:, 0] - pts[:, 1]
    return np.array(
        [pts[np.argmin(total)], pts[np.argmax(diff)], pts[np.argmax(total)], pts[np.argmin(diff)]],
        dtype=np.float32,
    )


def perspective_correct(img: np.ndarray, quad: np.ndarray) -> np.ndarray:
    """按四边形做透视矫正，输出正向矩形图。尺寸过小时原样返回。"""
    tl, tr, br, bl = order_quad_points(quad)
    out_w = int(max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl)))
    out_h = int(max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr)))
    if out_w < 10 or out_h < 10:
        return img
    dst = np.array(
        [[0, 0], [out_w - 1, 0], [out_w - 1, out_h - 1], [0, out_h - 1]], dtype=np.float32
    )
    src = np.array([tl, tr, br, bl], dtype=np.float32)
    return cv2.warpPerspective(img, cv2.getPerspectiveTransform(src, dst), (out_w, out_h))


def remove_shadow(gray: np.ndarray) -> np.ndarray:
    """消除光照不均与阴影。

    大核膨胀得到「背景亮度图」，再用原图除以背景做归一化，等价于同态滤波的简化版。
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (SHADOW_KSIZE, SHADOW_KSIZE))
    background = cv2.medianBlur(cv2.dilate(gray, kernel), 21)
    return cv2.divide(gray, np.maximum(background, 1), scale=255)


def binarize(gray: np.ndarray) -> np.ndarray:
    """二值化，输出前景=255 的图（供版面分析）。

    优先 Otsu；若前景占比落在合理区间之外（曝光异常），改用自适应阈值兜底。
    """
    otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    ratio = float(np.count_nonzero(otsu)) / otsu.size
    if OTSU_MIN_RATIO <= ratio <= OTSU_MAX_RATIO:
        return otsu
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, ADAPTIVE_BLOCK, ADAPTIVE_C
    )


def resize_to_range(img: np.ndarray, min_side: int = MIN_SIDE, max_side: int = MAX_SIDE) -> np.ndarray:
    """把短边抬到 min_side、长边压进 max_side，保持宽高比。

    插值核**按方向选**：放大用 LANCZOS4，缩小用 AREA。
    这不是随手挑的 —— 同一张送货单放大 1.39 倍后送 OCR 实测：
    CUBIC（原先用的）/ LINEAR / AREA / NEAREST 四种都把表格识别成乱码，
    **只有 LANCZOS4 能完整认出「品名/数量/单价/金额」与明细行**。
    放大时普通插值核会在笔画边缘产生过冲光晕，表线附近尤其明显，OCR 就此崩掉。

    两个约束是**先后施加**而非二选一：先按短边抬升，再看长边是否因此超限需要压回。
    早先写成 `elif` 时，极端长宽比（如 500x5000）会因为「短边不足」走进放大分支，
    结果产出 10000 宽、远超 `max_side` 的图 —— `max_side` 的承诺被绕过。
    """
    h, w = img.shape[:2]
    short, long_side = min(h, w), max(h, w)
    if short == 0:
        return img
    scale = 1.0
    if short < min_side:
        scale = min_side / float(short)
    if long_side * scale > max_side:
        scale = max_side / float(long_side)
    if abs(scale - 1.0) < 1e-3:
        return img
    size = (max(1, int(w * scale)), max(1, int(h * scale)))
    interp = cv2.INTER_LANCZOS4 if scale > 1.0 else cv2.INTER_AREA
    return cv2.resize(img, size, interpolation=interp)


def preprocess(data: bytes) -> PreprocessResult:
    """完整预处理流水线：解码 → 透视矫正 → 倾斜校正 → 缩放 → 去噪去阴影 → 二值化。

    几何变换在缩放前完成，缩放之后才生成 binary 与最终 gray，
    因此 image 与 binary 尺寸一致、坐标同空间。
    """
    img = load_image(data)
    meta: dict = {"original_shape": tuple(img.shape[:2])}

    quad = find_document_quad(to_gray(img))
    meta["perspective"] = quad is not None
    if quad is not None:
        img = perspective_correct(img, quad)

    skew = estimate_skew_angle(to_gray(img))
    meta["skew_angle"] = round(float(skew), 2)
    img = rotate(img, skew)

    img = resize_to_range(img)
    meta["final_shape"] = tuple(img.shape[:2])

    gray = denoise(remove_shadow(to_gray(img)))
    return PreprocessResult(image=img, binary=binarize(gray), meta=meta)
