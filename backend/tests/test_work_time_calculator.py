"""
勤務時間計算サービスのテスト
"""
import pytest
from backend.app.services.work_time_calculator import WorkTimeCalculator
from backend.app.models.work_pattern import WorkPattern, BreakTime
from backend.app.models.daily_record import DailyRecord, WorkType, LeaveType


class TestWorkTimeCalculator:
    """
    勤務時間計算サービスのテストクラス
    """

    def test_time_to_minutes(self):
        """時刻文字列を分に変換するテスト"""
        assert WorkTimeCalculator.time_to_minutes("09:00") == 540
        assert WorkTimeCalculator.time_to_minutes("18:00") == 1080
        assert WorkTimeCalculator.time_to_minutes("00:00") == 0
        assert WorkTimeCalculator.time_to_minutes("23:59") == 1439
        assert WorkTimeCalculator.time_to_minutes(None) is None

    def test_calculate_work_minutes_basic(self):
        """基本的な実労働時間計算のテスト"""
        calculator = WorkTimeCalculator(8.0)
        
        # 9:00-18:00で休憩なしの場合
        pattern = WorkPattern(
            pattern_id="test",
            user_id="user1",
            pattern_number=1,
            start_time="09:00",
            end_time="18:00",
            break_times=[],
            year_month="2024-01",
        )
        
        result = calculator.calculate_work_minutes("09:00", "18:00", pattern)
        assert result == 540  # 9時間 = 540分

    def test_calculate_work_minutes_with_break(self):
        """休憩時間を含む実労働時間計算のテスト"""
        calculator = WorkTimeCalculator(8.0)
        
        # 9:00-18:00で1時間休憩の場合
        pattern = WorkPattern(
            pattern_id="test",
            user_id="user1",
            pattern_number=1,
            start_time="09:00",
            end_time="18:00",
            break_times=[BreakTime(start_time="12:00", end_time="13:00")],
            year_month="2024-01",
        )
        
        result = calculator.calculate_work_minutes("09:00", "18:00", pattern)
        assert result == 480  # 8時間 = 480分

    def test_calculate_late_minutes(self):
        """遅刻時間計算のテスト"""
        calculator = WorkTimeCalculator(8.0)
        
        pattern = WorkPattern(
            pattern_id="test",
            user_id="user1",
            pattern_number=1,
            start_time="09:00",
            end_time="18:00",
            break_times=[],
            year_month="2024-01",
        )
        
        # 30分遅刻
        result = calculator.calculate_late_minutes("09:30", pattern)
        assert result == 30
        
        # 遅刻なし
        result = calculator.calculate_late_minutes("09:00", pattern)
        assert result == 0
        
        # 早出
        result = calculator.calculate_late_minutes("08:30", pattern)
        assert result == 0

    def test_calculate_early_leave_minutes(self):
        """早退時間計算のテスト"""
        calculator = WorkTimeCalculator(8.0)
        
        pattern = WorkPattern(
            pattern_id="test",
            user_id="user1",
            pattern_number=1,
            start_time="09:00",
            end_time="18:00",
            break_times=[],
            year_month="2024-01",
        )
        
        # 1時間早退
        result = calculator.calculate_early_leave_minutes("17:00", pattern)
        assert result == 60
        
        # 早退なし
        result = calculator.calculate_early_leave_minutes("18:00", pattern)
        assert result == 0
        
        # 残業
        result = calculator.calculate_early_leave_minutes("19:00", pattern)
        assert result == 0

    def test_calculate_overtime_minutes_regular(self):
        """通常日の残業時間計算のテスト"""
        calculator = WorkTimeCalculator(8.0)  # 8時間 = 480分
        
        # 1時間残業
        result = calculator.calculate_overtime_minutes(540, WorkType.WORK)
        assert result == 60
        
        # 残業なし
        result = calculator.calculate_overtime_minutes(480, WorkType.WORK)
        assert result == 0
        
        # 労働時間不足
        result = calculator.calculate_overtime_minutes(420, WorkType.WORK)
        assert result == 0

    def test_calculate_overtime_minutes_holiday(self):
        """休日の残業時間計算のテスト"""
        calculator = WorkTimeCalculator(8.0)
        
        # 法定休日は全て残業に計上
        result = calculator.calculate_overtime_minutes(480, WorkType.HOLIDAY_LEGAL)
        assert result == 480
        
        # 法定外休日も全て残業に計上
        result = calculator.calculate_overtime_minutes(480, WorkType.HOLIDAY_EXTRA)
        assert result == 480

    def test_calculate_night_overtime_minutes_early_morning(self):
        """深夜早朝残業時間計算のテスト（早朝）"""
        calculator = WorkTimeCalculator(8.0)
        
        pattern = WorkPattern(
            pattern_id="test",
            user_id="user1",
            pattern_number=1,
            start_time="03:00",
            end_time="12:00",
            break_times=[],
            year_month="2024-01",
        )
        
        # 3:00-5:00は深夜帯（2時間 = 120分）
        result = calculator.calculate_night_overtime_minutes("03:00", "12:00", pattern)
        assert result == 120

    def test_calculate_night_overtime_minutes_late_night(self):
        """深夜早朝残業時間計算のテスト（深夜）"""
        calculator = WorkTimeCalculator(8.0)
        
        pattern = WorkPattern(
            pattern_id="test",
            user_id="user1",
            pattern_number=1,
            start_time="18:00",
            end_time="23:00",
            break_times=[],
            year_month="2024-01",
        )
        
        # 22:00-23:00は深夜帯（1時間 = 60分）
        result = calculator.calculate_night_overtime_minutes("18:00", "23:00", pattern)
        assert result == 60

    def test_calculate_daily_record_times(self):
        """日次記録の時間計算テスト"""
        calculator = WorkTimeCalculator(8.0)
        
        pattern = WorkPattern(
            pattern_id="test",
            user_id="user1",
            pattern_number=1,
            start_time="09:00",
            end_time="18:00",
            break_times=[BreakTime(start_time="12:00", end_time="13:00")],
            year_month="2024-01",
        )
        
        record = DailyRecord(
            record_id="test",
            user_id="user1",
            monthly_record_id="monthly1",
            record_date="2024-01-15",
            work_type=WorkType.WORK,
            leave_type=LeaveType.NONE,
            pattern_number=1,
            start_time="09:00",
            end_time="19:00",
        )
        
        result = calculator.calculate_daily_record_times(record, pattern)
        
        # 実労働時間: 10時間 - 1時間休憩 = 9時間 = 540分
        assert result.work_minutes == 540
        # 残業時間: 9時間 - 8時間 = 1時間 = 60分
        assert result.overtime_minutes == 60
        # 遅刻なし
        assert result.late_minutes == 0
        # 早退なし
        assert result.early_leave_minutes == 0

    def test_calculate_daily_record_times_holiday_legal(self):
        """法定休日の時間計算テスト"""
        calculator = WorkTimeCalculator(8.0)
        
        pattern = WorkPattern(
            pattern_id="test",
            user_id="user1",
            pattern_number=1,
            start_time="09:00",
            end_time="18:00",
            break_times=[],
            year_month="2024-01",
        )
        
        record = DailyRecord(
            record_id="test",
            user_id="user1",
            monthly_record_id="monthly1",
            record_date="2024-01-15",
            work_type=WorkType.HOLIDAY_LEGAL,
            leave_type=LeaveType.NONE,
            pattern_number=1,
            start_time="09:00",
            end_time="18:00",
        )
        
        result = calculator.calculate_daily_record_times(record, pattern)
        
        # 法定休日は全て残業に計上
        assert result.work_minutes == 540
        assert result.holiday_work_minutes == 540
        assert result.overtime_minutes == 0
