"""
勤務パターンスキーマ
APIリクエスト/レスポンス用のPydanticモデル
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class BreakTimeSchema(BaseModel):
    """
    休憩時間スキーマ
    """
    start_time: str = Field(..., description="休憩開始時刻 (HH:MM形式)")
    end_time: str = Field(..., description="休憩終了時刻 (HH:MM形式)")

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """時刻形式のバリデーション"""
        if not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("時刻はHH:MM形式で入力してください")
        return v


class WorkPatternCreate(BaseModel):
    """
    勤務パターン作成リクエストスキーマ
    """
    pattern_number: int = Field(..., ge=1, le=3, description="パターン番号（1-3）")
    start_time: str = Field(..., description="始業時刻 (HH:MM形式)")
    end_time: str = Field(..., description="終業時刻 (HH:MM形式)")
    break_times: list[BreakTimeSchema] = Field(
        default_factory=list,
        max_length=3,
        description="休憩時間リスト（最大3つ）"
    )
    year_month: str = Field(..., description="年月 (YYYY-MM形式)")

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """時刻形式のバリデーション"""
        if not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("時刻はHH:MM形式で入力してください")
        return v

    @field_validator("year_month")
    @classmethod
    def validate_year_month_format(cls, v: str) -> str:
        """年月形式のバリデーション"""
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
            raise ValueError("年月はYYYY-MM形式で入力してください")
        return v


class WorkPatternUpdate(BaseModel):
    """
    勤務パターン更新リクエストスキーマ
    """
    start_time: Optional[str] = Field(None, description="始業時刻 (HH:MM形式)")
    end_time: Optional[str] = Field(None, description="終業時刻 (HH:MM形式)")
    break_times: Optional[list[BreakTimeSchema]] = Field(
        None,
        max_length=3,
        description="休憩時間リスト（最大3つ）"
    )

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """時刻形式のバリデーション"""
        if v is not None and not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("時刻はHH:MM形式で入力してください")
        return v


class WorkPatternResponse(BaseModel):
    """
    勤務パターンレスポンススキーマ
    """
    pattern_id: str = Field(..., description="パターンID")
    user_id: str = Field(..., description="ユーザーID")
    pattern_number: int = Field(..., description="パターン番号")
    start_time: str = Field(..., description="始業時刻")
    end_time: str = Field(..., description="終業時刻")
    break_times: list[BreakTimeSchema] = Field(..., description="休憩時間リスト")
    year_month: str = Field(..., description="年月")
    scheduled_work_minutes: int = Field(..., description="所定労働時間（分）")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = {"from_attributes": True}
