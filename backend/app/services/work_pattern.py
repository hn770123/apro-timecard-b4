"""
勤務パターンサービス
勤務パターン管理のビジネスロジック
"""
import uuid
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from ..config import get_settings
from ..models.work_pattern import WorkPattern, BreakTime
from ..services.dynamodb import DynamoDBService


class WorkPatternService:
    """
    勤務パターンサービスクラス
    勤務パターンのCRUD操作を提供
    """
    
    def __init__(self, db_service: DynamoDBService):
        """
        サービスを初期化
        
        Args:
            db_service: DynamoDBサービス
        """
        self.db_service = db_service
        self.settings = get_settings()
        self.table = db_service.get_table(self.settings.work_patterns_table)

    def create_pattern(
        self,
        user_id: str,
        pattern_number: int,
        start_time: str,
        end_time: str,
        break_times: list[dict],
        year_month: str,
    ) -> WorkPattern:
        """
        勤務パターンを作成
        
        Args:
            user_id: ユーザーID
            pattern_number: パターン番号（1-3）
            start_time: 始業時刻
            end_time: 終業時刻
            break_times: 休憩時間リスト
            year_month: 年月
            
        Returns:
            作成された勤務パターン
        """
        # 既存パターンのチェック（同じ月、同じパターン番号は上書き）
        existing = self.get_pattern_by_user_month_number(user_id, year_month, pattern_number)
        if existing:
            # 既存パターンを更新
            return self.update_pattern(
                existing.pattern_id,
                start_time=start_time,
                end_time=end_time,
                break_times=break_times,
            )
        
        # 新規パターン作成
        pattern = WorkPattern(
            pattern_id=str(uuid.uuid4()),
            user_id=user_id,
            pattern_number=pattern_number,
            start_time=start_time,
            end_time=end_time,
            break_times=[BreakTime.from_dict(bt) for bt in break_times],
            year_month=year_month,
        )
        
        # DynamoDBに保存
        self.table.put_item(Item=pattern.to_dict())
        
        return pattern

    def get_pattern(self, pattern_id: str) -> Optional[WorkPattern]:
        """
        勤務パターンをIDで取得
        
        Args:
            pattern_id: パターンID
            
        Returns:
            勤務パターンまたはNone
        """
        try:
            response = self.table.get_item(Key={"pattern_id": pattern_id})
            if "Item" in response:
                return WorkPattern.from_dict(response["Item"])
            return None
        except ClientError:
            return None

    def get_patterns_by_user_month(self, user_id: str, year_month: str) -> list[WorkPattern]:
        """
        ユーザーの月別勤務パターンを取得
        
        Args:
            user_id: ユーザーID
            year_month: 年月
            
        Returns:
            勤務パターンリスト
        """
        try:
            response = self.table.query(
                IndexName="user-month-index",
                KeyConditionExpression=Key("user_id").eq(user_id) & Key("year_month").eq(year_month),
            )
            patterns = [WorkPattern.from_dict(item) for item in response.get("Items", [])]
            return sorted(patterns, key=lambda p: p.pattern_number)
        except ClientError:
            return []

    def get_pattern_by_user_month_number(
        self,
        user_id: str,
        year_month: str,
        pattern_number: int,
    ) -> Optional[WorkPattern]:
        """
        ユーザーの月別勤務パターンを番号で取得
        
        Args:
            user_id: ユーザーID
            year_month: 年月
            pattern_number: パターン番号
            
        Returns:
            勤務パターンまたはNone
        """
        patterns = self.get_patterns_by_user_month(user_id, year_month)
        for pattern in patterns:
            if pattern.pattern_number == pattern_number:
                return pattern
        return None

    def update_pattern(
        self,
        pattern_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        break_times: Optional[list[dict]] = None,
    ) -> Optional[WorkPattern]:
        """
        勤務パターンを更新
        
        Args:
            pattern_id: パターンID
            start_time: 始業時刻
            end_time: 終業時刻
            break_times: 休憩時間リスト
            
        Returns:
            更新された勤務パターンまたはNone
        """
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return None
        
        # フィールドを更新
        if start_time is not None:
            pattern.start_time = start_time
        if end_time is not None:
            pattern.end_time = end_time
        if break_times is not None:
            pattern.break_times = [BreakTime.from_dict(bt) for bt in break_times]
        
        pattern.updated_at = datetime.now()
        
        # DynamoDBに保存
        self.table.put_item(Item=pattern.to_dict())
        
        return pattern

    def delete_pattern(self, pattern_id: str) -> bool:
        """
        勤務パターンを削除
        
        Args:
            pattern_id: パターンID
            
        Returns:
            削除成功したかどうか
        """
        try:
            self.table.delete_item(Key={"pattern_id": pattern_id})
            return True
        except ClientError:
            return False

    def copy_patterns_from_previous_month(
        self,
        user_id: str,
        target_year_month: str,
    ) -> list[WorkPattern]:
        """
        前月のパターンを当月にコピー
        
        Args:
            user_id: ユーザーID
            target_year_month: 対象年月
            
        Returns:
            コピーされた勤務パターンリスト
        """
        # 前月を計算
        year, month = map(int, target_year_month.split("-"))
        if month == 1:
            prev_year_month = f"{year - 1}-12"
        else:
            prev_year_month = f"{year}-{month - 1:02d}"
        
        # 前月のパターンを取得
        prev_patterns = self.get_patterns_by_user_month(user_id, prev_year_month)
        
        # 当月にコピー
        new_patterns = []
        for prev in prev_patterns:
            pattern = self.create_pattern(
                user_id=user_id,
                pattern_number=prev.pattern_number,
                start_time=prev.start_time,
                end_time=prev.end_time,
                break_times=[bt.to_dict() for bt in prev.break_times],
                year_month=target_year_month,
            )
            new_patterns.append(pattern)
        
        return new_patterns
