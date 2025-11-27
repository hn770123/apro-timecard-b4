"""
日次記録スキーマ
APIリクエスト/レスポンス用のPydanticモデル
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class DailyRecordCreate(BaseModel):
    """
    日次記録作成リクエストスキーマ
    """
    record_date: str = Field(..., description="日付 (YYYY-MM-DD形式)")
    work_type: str = Field(default="work", description="勤務の種類")
    leave_type: str = Field(default="none", description="休暇種類")
    pattern_number: int = Field(default=1, ge=1, le=3, description="勤務パターン番号")
    start_time: Optional[str] = Field(None, description="出勤時刻 (HH:MM形式)")
    end_time: Optional[str] = Field(None, description="退勤時刻 (HH:MM形式)")
    note: Optional[str] = Field(None, description="補足欄")

    @field_validator("record_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """日付形式のバリデーション"""
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$", v):
            raise ValueError("日付はYYYY-MM-DD形式で入力してください")
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """時刻形式のバリデーション"""
        if v is not None and not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("時刻はHH:MM形式で入力してください")
        return v

    @field_validator("work_type")
    @classmethod
    def validate_work_type(cls, v: str) -> str:
        """勤務種類のバリデーション"""
        valid_types = ["work", "remote", "late", "early_leave", "late_and_early", "holiday_legal", "holiday_extra"]
        if v not in valid_types:
            raise ValueError(f"勤務種類は{valid_types}のいずれかを指定してください")
        return v

    @field_validator("leave_type")
    @classmethod
    def validate_leave_type(cls, v: str) -> str:
        """休暇種類のバリデーション"""
        valid_types = ["none", "paid", "absence", "special", "condolence"]
        if v not in valid_types:
            raise ValueError(f"休暇種類は{valid_types}のいずれかを指定してください")
        return v


class DailyRecordUpdate(BaseModel):
    """
    日次記録更新リクエストスキーマ
    """
    work_type: Optional[str] = Field(None, description="勤務の種類")
    leave_type: Optional[str] = Field(None, description="休暇種類")
    pattern_number: Optional[int] = Field(None, ge=1, le=3, description="勤務パターン番号")
    start_time: Optional[str] = Field(None, description="出勤時刻 (HH:MM形式)")
    end_time: Optional[str] = Field(None, description="退勤時刻 (HH:MM形式)")
    late_minutes: Optional[int] = Field(None, ge=0, description="遅刻時間（分）")
    early_leave_minutes: Optional[int] = Field(None, ge=0, description="早退時間（分）")
    overtime_minutes: Optional[int] = Field(None, ge=0, description="残業時間（分）")
    note: Optional[str] = Field(None, description="補足欄")

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """時刻形式のバリデーション"""
        if v is not None and not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("時刻はHH:MM形式で入力してください")
        return v

    @field_validator("work_type")
    @classmethod
    def validate_work_type(cls, v: Optional[str]) -> Optional[str]:
        """勤務種類のバリデーション"""
        valid_types = ["work", "remote", "late", "early_leave", "late_and_early", "holiday_legal", "holiday_extra"]
        if v is not None and v not in valid_types:
            raise ValueError(f"勤務種類は{valid_types}のいずれかを指定してください")
        return v

    @field_validator("leave_type")
    @classmethod
    def validate_leave_type(cls, v: Optional[str]) -> Optional[str]:
        """休暇種類のバリデーション"""
        valid_types = ["none", "paid", "absence", "special", "condolence"]
        if v is not None and v not in valid_types:
            raise ValueError(f"休暇種類は{valid_types}のいずれかを指定してください")
        return v


class DailyRecordResponse(BaseModel):
    """
    日次記録レスポンススキーマ
    """
    record_id: str = Field(..., description="レコードID")
    user_id: str = Field(..., description="ユーザーID")
    monthly_record_id: str = Field(..., description="月次記録ID")
    record_date: str = Field(..., description="日付")
    work_type: str = Field(..., description="勤務の種類")
    leave_type: str = Field(..., description="休暇種類")
    pattern_number: int = Field(..., description="勤務パターン番号")
    start_time: Optional[str] = Field(None, description="出勤時刻")
    end_time: Optional[str] = Field(None, description="退勤時刻")
    late_minutes: int = Field(..., description="遅刻時間（分）")
    early_leave_minutes: int = Field(..., description="早退時間（分）")
    work_minutes: int = Field(..., description="実労働時間（分）")
    overtime_minutes: int = Field(..., description="残業時間（分）")
    night_overtime_minutes: int = Field(..., description="深夜早朝残業時間（分）")
    holiday_work_minutes: int = Field(..., description="法定休日残業時間（分）")
    extra_holiday_work_minutes: int = Field(..., description="法定外休日残業時間（分）")
    note: Optional[str] = Field(None, description="補足欄")
    is_note_required: bool = Field(..., description="補足入力必須フラグ")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = {"from_attributes": True}
