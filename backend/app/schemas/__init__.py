"""
スキーマパッケージ
Pydanticスキーマ定義（APIリクエスト/レスポンス用）
"""
from .user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenData,
)
from .work_pattern import (
    BreakTimeSchema,
    WorkPatternCreate,
    WorkPatternUpdate,
    WorkPatternResponse,
)
from .monthly_record import (
    MonthlyRecordCreate,
    MonthlyRecordUpdate,
    MonthlyRecordResponse,
    ApprovalRequest,
)
from .daily_record import (
    DailyRecordCreate,
    DailyRecordUpdate,
    DailyRecordResponse,
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenData",
    # WorkPattern
    "BreakTimeSchema",
    "WorkPatternCreate",
    "WorkPatternUpdate",
    "WorkPatternResponse",
    # MonthlyRecord
    "MonthlyRecordCreate",
    "MonthlyRecordUpdate",
    "MonthlyRecordResponse",
    "ApprovalRequest",
    # DailyRecord
    "DailyRecordCreate",
    "DailyRecordUpdate",
    "DailyRecordResponse",
]
