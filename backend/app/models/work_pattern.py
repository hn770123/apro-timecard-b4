"""
勤務パターンモデル
勤務時間と休憩時間のパターンを定義
"""
from dataclasses import dataclass, field
from datetime import time, datetime
from typing import Optional


@dataclass
class BreakTime:
    """
    休憩時間モデル
    開始時刻と終了時刻のペア
    """
    start_time: str  # 休憩開始時刻 (HH:MM形式)
    end_time: str  # 休憩終了時刻 (HH:MM形式)

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BreakTime":
        """辞書からインスタンスを生成"""
        return cls(
            start_time=data["start_time"],
            end_time=data["end_time"],
        )

    def get_duration_minutes(self) -> int:
        """
        休憩時間を分単位で計算
        """
        start_parts = self.start_time.split(":")
        end_parts = self.end_time.split(":")
        start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
        end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])
        return end_minutes - start_minutes


@dataclass
class WorkPattern:
    """
    勤務パターンモデル
    始業～終業時刻と休憩時間を管理
    
    ユーザーごとに最大3パターンまで登録可能
    各パターンに最大3つの休憩時間を設定可能
    """
    pattern_id: str  # パターンID（主キー）
    user_id: str  # ユーザーID
    pattern_number: int  # パターン番号（1-3）
    start_time: str  # 始業時刻 (HH:MM形式)
    end_time: str  # 終業時刻 (HH:MM形式)
    break_times: list[BreakTime] = field(default_factory=list)  # 休憩時間リスト（最大3つ）
    year_month: str = ""  # 年月 (YYYY-MM形式)
    created_at: datetime = field(default_factory=datetime.now)  # 作成日時
    updated_at: datetime = field(default_factory=datetime.now)  # 更新日時

    def get_scheduled_work_minutes(self) -> int:
        """
        所定労働時間を分単位で計算
        （始業～終業時間 - 休憩時間）
        """
        start_parts = self.start_time.split(":")
        end_parts = self.end_time.split(":")
        start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
        end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])
        
        work_minutes = end_minutes - start_minutes
        
        # 休憩時間を減算
        for break_time in self.break_times:
            work_minutes -= break_time.get_duration_minutes()
        
        return work_minutes

    def to_dict(self) -> dict:
        """辞書形式に変換（DynamoDB保存用）"""
        return {
            "pattern_id": self.pattern_id,
            "user_id": self.user_id,
            "pattern_number": self.pattern_number,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "break_times": [bt.to_dict() for bt in self.break_times],
            "year_month": self.year_month,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkPattern":
        """辞書からインスタンスを生成"""
        return cls(
            pattern_id=data["pattern_id"],
            user_id=data["user_id"],
            pattern_number=data["pattern_number"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            break_times=[BreakTime.from_dict(bt) for bt in data.get("break_times", [])],
            year_month=data.get("year_month", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
