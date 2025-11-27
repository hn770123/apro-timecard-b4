"""
設定モジュール
環境変数から設定値を読み込む
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    アプリケーション設定クラス
    環境変数から設定値を読み込む
    """
    # アプリケーション設定
    app_name: str = "勤務月報システム"  # アプリケーション名
    debug: bool = False  # デバッグモード

    # AWS設定
    aws_region: str = "ap-northeast-1"  # AWSリージョン
    dynamodb_endpoint: str | None = None  # DynamoDBエンドポイント（ローカル開発用）

    # DynamoDBテーブル名
    users_table: str = "timecard-users"  # ユーザーテーブル
    work_patterns_table: str = "timecard-work-patterns"  # 勤務パターンテーブル
    monthly_records_table: str = "timecard-monthly-records"  # 月次記録テーブル
    daily_records_table: str = "timecard-daily-records"  # 日次記録テーブル

    # JWT設定
    secret_key: str = "your-secret-key-change-in-production"  # JWT秘密鍵
    algorithm: str = "HS256"  # JWTアルゴリズム
    access_token_expire_minutes: int = 60  # アクセストークン有効期限（分）

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    """
    設定インスタンスを取得（シングルトン）
    キャッシュを使用してパフォーマンスを向上
    """
    return Settings()
