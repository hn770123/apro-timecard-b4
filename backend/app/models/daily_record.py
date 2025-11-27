"""
日次記録モデル
日ごとの勤務データを管理
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional


class WorkType(str, Enum):
    """
    勤務の種類の列挙型
    """
    WORK = "work"  # 出勤
    REMOTE = "remote"  # 出勤（リモート）
    LATE = "late"  # 遅刻
    EARLY_LEAVE = "early_leave"  # 早退
    LATE_AND_EARLY = "late_and_early"  # 遅刻かつ早退
    HOLIDAY_LEGAL = "holiday_legal"  # 休日（法定）
    HOLIDAY_EXTRA = "holiday_extra"  # 休日（法定外）


class LeaveType(str, Enum):
    """
    休暇種類の列挙型
    """
    NONE = "none"  # なし
    PAID = "paid"  # 有休
    ABSENCE = "absence"  # 欠勤
    SPECIAL = "special"  # 特休
    CONDOLENCE = "condolence"  # 慶弔


@dataclass
class DailyRecord:
    """
    日次記録モデル
    日ごとの勤務時間と種類を管理
    
    勤務時間の自動計算を行い、残業時間を種類別に分類
    """
    record_id: str  # レコードID（主キー）
    user_id: str  # ユーザーID
    monthly_record_id: str  # 月次記録ID
    record_date: str  # 日付 (YYYY-MM-DD形式)
    work_type: WorkType = WorkType.WORK  # 勤務の種類
    leave_type: LeaveType = LeaveType.NONE  # 休暇種類
    pattern_number: int = 1  # 使用する勤務パターン番号（1-3）
    start_time: Optional[str] = None  # 出勤時刻 (HH:MM形式)
    end_time: Optional[str] = None  # 退勤時刻 (HH:MM形式)
    late_minutes: int = 0  # 遅刻時間（分）- 自動計算だが変更可
    early_leave_minutes: int = 0  # 早退時間（分）- 自動計算だが変更可
    work_minutes: int = 0  # 実労働時間（分）
    overtime_minutes: int = 0  # 残業時間（分）- 自動計算だが変更可
    night_overtime_minutes: int = 0  # 深夜早朝残業時間（分）22:00～5:00
    holiday_work_minutes: int = 0  # 法定休日残業時間（分）
    extra_holiday_work_minutes: int = 0  # 法定外休日残業時間（分）
    note: Optional[str] = None  # 補足欄
    is_note_required: bool = False  # 補足入力必須フラグ
    created_at: datetime = field(default_factory=datetime.now)  # 作成日時
    updated_at: datetime = field(default_factory=datetime.now)  # 更新日時

    def should_require_note(self) -> bool:
        """
        補足欄の入力が必要かどうかを判定
        出勤以外の場合に必要
        """
        return self.work_type not in [WorkType.WORK, WorkType.REMOTE]

    def is_holiday(self) -> bool:
        """
        休日かどうかを判定
        """
        return self.work_type in [WorkType.HOLIDAY_LEGAL, WorkType.HOLIDAY_EXTRA]

    def to_dict(self) -> dict:
        """辞書形式に変換（DynamoDB保存用）"""
        return {
            "record_id": self.record_id,
            "user_id": self.user_id,
            "monthly_record_id": self.monthly_record_id,
            "record_date": self.record_date,
            "work_type": self.work_type.value,
            "leave_type": self.leave_type.value,
            "pattern_number": self.pattern_number,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "late_minutes": self.late_minutes,
            "early_leave_minutes": self.early_leave_minutes,
            "work_minutes": self.work_minutes,
            "overtime_minutes": self.overtime_minutes,
            "night_overtime_minutes": self.night_overtime_minutes,
            "holiday_work_minutes": self.holiday_work_minutes,
            "extra_holiday_work_minutes": self.extra_holiday_work_minutes,
            "note": self.note,
            "is_note_required": self.is_note_required,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DailyRecord":
        """辞書からインスタンスを生成"""
        return cls(
            record_id=data["record_id"],
            user_id=data["user_id"],
            monthly_record_id=data["monthly_record_id"],
            record_date=data["record_date"],
            work_type=WorkType(data.get("work_type", "work")),
            leave_type=LeaveType(data.get("leave_type", "none")),
            pattern_number=data.get("pattern_number", 1),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            late_minutes=data.get("late_minutes", 0),
            early_leave_minutes=data.get("early_leave_minutes", 0),
            work_minutes=data.get("work_minutes", 0),
            overtime_minutes=data.get("overtime_minutes", 0),
            night_overtime_minutes=data.get("night_overtime_minutes", 0),
            holiday_work_minutes=data.get("holiday_work_minutes", 0),
            extra_holiday_work_minutes=data.get("extra_holiday_work_minutes", 0),
            note=data.get("note"),
            is_note_required=data.get("is_note_required", False),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
