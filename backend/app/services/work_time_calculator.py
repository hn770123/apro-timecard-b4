"""
勤務時間計算サービス
勤務時間、残業時間の自動計算ロジック
"""
from typing import Optional
from ..models.work_pattern import WorkPattern
from ..models.daily_record import DailyRecord, WorkType


class WorkTimeCalculator:
    """
    勤務時間計算サービスクラス
    
    残業時間の分類:
    - 通常残業: 1日標準就労時間を超えた時間
    - 深夜早朝残業: 22:00～5:00の間の労働時間
    - 法定休日残業: 法定休日の労働時間
    - 法定外休日残業: 法定外休日の労働時間
    """
    
    # 深夜早朝時間帯の定義（分単位）
    NIGHT_START = 22 * 60  # 22:00
    NIGHT_END = 24 * 60 + 5 * 60  # 翌5:00（24:00 + 5:00 = 29:00として計算）
    EARLY_MORNING_END = 5 * 60  # 5:00
    
    def __init__(self, standard_work_hours: float = 8.0):
        """
        計算機を初期化
        
        Args:
            standard_work_hours: 1日標準就労時間（時間単位）
        """
        self.standard_work_minutes = int(standard_work_hours * 60)

    @staticmethod
    def time_to_minutes(time_str: Optional[str]) -> Optional[int]:
        """
        時刻文字列を分に変換
        
        Args:
            time_str: 時刻文字列 (HH:MM形式)
            
        Returns:
            分単位の時刻またはNone
        """
        if not time_str:
            return None
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])

    def calculate_work_minutes(
        self,
        start_time: Optional[str],
        end_time: Optional[str],
        pattern: Optional[WorkPattern],
    ) -> int:
        """
        実労働時間を計算（休憩時間を除く）
        
        Args:
            start_time: 出勤時刻
            end_time: 退勤時刻
            pattern: 勤務パターン
            
        Returns:
            実労働時間（分）
        """
        start = self.time_to_minutes(start_time)
        end = self.time_to_minutes(end_time)
        
        if start is None or end is None:
            return 0
        
        # 日をまたぐ場合の処理
        if end < start:
            end += 24 * 60
        
        work_minutes = end - start
        
        # 休憩時間を減算
        if pattern:
            for break_time in pattern.break_times:
                break_start = self.time_to_minutes(break_time.start_time)
                break_end = self.time_to_minutes(break_time.end_time)
                
                if break_start is not None and break_end is not None:
                    # 休憩時間が勤務時間内にある場合のみ減算
                    if break_start >= start and break_end <= end:
                        work_minutes -= (break_end - break_start)
        
        return max(0, work_minutes)

    def calculate_late_minutes(
        self,
        start_time: Optional[str],
        pattern: Optional[WorkPattern],
    ) -> int:
        """
        遅刻時間を計算
        
        Args:
            start_time: 出勤時刻
            pattern: 勤務パターン
            
        Returns:
            遅刻時間（分）
        """
        if not start_time or not pattern:
            return 0
        
        actual_start = self.time_to_minutes(start_time)
        scheduled_start = self.time_to_minutes(pattern.start_time)
        
        if actual_start is None or scheduled_start is None:
            return 0
        
        return max(0, actual_start - scheduled_start)

    def calculate_early_leave_minutes(
        self,
        end_time: Optional[str],
        pattern: Optional[WorkPattern],
    ) -> int:
        """
        早退時間を計算
        
        Args:
            end_time: 退勤時刻
            pattern: 勤務パターン
            
        Returns:
            早退時間（分）
        """
        if not end_time or not pattern:
            return 0
        
        actual_end = self.time_to_minutes(end_time)
        scheduled_end = self.time_to_minutes(pattern.end_time)
        
        if actual_end is None or scheduled_end is None:
            return 0
        
        return max(0, scheduled_end - actual_end)

    def calculate_overtime_minutes(
        self,
        work_minutes: int,
        work_type: WorkType,
    ) -> int:
        """
        通常残業時間を計算
        
        休日の場合は標準就労時間が0のため、全て残業に計上
        
        Args:
            work_minutes: 実労働時間（分）
            work_type: 勤務種類
            
        Returns:
            残業時間（分）
        """
        # 休日の場合は全て残業
        if work_type in [WorkType.HOLIDAY_LEGAL, WorkType.HOLIDAY_EXTRA]:
            return work_minutes
        
        # 通常日の場合は標準就労時間を超えた分
        return max(0, work_minutes - self.standard_work_minutes)

    def calculate_night_overtime_minutes(
        self,
        start_time: Optional[str],
        end_time: Optional[str],
        pattern: Optional[WorkPattern],
    ) -> int:
        """
        深夜早朝残業時間を計算（22:00～5:00）
        
        Args:
            start_time: 出勤時刻
            end_time: 退勤時刻
            pattern: 勤務パターン
            
        Returns:
            深夜早朝残業時間（分）
        """
        start = self.time_to_minutes(start_time)
        end = self.time_to_minutes(end_time)
        
        if start is None or end is None:
            return 0
        
        # 日をまたぐ場合の処理
        if end < start:
            end += 24 * 60
        
        night_minutes = 0
        
        # 早朝部分（0:00～5:00）
        if start < self.EARLY_MORNING_END:
            night_minutes += min(end, self.EARLY_MORNING_END) - start
        
        # 深夜部分（22:00～24:00+）
        if end > self.NIGHT_START:
            actual_start = max(start, self.NIGHT_START)
            actual_end = min(end, self.NIGHT_END)
            if actual_end > actual_start:
                night_minutes += actual_end - actual_start
        
        # 休憩時間を考慮（深夜時間帯かつ勤務時間内の休憩は減算）
        if pattern:
            for break_time in pattern.break_times:
                break_start = self.time_to_minutes(break_time.start_time)
                break_end = self.time_to_minutes(break_time.end_time)
                
                if break_start is not None and break_end is not None:
                    # 休憩が勤務時間内にある場合のみ処理
                    if break_start >= start and break_end <= end:
                        # 深夜帯の休憩時間を計算
                        # 早朝部分（0:00-5:00）
                        if break_start < self.EARLY_MORNING_END:
                            night_minutes -= min(break_end, self.EARLY_MORNING_END) - break_start
                        # 深夜部分（22:00-24:00+）
                        if break_end > self.NIGHT_START:
                            actual_break_start = max(break_start, self.NIGHT_START)
                            if break_end > actual_break_start:
                                night_minutes -= break_end - actual_break_start
        
        return max(0, night_minutes)

    def calculate_daily_record_times(
        self,
        record: DailyRecord,
        pattern: Optional[WorkPattern],
    ) -> DailyRecord:
        """
        日次記録の時間を計算
        
        Args:
            record: 日次記録
            pattern: 勤務パターン
            
        Returns:
            計算済みの日次記録
        """
        # 実労働時間
        record.work_minutes = self.calculate_work_minutes(
            record.start_time,
            record.end_time,
            pattern,
        )
        
        # 遅刻時間
        if record.work_type in [WorkType.LATE, WorkType.LATE_AND_EARLY]:
            record.late_minutes = self.calculate_late_minutes(
                record.start_time,
                pattern,
            )
        
        # 早退時間
        if record.work_type in [WorkType.EARLY_LEAVE, WorkType.LATE_AND_EARLY]:
            record.early_leave_minutes = self.calculate_early_leave_minutes(
                record.end_time,
                pattern,
            )
        
        # 残業時間の分類
        if record.work_type == WorkType.HOLIDAY_LEGAL:
            # 法定休日
            record.holiday_work_minutes = record.work_minutes
            record.overtime_minutes = 0
        elif record.work_type == WorkType.HOLIDAY_EXTRA:
            # 法定外休日
            record.extra_holiday_work_minutes = record.work_minutes
            record.overtime_minutes = 0
        else:
            # 通常日
            record.overtime_minutes = self.calculate_overtime_minutes(
                record.work_minutes,
                record.work_type,
            )
        
        # 深夜早朝残業
        record.night_overtime_minutes = self.calculate_night_overtime_minutes(
            record.start_time,
            record.end_time,
            pattern,
        )
        
        # 補足欄必須フラグ
        record.is_note_required = record.should_require_note()
        
        return record
