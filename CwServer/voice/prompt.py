from __future__ import annotations

import json
import re
from datetime import date, datetime

from voice.types import DIRECTION_IN, DIRECTION_OUT, VoiceCommand, VoiceItem

RAW_LIMIT = 200
TODAY_TOKEN = "<TODAY>"

# 模型被要求只输出 in/out；这里仍留同义词兜底（改错供应商或换模型时不必跟着改代码）
_OUT_WORDS = {"out", "outbound", "outcome", "出", "出库", "卖出", "出售", "销售", "sale", "sell"}
_FENCE_RE = re.compile(r"```(?:json|JSON)?\s*(.*?)```", re.S)
_DATE_RE = re.compile(r"(\d{4})\D{0,3}(\d{1,2})\D{0,3}(\d{1,2})")

SYSTEM_PROMPT = """你是仓库管理系统的语音录入助手。用户会用口语说一句进货或出货的话，
你要把它整理成**严格 JSON**，只输出 JSON 本身，不要解释、不要前后缀、不要 markdown 代码块。

输出结构：
{
  "direction": "in" 或 "out",
  "merchant": 字符串或 null,
  "date": "YYYY-MM-DD" 或 null,
  "total": 数字或 null,
  "note": 字符串或 null,
  "items": [
    {"name": 字符串, "quantity": 数字或 null, "unit": 字符串或 null,
     "unit_price": 数字或 null, "amount": 数字或 null, "category_hint": 字符串或 null}
  ]
}

判定规则：
1. direction：进货 / 入库 / 买入 / 买了 / 采购 / 收到 / 到货 → "in"；
   卖出 / 出货 / 卖掉 / 出库 / 卖给 / 销售 / 发货 → "out"。判断不出用 "in"。
2. items：name 必填，是物品名。「两斤花椒」要拆成 name=花椒、quantity=2、unit=斤，
   不要把数量单位混进 name；一句话里多个物品就拆成多条。
3. quantity / unit_price / amount 是纯数字，口语没说的填 null。
   金额与单价是两种东西：只说了「一共五十」就填 total=50，不要硬算 unit_price。
4. category_hint 只能填用户**说出来的**分类词（如「调料」「蔬菜」），
   不要把物品名当分类；用户没说就填 null。
5. date：今天 = <TODAY>。说「昨天」「前天」就换算成具体日期；只说「上周」这类模糊说法填 null。
6. merchant 是供应商 / 客户 / 店铺名，用户没提就填 null。
7. note 放其它值得记录但结构里没地方放的信息；没有就填 null。

只输出 JSON。"""


def build_system_prompt(today: str | None = None) -> str:
    """构造 system 提示词；注入当天日期，供模型换算「今天 / 昨天」。"""
    return SYSTEM_PROMPT.replace(TODAY_TOKEN, today or date.today().isoformat())


def build_user_prompt(transcript: str) -> str:
    """构造 user 提示词。

    用分隔串把口述内容包起来：口述是**外部输入**，万一里面夹着「忽略上面的要求」这类
    句子，分隔串能让模型更容易把它当作待整理的素材而不是新指令。
    """
    return f"把下面这段口述整理成 JSON：\n<口述>\n{transcript}\n</口述>"


def _snippet(text: str) -> str:
    """把模型原始返回压成一行并截断，用于错误信息里回显。"""
    return " ".join(str(text).split())[:RAW_LIMIT]


def _strip_fence(text: str) -> str:
    """剥掉 markdown 代码块围栏，取第一个围栏里的内容。"""
    match = _FENCE_RE.search(text)
    return match.group(1).strip() if match else ""


def _first_object(text: str) -> dict | None:
    """从首个 `{` 起解出一个完整对象，后面的内容一概忽略。

    模型在 JSON 后面又补了一段话（甚至再加一个对象）时用这条路径，
    规则是**取第一个完整的 JSON 对象**。
    """
    start = text.find("{")
    if start < 0:
        return None
    try:
        payload, _ = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def extract_json(text: str) -> dict:
    """从大模型返回文本里取出 JSON 对象。

    容错三层：直接解析 → 剥掉 ``` 围栏 → 取首个完整对象。
    全部失败时抛 `ValueError`，**不返回空壳** —— 猜出来的数据会静默污染库存，
    宁可让调用方看到明确失败（见 plan.md §15.3）。
    """
    stripped = text.strip()
    for candidate in (stripped, _strip_fence(stripped)):
        if not candidate:
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    found = _first_object(stripped)
    if found is not None:
        return found
    raise ValueError(f"大模型返回里没有可解析的 JSON 对象: {_snippet(text)}")


def _to_str(value: object) -> str | None:
    """非空字符串才返回，其余返回 None。"""
    return value.strip() if isinstance(value, str) and value.strip() else None


def _to_float(value: object) -> float | None:
    """转成正浮点数；`true/false`、空串、非数字串都返回 None。"""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().replace(",", ""))
        except ValueError:
            return None
    return None


def direction_of(value: object) -> str:
    """把模型给的 direction 归一到 `in` / `out`；认不出时按入库处理。"""
    return DIRECTION_OUT if (_to_str(value) or "").lower() in _OUT_WORDS else DIRECTION_IN


def normalize_date(value: object) -> str | None:
    """把模型给的日期归一到 `YYYY-MM-DD`；认不出或是非法日期返回 None。"""
    text = _to_str(value)
    if not text:
        return None
    match = _DATE_RE.search(text)
    if not match:
        return None
    year, month, day = (int(part) for part in match.groups())
    try:
        return datetime(year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return None


def _item_of(raw: object) -> VoiceItem | None:
    """把一条明细的原始 dict 转成 VoiceItem；没有名字的整条丢弃。"""
    if not isinstance(raw, dict):
        return None
    name = _to_str(raw.get("name"))
    if not name:
        return None
    return VoiceItem(
        name=name,
        quantity=_to_float(raw.get("quantity")),
        unit=_to_str(raw.get("unit")),
        unit_price=_to_float(raw.get("unit_price")),
        amount=_to_float(raw.get("amount")),
        category_hint=_to_str(raw.get("category_hint")),
    )


def _items_of(value: object) -> list[VoiceItem]:
    """把 items 转成 VoiceItem 列表；非数组返回空，脏元素逐条丢弃。"""
    if not isinstance(value, list):
        return []
    return [item for item in (_item_of(raw) for raw in value) if item is not None]


def parse_command(payload: dict, raw_text: str = "") -> VoiceCommand:
    """把大模型返回的 JSON 对象转成 `VoiceCommand`。

    字段缺失、类型不对、多出未见过的键，一律不报错：能取到的取，取不到的留空 / null。
    这层只在**结构**上兜错，不做业务猜测。
    """
    return VoiceCommand(
        direction=direction_of(payload.get("direction")),
        items=_items_of(payload.get("items")),
        merchant=_to_str(payload.get("merchant")),
        date=normalize_date(payload.get("date")),
        total=_to_float(payload.get("total")),
        note=_to_str(payload.get("note")),
        raw_text=raw_text,
    )


def command_from_text(text: str, raw_text: str = "") -> VoiceCommand:
    """从大模型返回的原始文本一路解析到 `VoiceCommand`。

    Raises:
        ValueError: 文本里没有可解析的 JSON 对象。
    """
    payload = extract_json(text)
    return parse_command(payload, raw_text or text)
