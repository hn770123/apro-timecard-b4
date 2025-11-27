"""
APIパッケージ
FastAPIルーター定義
"""
from .auth import router as auth_router
from .users import router as users_router
from .work_patterns import router as work_patterns_router
from .monthly_records import router as monthly_records_router
from .daily_records import router as daily_records_router

__all__ = [
    "auth_router",
    "users_router",
    "work_patterns_router",
    "monthly_records_router",
    "daily_records_router",
]
