import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()

CURRENCIES = [
    {"code": "CNY", "name": "人民币", "symbol": "¥"},
    {"code": "USD", "name": "美元", "symbol": "$"},
    {"code": "EUR", "name": "欧元", "symbol": "€"},
    {"code": "GBP", "name": "英镑", "symbol": "£"},
    {"code": "JPY", "name": "日元", "symbol": "¥"},
    {"code": "KRW", "name": "韩元", "symbol": "₩"},
    {"code": "HKD", "name": "港币", "symbol": "HK$"},
    {"code": "TWD", "name": "新台币", "symbol": "NT$"},
]


@router.get("/currencies")
async def list_currencies():
    return CURRENCIES
