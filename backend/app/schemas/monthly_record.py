"""
月次記録スキーマ
APIリクエスト/レスポンス用のPydanticモデル
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class MonthlyRecordCreate(BaseModel):
    """
    月次記録作成リクエストスキーマ
    """
    year_month: str = Field(..., description="年月 (YYYY-MM形式)")
    name: str = Field(..., min_length=1, description="氏名")
    department: str = Field(..., min_length=1, description="所属")
    standard_work_hours: float = Field(default=8.0, ge=0, le=24, description="1日標準就労時間")

    @field_validator("year_month")
    @classmethod
    def validate_year_month_format(cls, v: str) -> str:
        """年月形式のバリデーション"""
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
            raise ValueError("年月はYYYY-MM形式で入力してください")
        return v


class MonthlyRecordUpdate(BaseModel):
    """
    月次記録更新リクエストスキーマ
    """
    name: Optional[str] = Field(None, min_length=1, description="氏名")
    department: Optional[str] = Field(None, min_length=1, description="所属")
    standard_work_hours: Optional[float] = Field(None, ge=0, le=24, description="1日標準就労時間")


class ApprovalRequest(BaseModel):
    """
    承認リクエストスキーマ
    """
    action: str = Field(..., description="アクション（submit/approve/reject/revoke）")
    comment: Optional[str] = Field(None, description="コメント")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        """アクションのバリデーション"""
        valid_actions = ["submit", "approve", "reject", "revoke"]
        if v not in valid_actions:
            raise ValueError(f"アクションは{valid_actions}のいずれかを指定してください")
        return v


class MonthlyRecordResponse(BaseModel):
    """
    月次記録レスポンススキーマ
    """
    record_id: str = Field(..., description="レコードID")
    user_id: str = Field(..., description="ユーザーID")
    year_month: str = Field(..., description="年月")
    name: str = Field(..., description="氏名")
    department: str = Field(..., description="所属")
    standard_work_hours: float = Field(..., description="1日標準就労時間")
    status: str = Field(..., description="承認ステータス")
    approver_id: Optional[str] = Field(None, description="承認者ID")
    approved_at: Optional[datetime] = Field(None, description="承認日時")
    approval_comment: Optional[str] = Field(None, description="承認コメント")
    total_work_days: int = Field(..., description="総出勤日数")
    total_work_minutes: int = Field(..., description="総労働時間（分）")
    total_overtime_minutes: int = Field(..., description="総残業時間（分）")
    total_night_overtime_minutes: int = Field(..., description="深夜早朝残業時間（分）")
    total_holiday_work_minutes: int = Field(..., description="法定休日残業時間（分）")
    total_extra_holiday_work_minutes: int = Field(..., description="法定外休日残業時間（分）")
    total_late_minutes: int = Field(..., description="総遅刻時間（分）")
    total_early_leave_minutes: int = Field(..., description="総早退時間（分）")
    total_paid_leave_days: float = Field(..., description="有休日数")
    total_absence_days: float = Field(..., description="欠勤日数")
    total_special_leave_days: float = Field(..., description="特休日数")
    total_condolence_leave_days: float = Field(..., description="慶弔日数")
    is_locked: bool = Field(..., description="ロック状態")
    can_edit: bool = Field(..., description="編集可能フラグ")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = {"from_attributes": True}
