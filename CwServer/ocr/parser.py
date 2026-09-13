from __future__ import annotations

import re

from ocr.layout import group_lines_into_rows, split_regions
from ocr.types import Receipt, ReceiptItem, TextLine

# ---------- 调参常量 ----------
NAME_MIN_LEN = 2       # 品名最少字符数，低于此视为非明细行
HEAD_ROWS = 3          # 取不到抬头区域时的兜底行数

# 全角 → 半角（数字、标点、货币符号），并把全角空格 U+3000 归一成普通空格：
# 中文 OCR 常把「花椒　2　12.50」的空档输出成全角空格，归成普通空格后才能按空白切格。
_FULLWIDTH = str.maketrans(
    "０１２３４５６７８９．，：（）％－＃＄　", "0123456789.,:()%-#$ "
)
_UNIT_PAT = r"(?:元|个|件|箱|包|瓶|袋|斤|克|千克|公斤|kg|KG|g|L|ml)?"
_NUM_RE = re.compile(r"-?\d{1,3}(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?")
_AMOUNT_RE = re.compile(r"[0-9][0-9,]*(?:\.[0-9]{1,2})?")
_PURE_NUM_RE = re.compile(rf"^[¥￥$]?\s*-?[0-9][0-9,]*(?:\.[0-9]{{1,2}})?\s*{_UNIT_PAT}$")
_DATE_RE = re.compile(r"(20\d{2})[-/年.](\d{1,2})[-/月.](\d{1,2})")
_ORDER_RE = re.compile(
    r"(?:单据号|订单号|单号|票号|编号|No|NO|#)[:.]?([A-Za-z0-9][A-Za-z0-9\-_/]{3,31})",
    re.IGNORECASE,
)
_TRAILING_NUM_RE = re.compile(r"^(?P<name>.*?[a-zA-Z一-鿿])\s*(?P<num>[0-9][0-9,]*(?:\.[0-9]{1,2})?)$")
# 只去掉「中文字之间的」空白，保留拉丁词之间的空格（免得把英文商号粘成一块）
_CJK_GAP_RE = re.compile(r"(?<=[一-鿿])\s+(?=[一-鿿])")

_TOTAL_KEYS = ("总计", "价税合计", "总金额", "总额", "合计", "应收", "实收", "应付")
_TOTAL_ROW_KEYS = ("合计", "总计", "总额", "小计", "大写", "小写", "税额", "实收", "收款", "找零")
_META_ROW_KEYS = ("单号", "单据号", "订单号", "票号", "日期", "时间", "电话", "地址", "客户",
                  "收货", "供方", "联系人", "开票", "税号", "账号", "开户", "备注")
_HEADER_CELL_KEYS = ("品名", "名称", "商品", "货品", "数量", "单价", "金额", "单位", "规格", "序号")
_COLUMN_KEYS = (
    ("name", ("品名", "名称", "商品", "货品", "项目", "摘要")),
    ("quantity", ("数量", "数目")),
    ("unit_price", ("单价", "价格")),
    ("amount", ("金额", "小计", "总价")),
)
_DOC_TYPE_KEYS = (
    ("delivery", ("送货单", "送货", "配送单", "出库单")),
    ("invoice", ("发票", "增值税", "税号", "价税合计", "税率")),
    ("receipt", ("收据", "小票", "购物", "收银", "消费")),
)
_MERCHANT_KEYS = ("公司", "商行", "商店", "超市", "市场", "批发", "中心", "工厂", "厂", "店")
_MERCHANT_SKIP = ("电话", "地址", "日期", "单号", "编号", "收据", "发票", "送货单", "小票")


def _norm(text: str) -> str:
    """全角转半角，并把连续空格压成一个。用于按空白切分单元格与展示。"""
    return re.sub(r"[ \t]+", " ", str(text).translate(_FULLWIDTH)).strip()


def _squeeze(text: str) -> str:
    """在 `_norm` 基础上再去掉所有空白。

    关键词与正则匹配统一走这里，才能容忍「合　计」「品 名」这类被空格切开的写法，
    否则会被切成两个单字格而匹配不到。
    """
    return re.sub(r"\s+", "", _norm(text))


def _to_float(text: str) -> float | None:
    """取文本中第一个数字（容忍千分位逗号）；取不到返回 None。"""
    match = _NUM_RE.search(_norm(text))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None


def _is_pure_number(text: str) -> bool:
    """整格是否只是一个数字（含「25.00 元」「2件」这种带单位的写法）。"""
    return bool(_PURE_NUM_RE.match(_norm(text)))


def _last_amount(packed: str) -> float | None:
    """取一行中最后一个数字作为金额，如「合计25.00元」→ 25.00。"""
    amounts = _AMOUNT_RE.findall(packed)
    return _to_float(amounts[-1]) if amounts else None


def extract_date(text: str) -> str | None:
    """抽取日期并统一成 YYYY-MM-DD。"""
    match = _DATE_RE.search(_squeeze(text))
    if not match:
        return None
    year, month, day = (int(g) for g in match.groups())
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    return f"{year:04d}-{month:02d}-{day:02d}"


def extract_order_no(text: str) -> str | None:
    """抽取单据编号。"""
    match = _ORDER_RE.search(_squeeze(text))
    return match.group(1) if match else None


def extract_total(text: str) -> float | None:
    """抽取票据总额。

    先按关键词定优先级（总计 > 价税合计 > 总金额 > 合计 > 应收/实收…），
    同一优先级取最后一次出现（票据的最终合计通常在底部）。
    """
    best: tuple[int, float] | None = None
    for line in _norm(text).splitlines():
        packed = _squeeze(line)
        for key in _TOTAL_KEYS:
            if key not in packed:
                continue
            value = _last_amount(packed)
            if value is not None:
                rank = _TOTAL_KEYS.index(key)
                if best is None or rank <= best[0]:
                    best = (rank, value)
            break
    return best[1] if best else None


def detect_doc_type(text: str) -> str:
    """按标题/关键词判断票据类型，识别不出返回 unknown。"""
    packed = _squeeze(text)
    for kind, keys in _DOC_TYPE_KEYS:
        if any(key in packed for key in keys):
            return kind
    return "unknown"


def _merchant_candidates(lines: list[TextLine]) -> list[tuple[str, str]]:
    """把抬头文本行**按行聚类后拼接**成候选商户名，返回 (原文, 去空白版)。

    必须按行拼接而非逐条判断：引擎可能把「星辰调料批发部」拆成多条
    （逐词返回时是「星辰」「调料」「批发」「部」）。逐条看的话，
    「批发」本身就在 `_MERCHANT_KEYS` 里，于是商户名被猜成「批发」——
    这是实测踩到的。

    拼接时去掉**中文字之间的**空白：既兼容逐词返回，也顺手修掉
    「星辰 调料 批发 部」这种词间带空格的形态（同一个引擎按整行返回时的样子）。
    """
    candidates = []
    for row in group_lines_into_rows(lines):
        joined = _CJK_GAP_RE.sub("", "".join(_norm(line.text) for line in row))
        if joined:
            candidates.append((joined, _squeeze(joined)))
    return candidates


def extract_merchant(lines: list[TextLine]) -> str | None:
    """从抬头文本行中猜商户名。

    优先取含「公司/商行/超市/店…」等商户特征且不含单据类关键词的行；
    否则退化为第一条足够长的非关键词行。
    """
    candidates = _merchant_candidates(lines)
    for text, packed in candidates:
        if any(k in packed for k in _MERCHANT_KEYS) and not any(s in packed for s in _MERCHANT_SKIP):
            return text
    for text, packed in candidates:
        if len(text) >= NAME_MIN_LEN and not any(s in packed for s in _MERCHANT_SKIP):
            return text
    return None


def _row_cells(row: list[TextLine]) -> list[str]:
    """把一行 OCR 结果归一成格子文本。

    单条文本按空白切分（PaddleOCR 常把整行识别成一条），
    多条文本则直接按 x 序取用（按列切分的返回形态）。
    """
    if len(row) == 1:
        return [c for c in _norm(row[0].text).split(" ") if c]
    return [_norm(line.text) for line in row if _norm(line.text)]


def _is_header_row(packed: str) -> bool:
    """是否为表头行：整行含 2 个以上列名关键词。"""
    return sum(1 for key in _HEADER_CELL_KEYS if key in packed) >= 2


def _header_columns(cells: list[str]) -> dict[str, int] | None:
    """从表头行解析 字段 -> 列序号 映射；不是表头行则返回 None。"""
    mapping: dict[str, int] = {}
    for index, cell in enumerate(cells):
        packed = _squeeze(cell)
        for field, keys in _COLUMN_KEYS:
            if field not in mapping and any(key in packed for key in keys):
                mapping[field] = index
    return mapping if len(mapping) >= 2 else None


def _is_total_row(packed: str) -> bool:
    """是否为合计/税额/大小写等汇总行（传入已 squeeze 的整行文本）。"""
    return any(key in packed for key in _TOTAL_ROW_KEYS)


def _is_meta_row(packed: str) -> bool:
    """是否为单号/日期/地址等抬头元信息行（传入已 squeeze 的整行文本）。

    否则「单号: SH20260913001」会被当成一条品名为「单号:」的明细。
    """
    return any(key in packed for key in _META_ROW_KEYS)


def _name_of(cells: list[str], columns: dict[str, int]) -> str | None:
    """取品名格文本；越界、过短或纯数字则返回 None（视为非明细行）。"""
    index = columns.get("name", 0)
    if not 0 <= index < len(cells):
        return None
    name = cells[index]
    return None if len(name) < NAME_MIN_LEN or _is_pure_number(name) else name


def _number_at(cells: list[str], columns: dict[str, int], field: str) -> float | None:
    """按列映射取数字；无映射或越界返回 None。"""
    index = columns.get(field)
    if index is None or not 0 <= index < len(cells):
        return None
    return _to_float(cells[index])


def _positional_numbers(values: list[float]) -> tuple[float | None, float | None, float | None]:
    """无表头时按数字个数推断 (数量, 单价, 金额)。

    3 个数字按票据最常见位序「数量/单价/金额」；2 个数字按「数量/金额」
    （本应用库存要数量、账本要金额）；1 个数字视为金额。
    """
    if len(values) >= 3:
        return values[0], values[1], values[2]
    if len(values) == 2:
        return values[0], None, values[1]
    if len(values) == 1:
        return None, None, values[0]
    return None, None, None


def _split_name_quantity(name: str) -> tuple[str, float | None]:
    """拆分「花椒2」这类粘连的「品名+数量」。"""
    match = _TRAILING_NUM_RE.match(name)
    if not match:
        return name, None
    return match.group("name"), _to_float(match.group("num"))


def _cells_to_item(cells: list[str], columns: dict[str, int]) -> ReceiptItem | None:
    """把一行格子文本转成 ReceiptItem；信息不足返回 None。

    有表头映射时严格按列取值；否则按位序推断，并尝试从粘连的品名里拆出数量。
    一个数字都没有的行对库存/账本无意义，多半是标题或残留，直接丢弃。
    """
    name = _name_of(cells, columns)
    if name is None:
        return None
    if columns:
        item = ReceiptItem(
            name,
            _number_at(cells, columns, "quantity"),
            _number_at(cells, columns, "unit_price"),
            _number_at(cells, columns, "amount"),
        )
    else:
        split_name, sticky = _split_name_quantity(name)
        values = [sticky] if sticky is not None else []
        values += [v for v in (_to_float(cell) for cell in cells[1:]) if v is not None]
        quantity, unit_price, amount = _positional_numbers(values)
        item = ReceiptItem(split_name, quantity, unit_price, amount)
    if item.quantity is None and item.unit_price is None and item.amount is None:
        return None
    return item


def parse_items(rows: list[list[TextLine]]) -> list[ReceiptItem]:
    """从版面行抽取明细行。

    先找表头行（品名/数量/单价/金额）建立列映射，后续行按该映射取值；
    没有表头时退化为「首格为品名、其余数字按位序解释」。
    汇总行与单号/日期等元信息行会被跳过。
    """
    items: list[ReceiptItem] = []
    columns: dict[str, int] = {}
    for row in rows:
        cells = _row_cells(row)
        if not cells:
            continue
        packed = _squeeze("".join(line.text for line in row))
        header = _header_columns(cells)
        if header is not None or _is_header_row(packed):
            columns = header or columns
            continue
        if _is_total_row(packed) or _is_meta_row(packed):
            continue
        item = _cells_to_item(cells, columns)
        if item is not None:
            items.append(item)
    return items


def _header_lines(lines: list[TextLine]) -> list[TextLine]:
    """取抬头（表体之前）的文本行，用于猜商户名。"""
    regions = split_regions([line.bbox for line in lines])
    for region in regions:
        if region.kind == "header":
            return [lines[i] for i in region.line_indices]
    return lines[:HEAD_ROWS]


def _sum_amounts(items: list[ReceiptItem]) -> float | None:
    """找不到合计关键词时的兜底：把明细金额加总（需至少一条有金额）。"""
    amounts = [item.amount for item in items if item.amount is not None]
    return round(sum(amounts), 2) if amounts else None


def parse_receipt(lines: list[TextLine], raw_text: str = "") -> Receipt:
    """把版面文本行解析为通用票据结构。

    日期/单号/总额走全文正则（不依赖区域切分）；明细走行聚类 + 列映射；
    商户名走抬头区域；总额缺失时用明细金额加总兜底。
    """
    text = raw_text or "\n".join(line.text for line in lines)
    rows = group_lines_into_rows(lines)
    items = parse_items(rows)
    total = extract_total(text)
    if total is None:
        total = _sum_amounts(items)
    return Receipt(
        doc_type=detect_doc_type(text),
        merchant=extract_merchant(_header_lines(lines)),
        date=extract_date(text),
        order_no=extract_order_no(text),
        items=items,
        total=total,
        raw_text=text,
        extra={"line_count": len(lines), "row_count": len(rows)},
    )
