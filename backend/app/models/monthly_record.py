"""
月次記録モデル
月単位の勤務記録と承認状態を管理
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ApprovalStatus(str, Enum):
    """
    承認ステータスの列挙型
    """
    DRAFT = "draft"  # 下書き（編集可能）
    SUBMITTED = "submitted"  # 提出済み（承認待ち）
    APPROVED = "approved"  # 承認済み（ロック状態）
    REJECTED = "rejected"  # 差し戻し（再編集可能）


@dataclass
class MonthlyRecord:
    """
    月次記録モデル
    月ごとの勤務情報と承認状態を管理
    
    承認を受けた月のデータはロックされ閲覧のみ可能
    前月の内容（氏名、所属、勤務パターン等）を引き継ぐが変更可能
    """
    record_id: str  # レコードID（主キー）
    user_id: str  # ユーザーID
    year_month: str  # 年月 (YYYY-MM形式)
    name: str  # 氏名（月ごとに保存）
    department: str  # 所属（月ごとに保存）
    standard_work_hours: float = 8.0  # 1日標準就労時間（初期値8時間）
    status: ApprovalStatus = ApprovalStatus.DRAFT  # 承認ステータス
    approver_id: Optional[str] = None  # 承認者ID
    approved_at: Optional[datetime] = None  # 承認日時
    approval_comment: Optional[str] = None  # 承認コメント
    total_work_days: int = 0  # 総出勤日数
    total_work_minutes: int = 0  # 総労働時間（分）
    total_overtime_minutes: int = 0  # 総残業時間（分）
    total_night_overtime_minutes: int = 0  # 深夜早朝残業時間（分）
    total_holiday_work_minutes: int = 0  # 法定休日残業時間（分）
    total_extra_holiday_work_minutes: int = 0  # 法定外休日残業時間（分）
    total_late_minutes: int = 0  # 総遅刻時間（分）
    total_early_leave_minutes: int = 0  # 総早退時間（分）
    total_paid_leave_days: float = 0.0  # 有休日数
    total_absence_days: float = 0.0  # 欠勤日数
    total_special_leave_days: float = 0.0  # 特休日数
    total_condolence_leave_days: float = 0.0  # 慶弔日数
    created_at: datetime = field(default_factory=datetime.now)  # 作成日時
    updated_at: datetime = field(default_factory=datetime.now)  # 更新日時

    def is_locked(self) -> bool:
        """
        データがロック状態かどうかを判定
        承認済みの場合は変更不可
        """
        return self.status == ApprovalStatus.APPROVED

    def can_edit(self) -> bool:
        """
        編集可能かどうかを判定
        """
        return self.status in [ApprovalStatus.DRAFT, ApprovalStatus.REJECTED]

    def to_dict(self) -> dict:
        """辞書形式に変換（DynamoDB保存用）"""
        return {
            "record_id": self.record_id,
            "user_id": self.user_id,
            "year_month": self.year_month,
            "name": self.name,
            "department": self.department,
            "standard_work_hours": str(self.standard_work_hours),
            "status": self.status.value,
            "approver_id": self.approver_id,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approval_comment": self.approval_comment,
            "total_work_days": self.total_work_days,
            "total_work_minutes": self.total_work_minutes,
            "total_overtime_minutes": self.total_overtime_minutes,
            "total_night_overtime_minutes": self.total_night_overtime_minutes,
            "total_holiday_work_minutes": self.total_holiday_work_minutes,
            "total_extra_holiday_work_minutes": self.total_extra_holiday_work_minutes,
            "total_late_minutes": self.total_late_minutes,
            "total_early_leave_minutes": self.total_early_leave_minutes,
            "total_paid_leave_days": str(self.total_paid_leave_days),
            "total_absence_days": str(self.total_absence_days),
            "total_special_leave_days": str(self.total_special_leave_days),
            "total_condolence_leave_days": str(self.total_condolence_leave_days),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MonthlyRecord":
        """辞書からインスタンスを生成"""
        return cls(
            record_id=data["record_id"],
            user_id=data["user_id"],
            year_month=data["year_month"],
            name=data["name"],
            department=data["department"],
            standard_work_hours=float(data.get("standard_work_hours", 8.0)),
            status=ApprovalStatus(data.get("status", "draft")),
            approver_id=data.get("approver_id"),
            approved_at=datetime.fromisoformat(data["approved_at"]) if data.get("approved_at") else None,
            approval_comment=data.get("approval_comment"),
            total_work_days=data.get("total_work_days", 0),
            total_work_minutes=data.get("total_work_minutes", 0),
            total_overtime_minutes=data.get("total_overtime_minutes", 0),
            total_night_overtime_minutes=data.get("total_night_overtime_minutes", 0),
            total_holiday_work_minutes=data.get("total_holiday_work_minutes", 0),
            total_extra_holiday_work_minutes=data.get("total_extra_holiday_work_minutes", 0),
            total_late_minutes=data.get("total_late_minutes", 0),
            total_early_leave_minutes=data.get("total_early_leave_minutes", 0),
            total_paid_leave_days=float(data.get("total_paid_leave_days", 0)),
            total_absence_days=float(data.get("total_absence_days", 0)),
            total_special_leave_days=float(data.get("total_special_leave_days", 0)),
            total_condolence_leave_days=float(data.get("total_condolence_leave_days", 0)),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
