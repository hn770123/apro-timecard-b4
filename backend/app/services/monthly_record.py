"""
月次記録サービス
月次記録管理のビジネスロジック
"""
import uuid
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from ..config import get_settings
from ..models.monthly_record import MonthlyRecord, ApprovalStatus
from ..models.daily_record import LeaveType
from ..services.dynamodb import DynamoDBService


class MonthlyRecordService:
    """
    月次記録サービスクラス
    月次記録のCRUD操作と承認ワークフローを提供
    """
    
    def __init__(self, db_service: DynamoDBService):
        """
        サービスを初期化
        
        Args:
            db_service: DynamoDBサービス
        """
        self.db_service = db_service
        self.settings = get_settings()
        self.table = db_service.get_table(self.settings.monthly_records_table)

    def create_record(
        self,
        user_id: str,
        year_month: str,
        name: str,
        department: str,
        standard_work_hours: float = 8.0,
    ) -> MonthlyRecord:
        """
        月次記録を作成
        
        Args:
            user_id: ユーザーID
            year_month: 年月
            name: 氏名
            department: 所属
            standard_work_hours: 1日標準就労時間
            
        Returns:
            作成された月次記録
        """
        # 既存レコードのチェック
        existing = self.get_record_by_user_month(user_id, year_month)
        if existing:
            raise ValueError("この月の記録は既に存在します")
        
        record = MonthlyRecord(
            record_id=str(uuid.uuid4()),
            user_id=user_id,
            year_month=year_month,
            name=name,
            department=department,
            standard_work_hours=standard_work_hours,
        )
        
        # DynamoDBに保存
        self.table.put_item(Item=record.to_dict())
        
        return record

    def get_record(self, record_id: str) -> Optional[MonthlyRecord]:
        """
        月次記録をIDで取得
        
        Args:
            record_id: レコードID
            
        Returns:
            月次記録またはNone
        """
        try:
            response = self.table.get_item(Key={"record_id": record_id})
            if "Item" in response:
                return MonthlyRecord.from_dict(response["Item"])
            return None
        except ClientError:
            return None

    def get_record_by_user_month(self, user_id: str, year_month: str) -> Optional[MonthlyRecord]:
        """
        ユーザーの月別記録を取得
        
        Args:
            user_id: ユーザーID
            year_month: 年月
            
        Returns:
            月次記録またはNone
        """
        try:
            response = self.table.query(
                IndexName="user-month-index",
                KeyConditionExpression=Key("user_id").eq(user_id) & Key("year_month").eq(year_month),
            )
            if response["Items"]:
                return MonthlyRecord.from_dict(response["Items"][0])
            return None
        except ClientError:
            return None

    def update_record(
        self,
        record_id: str,
        name: Optional[str] = None,
        department: Optional[str] = None,
        standard_work_hours: Optional[float] = None,
    ) -> Optional[MonthlyRecord]:
        """
        月次記録を更新
        
        Args:
            record_id: レコードID
            name: 氏名
            department: 所属
            standard_work_hours: 1日標準就労時間
            
        Returns:
            更新された月次記録またはNone
            
        Raises:
            ValueError: ロック状態の場合
        """
        record = self.get_record(record_id)
        if not record:
            return None
        
        if not record.can_edit():
            raise ValueError("承認済みのため編集できません")
        
        # フィールドを更新
        if name is not None:
            record.name = name
        if department is not None:
            record.department = department
        if standard_work_hours is not None:
            record.standard_work_hours = standard_work_hours
        
        record.updated_at = datetime.now()
        
        # DynamoDBに保存
        self.table.put_item(Item=record.to_dict())
        
        return record

    def update_totals(
        self,
        record_id: str,
        daily_records: list,
    ) -> Optional[MonthlyRecord]:
        """
        月次記録の集計値を更新
        
        Args:
            record_id: レコードID
            daily_records: 日次記録リスト
            
        Returns:
            更新された月次記録またはNone
        """
        record = self.get_record(record_id)
        if not record:
            return None
        
        # 集計を初期化
        record.total_work_days = 0
        record.total_work_minutes = 0
        record.total_overtime_minutes = 0
        record.total_night_overtime_minutes = 0
        record.total_holiday_work_minutes = 0
        record.total_extra_holiday_work_minutes = 0
        record.total_late_minutes = 0
        record.total_early_leave_minutes = 0
        record.total_paid_leave_days = 0.0
        record.total_absence_days = 0.0
        record.total_special_leave_days = 0.0
        record.total_condolence_leave_days = 0.0
        
        # 日次記録を集計
        for daily in daily_records:
            if daily.work_minutes > 0:
                record.total_work_days += 1
            
            record.total_work_minutes += daily.work_minutes
            record.total_overtime_minutes += daily.overtime_minutes
            record.total_night_overtime_minutes += daily.night_overtime_minutes
            record.total_holiday_work_minutes += daily.holiday_work_minutes
            record.total_extra_holiday_work_minutes += daily.extra_holiday_work_minutes
            record.total_late_minutes += daily.late_minutes
            record.total_early_leave_minutes += daily.early_leave_minutes
            
            # 休暇日数
            if daily.leave_type == LeaveType.PAID:
                record.total_paid_leave_days += 1.0
            elif daily.leave_type == LeaveType.ABSENCE:
                record.total_absence_days += 1.0
            elif daily.leave_type == LeaveType.SPECIAL:
                record.total_special_leave_days += 1.0
            elif daily.leave_type == LeaveType.CONDOLENCE:
                record.total_condolence_leave_days += 1.0
        
        record.updated_at = datetime.now()
        
        # DynamoDBに保存
        self.table.put_item(Item=record.to_dict())
        
        return record

    def submit_for_approval(self, record_id: str) -> Optional[MonthlyRecord]:
        """
        承認申請
        
        Args:
            record_id: レコードID
            
        Returns:
            更新された月次記録またはNone
        """
        record = self.get_record(record_id)
        if not record:
            return None
        
        if record.status != ApprovalStatus.DRAFT and record.status != ApprovalStatus.REJECTED:
            raise ValueError("この状態では申請できません")
        
        record.status = ApprovalStatus.SUBMITTED
        record.updated_at = datetime.now()
        
        self.table.put_item(Item=record.to_dict())
        
        return record

    def approve(
        self,
        record_id: str,
        approver_id: str,
        comment: Optional[str] = None,
    ) -> Optional[MonthlyRecord]:
        """
        承認
        
        Args:
            record_id: レコードID
            approver_id: 承認者ID
            comment: コメント
            
        Returns:
            更新された月次記録またはNone
        """
        record = self.get_record(record_id)
        if not record:
            return None
        
        if record.status != ApprovalStatus.SUBMITTED:
            raise ValueError("申請されていないため承認できません")
        
        record.status = ApprovalStatus.APPROVED
        record.approver_id = approver_id
        record.approved_at = datetime.now()
        record.approval_comment = comment
        record.updated_at = datetime.now()
        
        self.table.put_item(Item=record.to_dict())
        
        return record

    def reject(
        self,
        record_id: str,
        approver_id: str,
        comment: Optional[str] = None,
    ) -> Optional[MonthlyRecord]:
        """
        差し戻し
        
        Args:
            record_id: レコードID
            approver_id: 承認者ID
            comment: コメント
            
        Returns:
            更新された月次記録またはNone
        """
        record = self.get_record(record_id)
        if not record:
            return None
        
        if record.status != ApprovalStatus.SUBMITTED:
            raise ValueError("申請されていないため差し戻しできません")
        
        record.status = ApprovalStatus.REJECTED
        record.approver_id = approver_id
        record.approval_comment = comment
        record.updated_at = datetime.now()
        
        self.table.put_item(Item=record.to_dict())
        
        return record

    def revoke_approval(
        self,
        record_id: str,
        approver_id: str,
    ) -> Optional[MonthlyRecord]:
        """
        承認取り消し
        
        Args:
            record_id: レコードID
            approver_id: 承認者ID
            
        Returns:
            更新された月次記録またはNone
        """
        record = self.get_record(record_id)
        if not record:
            return None
        
        if record.status != ApprovalStatus.APPROVED:
            raise ValueError("承認されていないため取り消しできません")
        
        record.status = ApprovalStatus.DRAFT
        record.approver_id = None
        record.approved_at = None
        record.approval_comment = None
        record.updated_at = datetime.now()
        
        self.table.put_item(Item=record.to_dict())
        
        return record

    def get_records_by_user(self, user_id: str) -> list[MonthlyRecord]:
        """
        ユーザーの全月次記録を取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            月次記録リスト
        """
        try:
            response = self.table.query(
                IndexName="user-month-index",
                KeyConditionExpression=Key("user_id").eq(user_id),
            )
            records = [MonthlyRecord.from_dict(item) for item in response.get("Items", [])]
            return sorted(records, key=lambda r: r.year_month, reverse=True)
        except ClientError:
            return []

    def get_pending_approvals(self) -> list[MonthlyRecord]:
        """
        承認待ちの全記録を取得
        
        Returns:
            月次記録リスト
        """
        try:
            response = self.table.scan(
                FilterExpression="status = :status",
                ExpressionAttributeValues={":status": ApprovalStatus.SUBMITTED.value},
            )
            records = [MonthlyRecord.from_dict(item) for item in response.get("Items", [])]
            return sorted(records, key=lambda r: r.year_month)
        except ClientError:
            return []
