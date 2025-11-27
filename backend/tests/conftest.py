"""
テスト用共通設定とフィクスチャ
"""
import pytest
import os
from unittest.mock import MagicMock, patch
from datetime import datetime
from moto import mock_aws

# テスト用環境変数
os.environ["AWS_DEFAULT_REGION"] = "ap-northeast-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["DYNAMODB_ENDPOINT"] = "http://localhost:8000"


@pytest.fixture
def mock_dynamodb():
    """
    DynamoDBモックを提供するフィクスチャ
    """
    with mock_aws():
        from backend.app.services.dynamodb import DynamoDBService
        db_service = DynamoDBService()
        db_service.create_tables()
        yield db_service


@pytest.fixture
def auth_service():
    """
    認証サービスを提供するフィクスチャ
    """
    from backend.app.services.auth import AuthService
    return AuthService()


@pytest.fixture
def sample_user():
    """
    サンプルユーザーデータを提供
    """
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "テスト太郎",
        "department": "開発部",
        "is_approver": False,
        "is_admin": False,
    }


@pytest.fixture
def sample_work_pattern():
    """
    サンプル勤務パターンデータを提供
    """
    return {
        "pattern_number": 1,
        "start_time": "09:00",
        "end_time": "18:00",
        "break_times": [
            {"start_time": "12:00", "end_time": "13:00"},
        ],
        "year_month": "2024-01",
    }


@pytest.fixture
def sample_monthly_record():
    """
    サンプル月次記録データを提供
    """
    return {
        "year_month": "2024-01",
        "name": "テスト太郎",
        "department": "開発部",
        "standard_work_hours": 8.0,
    }


@pytest.fixture
def sample_daily_record():
    """
    サンプル日次記録データを提供
    """
    return {
        "record_date": "2024-01-15",
        "work_type": "work",
        "leave_type": "none",
        "pattern_number": 1,
        "start_time": "09:00",
        "end_time": "18:00",
        "note": None,
    }
