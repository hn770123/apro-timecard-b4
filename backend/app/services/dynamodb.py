"""
DynamoDBサービス
DynamoDBへの接続とテーブル操作を提供
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Any
from ..config import get_settings


class DynamoDBService:
    """
    DynamoDBサービスクラス
    テーブル操作の共通機能を提供
    """
    
    def __init__(self):
        """
        DynamoDBクライアントを初期化
        ローカル開発時はエンドポイントを指定可能
        """
        settings = get_settings()
        
        # DynamoDBクライアント設定
        config = {
            "region_name": settings.aws_region,
        }
        
        # ローカル開発用エンドポイント
        if settings.dynamodb_endpoint:
            config["endpoint_url"] = settings.dynamodb_endpoint
        
        self.dynamodb = boto3.resource("dynamodb", **config)
        self.client = boto3.client("dynamodb", **config)
        self.settings = settings

    def get_table(self, table_name: str):
        """
        テーブルオブジェクトを取得
        """
        return self.dynamodb.Table(table_name)

    def create_tables(self) -> None:
        """
        必要なテーブルを作成（開発/テスト用）
        """
        tables_config = [
            {
                "TableName": self.settings.users_table,
                "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                "AttributeDefinitions": [
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "email", "AttributeType": "S"},
                ],
                "GlobalSecondaryIndexes": [
                    {
                        "IndexName": "email-index",
                        "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                    }
                ],
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            },
            {
                "TableName": self.settings.work_patterns_table,
                "KeySchema": [{"AttributeName": "pattern_id", "KeyType": "HASH"}],
                "AttributeDefinitions": [
                    {"AttributeName": "pattern_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "year_month", "AttributeType": "S"},
                ],
                "GlobalSecondaryIndexes": [
                    {
                        "IndexName": "user-month-index",
                        "KeySchema": [
                            {"AttributeName": "user_id", "KeyType": "HASH"},
                            {"AttributeName": "year_month", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                    }
                ],
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            },
            {
                "TableName": self.settings.monthly_records_table,
                "KeySchema": [{"AttributeName": "record_id", "KeyType": "HASH"}],
                "AttributeDefinitions": [
                    {"AttributeName": "record_id", "AttributeType": "S"},
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "year_month", "AttributeType": "S"},
                ],
                "GlobalSecondaryIndexes": [
                    {
                        "IndexName": "user-month-index",
                        "KeySchema": [
                            {"AttributeName": "user_id", "KeyType": "HASH"},
                            {"AttributeName": "year_month", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                    }
                ],
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            },
            {
                "TableName": self.settings.daily_records_table,
                "KeySchema": [{"AttributeName": "record_id", "KeyType": "HASH"}],
                "AttributeDefinitions": [
                    {"AttributeName": "record_id", "AttributeType": "S"},
                    {"AttributeName": "monthly_record_id", "AttributeType": "S"},
                    {"AttributeName": "record_date", "AttributeType": "S"},
                ],
                "GlobalSecondaryIndexes": [
                    {
                        "IndexName": "monthly-date-index",
                        "KeySchema": [
                            {"AttributeName": "monthly_record_id", "KeyType": "HASH"},
                            {"AttributeName": "record_date", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                    }
                ],
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            },
        ]

        for table_config in tables_config:
            try:
                self.dynamodb.create_table(**table_config)
            except ClientError as e:
                if e.response["Error"]["Code"] != "ResourceInUseException":
                    raise

    def delete_tables(self) -> None:
        """
        テーブルを削除（テスト用）
        """
        table_names = [
            self.settings.users_table,
            self.settings.work_patterns_table,
            self.settings.monthly_records_table,
            self.settings.daily_records_table,
        ]
        
        for table_name in table_names:
            try:
                table = self.get_table(table_name)
                table.delete()
            except ClientError:
                pass
