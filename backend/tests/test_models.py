"""
モデルのテスト
"""
import pytest
from datetime import datetime
from backend.app.models.user import User, UserRole
from backend.app.models.work_pattern import WorkPattern, BreakTime
from backend.app.models.monthly_record import MonthlyRecord, ApprovalStatus
from backend.app.models.daily_record import DailyRecord, WorkType, LeaveType


class TestUserModel:
    """ユーザーモデルのテストクラス"""

    def test_user_creation(self):
        """ユーザー作成テスト"""
        user = User(
            user_id="test-id",
            email="test@example.com",
            password_hash="hashed",
            name="テスト太郎",
            department="開発部",
        )
        
        assert user.user_id == "test-id"
        assert user.email == "test@example.com"
        assert user.name == "テスト太郎"
        assert user.is_approver is False
        assert user.is_admin is False
        assert user.is_active is True

    def test_user_get_roles_general(self):
        """一般ユーザーの権限取得テスト"""
        user = User(
            user_id="test-id",
            email="test@example.com",
            password_hash="hashed",
            name="テスト太郎",
            department="開発部",
        )
        
        roles = user.get_roles()
        assert roles == ["general"]

    def test_user_get_roles_approver(self):
        """承認者の権限取得テスト"""
        user = User(
            user_id="test-id",
            email="test@example.com",
            password_hash="hashed",
            name="テスト太郎",
            department="開発部",
            is_approver=True,
        )
        
        roles = user.get_roles()
        assert "general" in roles
        assert "approver" in roles
        assert "admin" not in roles

    def test_user_get_roles_admin(self):
        """管理者の権限取得テスト"""
        user = User(
            user_id="test-id",
            email="test@example.com",
            password_hash="hashed",
            name="テスト太郎",
            department="開発部",
            is_admin=True,
        )
        
        roles = user.get_roles()
        assert "general" in roles
        assert "approver" not in roles
        assert "admin" in roles

    def test_user_get_roles_both(self):
        """承認者かつ管理者の権限取得テスト"""
        user = User(
            user_id="test-id",
            email="test@example.com",
            password_hash="hashed",
            name="テスト太郎",
            department="開発部",
            is_approver=True,
            is_admin=True,
        )
        
        roles = user.get_roles()
        assert "general" in roles
        assert "approver" in roles
        assert "admin" in roles

    def test_user_to_dict(self):
        """辞書変換テスト"""
        user = User(
            user_id="test-id",
            email="test@example.com",
            password_hash="hashed",
            name="テスト太郎",
            department="開発部",
        )
        
        data = user.to_dict()
        assert data["user_id"] == "test-id"
        assert data["email"] == "test@example.com"
        assert "created_at" in data

    def test_user_from_dict(self):
        """辞書からの復元テスト"""
        now = datetime.now()
        data = {
            "user_id": "test-id",
            "email": "test@example.com",
            "password_hash": "hashed",
            "name": "テスト太郎",
            "department": "開発部",
            "is_approver": True,
            "is_admin": False,
            "is_active": True,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        
        user = User.from_dict(data)
        assert user.user_id == "test-id"
        assert user.is_approver is True


class TestWorkPatternModel:
    """勤務パターンモデルのテストクラス"""

    def test_work_pattern_creation(self):
        """勤務パターン作成テスト"""
        pattern = WorkPattern(
            pattern_id="pattern-id",
            user_id="user-id",
            pattern_number=1,
            start_time="09:00",
            end_time="18:00",
            year_month="2024-01",
        )
        
        assert pattern.pattern_number == 1
        assert pattern.start_time == "09:00"

    def test_work_pattern_with_breaks(self):
        """休憩時間を含む勤務パターンテスト"""
        pattern = WorkPattern(
            pattern_id="pattern-id",
            user_id="user-id",
            pattern_number=1,
            start_time="09:00",
            end_time="18:00",
            break_times=[
                BreakTime(start_time="12:00", end_time="13:00"),
            ],
            year_month="2024-01",
        )
        
        assert len(pattern.break_times) == 1
        assert pattern.break_times[0].get_duration_minutes() == 60

    def test_get_scheduled_work_minutes(self):
        """所定労働時間計算テスト"""
        pattern = WorkPattern(
            pattern_id="pattern-id",
            user_id="user-id",
            pattern_number=1,
            start_time="09:00",
            end_time="18:00",
            break_times=[
                BreakTime(start_time="12:00", end_time="13:00"),
            ],
            year_month="2024-01",
        )
        
        # 9時間 - 1時間休憩 = 8時間 = 480分
        assert pattern.get_scheduled_work_minutes() == 480


class TestMonthlyRecordModel:
    """月次記録モデルのテストクラス"""

    def test_monthly_record_creation(self):
        """月次記録作成テスト"""
        record = MonthlyRecord(
            record_id="record-id",
            user_id="user-id",
            year_month="2024-01",
            name="テスト太郎",
            department="開発部",
        )
        
        assert record.status == ApprovalStatus.DRAFT
        assert record.standard_work_hours == 8.0
        assert record.is_locked() is False
        assert record.can_edit() is True

    def test_monthly_record_locked_when_approved(self):
        """承認時のロック状態テスト"""
        record = MonthlyRecord(
            record_id="record-id",
            user_id="user-id",
            year_month="2024-01",
            name="テスト太郎",
            department="開発部",
            status=ApprovalStatus.APPROVED,
        )
        
        assert record.is_locked() is True
        assert record.can_edit() is False

    def test_monthly_record_editable_when_rejected(self):
        """差し戻し時の編集可能状態テスト"""
        record = MonthlyRecord(
            record_id="record-id",
            user_id="user-id",
            year_month="2024-01",
            name="テスト太郎",
            department="開発部",
            status=ApprovalStatus.REJECTED,
        )
        
        assert record.is_locked() is False
        assert record.can_edit() is True


class TestDailyRecordModel:
    """日次記録モデルのテストクラス"""

    def test_daily_record_creation(self):
        """日次記録作成テスト"""
        record = DailyRecord(
            record_id="record-id",
            user_id="user-id",
            monthly_record_id="monthly-id",
            record_date="2024-01-15",
        )
        
        assert record.work_type == WorkType.WORK
        assert record.leave_type == LeaveType.NONE
        assert record.pattern_number == 1

    def test_should_require_note_for_holiday(self):
        """休日の補足入力必須判定テスト"""
        record = DailyRecord(
            record_id="record-id",
            user_id="user-id",
            monthly_record_id="monthly-id",
            record_date="2024-01-15",
            work_type=WorkType.HOLIDAY_LEGAL,
        )
        
        assert record.should_require_note() is True

    def test_should_not_require_note_for_work(self):
        """出勤時の補足入力不要判定テスト"""
        record = DailyRecord(
            record_id="record-id",
            user_id="user-id",
            monthly_record_id="monthly-id",
            record_date="2024-01-15",
            work_type=WorkType.WORK,
        )
        
        assert record.should_require_note() is False

    def test_is_holiday(self):
        """休日判定テスト"""
        record_legal = DailyRecord(
            record_id="record-id",
            user_id="user-id",
            monthly_record_id="monthly-id",
            record_date="2024-01-15",
            work_type=WorkType.HOLIDAY_LEGAL,
        )
        
        record_extra = DailyRecord(
            record_id="record-id",
            user_id="user-id",
            monthly_record_id="monthly-id",
            record_date="2024-01-15",
            work_type=WorkType.HOLIDAY_EXTRA,
        )
        
        record_work = DailyRecord(
            record_id="record-id",
            user_id="user-id",
            monthly_record_id="monthly-id",
            record_date="2024-01-15",
            work_type=WorkType.WORK,
        )
        
        assert record_legal.is_holiday() is True
        assert record_extra.is_holiday() is True
        assert record_work.is_holiday() is False
