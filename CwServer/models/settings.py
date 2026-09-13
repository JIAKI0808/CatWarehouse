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
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
