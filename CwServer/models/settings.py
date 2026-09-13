from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.dialects.sqlite import JSON

from models import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, default=1)
    ai_config = Column(JSON, default=dict)
    plugin_config = Column(JSON, default=dict)
    # 界面语言偏好（BCP-47，如 zh-CN / en-US）。2026-09-14 新增，服务于 `api/i18n` 分区。
    # 刻意**不**加进 `schemas.settings.SettingsResponse` —— 那样会改掉 /api/settings 的响应，
    # 而本次的硬约束是「既有接口一个字不改」。读取走 `GET /api/i18n/preference`。
    locale = Column(String, server_default="zh-CN", default="zh-CN")
    # 计价货币代码（ISO 4217，如 CNY / USD）。2026-09-14 新增，服务于「通用化」环。
    # 默认 `CNY` ⇒ 符号 `¥` ⇒ **界面逐字不变**（与 locale 默认 zh-CN 同一个把风险压到零的手法）。
    # 同样**不**加进 `SettingsResponse`，读取走 `GET /api/currencies/preference`。
    currency = Column(String, server_default="CNY", default="CNY")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


async def get_or_create(db, settings_id: int = 1) -> "Settings":
    """取（或建）Settings 单行。

    原本 `api/system/settings_router.py` 与 `api/i18n/i18n_router.py` **各有一份私有副本**
    （i18n 那份当时是为了遵守「分区之间不互相 import」而刻意重复的）。
    到了货币分区会变成**第三份** —— 三份 8 行就是该抽的时候了（本环正是「通用化」）。

    放在 `models/` 而不是某个分区里：它是**数据访问**而不是任何一个分区的职责，
    这样三个分区都不必 import 另一个分区。
    """
    from sqlalchemy import select  # 局部导入：本模块其余部分不需要它

    result = await db.execute(select(Settings).where(Settings.id == settings_id))
    row = result.scalar_one_or_none()
    if row is None:
        row = Settings(id=settings_id, ai_config={}, plugin_config={})
        db.add(row)
        await db.commit()
        await db.refresh(row)
    return row
