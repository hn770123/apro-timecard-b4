"""
日次記録サービス
日次記録管理のビジネスロジック
"""
import uuid
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from ..config import get_settings
from ..models.daily_record import DailyRecord, WorkType, LeaveType
from ..services.dynamodb import DynamoDBService
from ..services.work_time_calculator import WorkTimeCalculator


class DailyRecordService:
    """
    日次記録サービスクラス
    日次記録のCRUD操作と時間計算を提供
    """
    
    def __init__(self, db_service: DynamoDBService):
        """
        サービスを初期化
        
        Args:
            db_service: DynamoDBサービス
        """
        self.db_service = db_service
        self.settings = get_settings()
        self.table = db_service.get_table(self.settings.daily_records_table)

    def create_record(
        self,
        user_id: str,
        monthly_record_id: str,
        record_date: str,
        work_type: str = "work",
        leave_type: str = "none",
        pattern_number: int = 1,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        note: Optional[str] = None,
    ) -> DailyRecord:
        """
        日次記録を作成
        
        Args:
            user_id: ユーザーID
            monthly_record_id: 月次記録ID
            record_date: 日付
            work_type: 勤務種類
            leave_type: 休暇種類
            pattern_number: パターン番号
            start_time: 出勤時刻
            end_time: 退勤時刻
            note: 補足欄
            
        Returns:
            作成された日次記録
        """
        # 既存レコードのチェック
        existing = self.get_record_by_monthly_date(monthly_record_id, record_date)
        if existing:
            raise ValueError("この日の記録は既に存在します")
        
        record = DailyRecord(
            record_id=str(uuid.uuid4()),
            user_id=user_id,
            monthly_record_id=monthly_record_id,
            record_date=record_date,
            work_type=WorkType(work_type),
            leave_type=LeaveType(leave_type),
            pattern_number=pattern_number,
            start_time=start_time,
            end_time=end_time,
            note=note,
            is_note_required=WorkType(work_type) not in [WorkType.WORK, WorkType.REMOTE],
        )
        
        # DynamoDBに保存
        self.table.put_item(Item=record.to_dict())
        
        return record

    def get_record(self, record_id: str) -> Optional[DailyRecord]:
        """
        日次記録をIDで取得
        
        Args:
            record_id: レコードID
            
        Returns:
            日次記録またはNone
        """
        try:
            response = self.table.get_item(Key={"record_id": record_id})
            if "Item" in response:
                return DailyRecord.from_dict(response["Item"])
            return None
        except ClientError:
            return None

    def get_record_by_monthly_date(
        self,
        monthly_record_id: str,
        record_date: str,
    ) -> Optional[DailyRecord]:
        """
        月次記録と日付で日次記録を取得
        
        Args:
            monthly_record_id: 月次記録ID
            record_date: 日付
            
        Returns:
            日次記録またはNone
        """
        try:
            response = self.table.query(
                IndexName="monthly-date-index",
                KeyConditionExpression=Key("monthly_record_id").eq(monthly_record_id) & Key("record_date").eq(record_date),
            )
            if response["Items"]:
                return DailyRecord.from_dict(response["Items"][0])
            return None
        except ClientError:
            return None

    def get_records_by_monthly(self, monthly_record_id: str) -> list[DailyRecord]:
        """
        月次記録に属する全日次記録を取得
        
        Args:
            monthly_record_id: 月次記録ID
            
        Returns:
            日次記録リスト
        """
        try:
            response = self.table.query(
                IndexName="monthly-date-index",
                KeyConditionExpression=Key("monthly_record_id").eq(monthly_record_id),
            )
            records = [DailyRecord.from_dict(item) for item in response.get("Items", [])]
            return sorted(records, key=lambda r: r.record_date)
        except ClientError:
            return []

    def update_record(
        self,
        record_id: str,
        work_type: Optional[str] = None,
        leave_type: Optional[str] = None,
        pattern_number: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        late_minutes: Optional[int] = None,
        early_leave_minutes: Optional[int] = None,
        overtime_minutes: Optional[int] = None,
        note: Optional[str] = None,
    ) -> Optional[DailyRecord]:
        """
        日次記録を更新
        
        Args:
            record_id: レコードID
            その他: 更新フィールド
            
        Returns:
            更新された日次記録またはNone
        """
        record = self.get_record(record_id)
        if not record:
            return None
        
        # フィールドを更新
        if work_type is not None:
            record.work_type = WorkType(work_type)
            record.is_note_required = record.should_require_note()
        if leave_type is not None:
            record.leave_type = LeaveType(leave_type)
        if pattern_number is not None:
            record.pattern_number = pattern_number
        if start_time is not None:
            record.start_time = start_time
        if end_time is not None:
            record.end_time = end_time
        if late_minutes is not None:
            record.late_minutes = late_minutes
        if early_leave_minutes is not None:
            record.early_leave_minutes = early_leave_minutes
        if overtime_minutes is not None:
            record.overtime_minutes = overtime_minutes
        if note is not None:
            record.note = note
        
        record.updated_at = datetime.now()
        
        # DynamoDBに保存
        self.table.put_item(Item=record.to_dict())
        
        return record

    def update_calculated_times(
        self,
        record_id: str,
        calculator: WorkTimeCalculator,
        pattern,
    ) -> Optional[DailyRecord]:
        """
        日次記録の計算済み時間を更新
        
        Args:
            record_id: レコードID
            calculator: 時間計算サービス
            pattern: 勤務パターン
            
        Returns:
            更新された日次記録またはNone
        """
        record = self.get_record(record_id)
        if not record:
            return None
        
        # 時間を計算
        record = calculator.calculate_daily_record_times(record, pattern)
        record.updated_at = datetime.now()
        
        # DynamoDBに保存
        self.table.put_item(Item=record.to_dict())
        
        return record

    def delete_record(self, record_id: str) -> bool:
        """
        日次記録を削除
        
        Args:
            record_id: レコードID
            
        Returns:
            削除成功したかどうか
        """
        try:
            self.table.delete_item(Key={"record_id": record_id})
            return True
        except ClientError:
            return False

    def delete_records_by_monthly(self, monthly_record_id: str) -> bool:
        """
        月次記録に属する全日次記録を削除
        
        Args:
            monthly_record_id: 月次記録ID
            
        Returns:
            削除成功したかどうか
        """
        try:
            records = self.get_records_by_monthly(monthly_record_id)
            for record in records:
                self.delete_record(record.record_id)
            return True
        except ClientError:
            return False
