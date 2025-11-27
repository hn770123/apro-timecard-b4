"""
日次記録APIエンドポイント
日次記録のCRUD操作を提供
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..schemas.daily_record import DailyRecordCreate, DailyRecordUpdate, DailyRecordResponse
from ..schemas.user import TokenData
from ..services.auth import get_current_user
from ..services.dynamodb import DynamoDBService
from ..services.daily_record import DailyRecordService
from ..services.monthly_record import MonthlyRecordService
from ..services.work_pattern import WorkPatternService
from ..services.work_time_calculator import WorkTimeCalculator


router = APIRouter(prefix="/api/daily-records", tags=["日次記録"])


def get_daily_record_service() -> DailyRecordService:
    """日次記録サービスを取得"""
    db_service = DynamoDBService()
    return DailyRecordService(db_service)


def get_monthly_record_service() -> MonthlyRecordService:
    """月次記録サービスを取得"""
    db_service = DynamoDBService()
    return MonthlyRecordService(db_service)


def get_work_pattern_service() -> WorkPatternService:
    """勤務パターンサービスを取得"""
    db_service = DynamoDBService()
    return WorkPatternService(db_service)


@router.get("/monthly/{monthly_record_id}", response_model=List[DailyRecordResponse], summary="日次記録一覧取得")
async def list_daily_records(
    monthly_record_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    指定した月次記録の日次記録一覧を取得
    """
    monthly_service = get_monthly_record_service()
    daily_service = get_daily_record_service()
    
    # 月次記録の所有権チェック
    monthly = monthly_service.get_record(monthly_record_id)
    if not monthly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="月次記録が見つかりません",
        )
    
    if monthly.user_id != current_user.user_id and "approver" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    records = daily_service.get_records_by_monthly(monthly_record_id)
    
    return [
        DailyRecordResponse(
            record_id=r.record_id,
            user_id=r.user_id,
            monthly_record_id=r.monthly_record_id,
            record_date=r.record_date,
            work_type=r.work_type.value,
            leave_type=r.leave_type.value,
            pattern_number=r.pattern_number,
            start_time=r.start_time,
            end_time=r.end_time,
            late_minutes=r.late_minutes,
            early_leave_minutes=r.early_leave_minutes,
            work_minutes=r.work_minutes,
            overtime_minutes=r.overtime_minutes,
            night_overtime_minutes=r.night_overtime_minutes,
            holiday_work_minutes=r.holiday_work_minutes,
            extra_holiday_work_minutes=r.extra_holiday_work_minutes,
            note=r.note,
            is_note_required=r.is_note_required,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in records
    ]


@router.post("", response_model=DailyRecordResponse, status_code=status.HTTP_201_CREATED, summary="日次記録作成")
async def create_daily_record(
    monthly_record_id: str,
    record_data: DailyRecordCreate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    新規日次記録を作成
    """
    monthly_service = get_monthly_record_service()
    daily_service = get_daily_record_service()
    pattern_service = get_work_pattern_service()
    
    # 月次記録の所有権とロック状態チェック
    monthly = monthly_service.get_record(monthly_record_id)
    if not monthly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="月次記録が見つかりません",
        )
    
    if monthly.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    if not monthly.can_edit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="承認済みのため編集できません",
        )
    
    try:
        record = daily_service.create_record(
            user_id=current_user.user_id,
            monthly_record_id=monthly_record_id,
            record_date=record_data.record_date,
            work_type=record_data.work_type,
            leave_type=record_data.leave_type,
            pattern_number=record_data.pattern_number,
            start_time=record_data.start_time,
            end_time=record_data.end_time,
            note=record_data.note,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    # 時間を自動計算
    pattern = pattern_service.get_pattern_by_user_month_number(
        current_user.user_id,
        monthly.year_month,
        record.pattern_number,
    )
    calculator = WorkTimeCalculator(monthly.standard_work_hours)
    record = daily_service.update_calculated_times(record.record_id, calculator, pattern)
    
    return DailyRecordResponse(
        record_id=record.record_id,
        user_id=record.user_id,
        monthly_record_id=record.monthly_record_id,
        record_date=record.record_date,
        work_type=record.work_type.value,
        leave_type=record.leave_type.value,
        pattern_number=record.pattern_number,
        start_time=record.start_time,
        end_time=record.end_time,
        late_minutes=record.late_minutes,
        early_leave_minutes=record.early_leave_minutes,
        work_minutes=record.work_minutes,
        overtime_minutes=record.overtime_minutes,
        night_overtime_minutes=record.night_overtime_minutes,
        holiday_work_minutes=record.holiday_work_minutes,
        extra_holiday_work_minutes=record.extra_holiday_work_minutes,
        note=record.note,
        is_note_required=record.is_note_required,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("/{record_id}", response_model=DailyRecordResponse, summary="日次記録取得")
async def get_daily_record(
    record_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    指定した日次記録を取得
    """
    daily_service = get_daily_record_service()
    monthly_service = get_monthly_record_service()
    
    record = daily_service.get_record(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日次記録が見つかりません",
        )
    
    # 月次記録の所有権チェック
    monthly = monthly_service.get_record(record.monthly_record_id)
    if monthly and monthly.user_id != current_user.user_id and "approver" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    return DailyRecordResponse(
        record_id=record.record_id,
        user_id=record.user_id,
        monthly_record_id=record.monthly_record_id,
        record_date=record.record_date,
        work_type=record.work_type.value,
        leave_type=record.leave_type.value,
        pattern_number=record.pattern_number,
        start_time=record.start_time,
        end_time=record.end_time,
        late_minutes=record.late_minutes,
        early_leave_minutes=record.early_leave_minutes,
        work_minutes=record.work_minutes,
        overtime_minutes=record.overtime_minutes,
        night_overtime_minutes=record.night_overtime_minutes,
        holiday_work_minutes=record.holiday_work_minutes,
        extra_holiday_work_minutes=record.extra_holiday_work_minutes,
        note=record.note,
        is_note_required=record.is_note_required,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.put("/{record_id}", response_model=DailyRecordResponse, summary="日次記録更新")
async def update_daily_record(
    record_id: str,
    record_data: DailyRecordUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    日次記録を更新
    """
    daily_service = get_daily_record_service()
    monthly_service = get_monthly_record_service()
    pattern_service = get_work_pattern_service()
    
    # レコードの存在確認
    existing = daily_service.get_record(record_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日次記録が見つかりません",
        )
    
    # 月次記録の所有権とロック状態チェック
    monthly = monthly_service.get_record(existing.monthly_record_id)
    if not monthly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="月次記録が見つかりません",
        )
    
    if monthly.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    if not monthly.can_edit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="承認済みのため編集できません",
        )
    
    record = daily_service.update_record(
        record_id=record_id,
        work_type=record_data.work_type,
        leave_type=record_data.leave_type,
        pattern_number=record_data.pattern_number,
        start_time=record_data.start_time,
        end_time=record_data.end_time,
        late_minutes=record_data.late_minutes,
        early_leave_minutes=record_data.early_leave_minutes,
        overtime_minutes=record_data.overtime_minutes,
        note=record_data.note,
    )
    
    # 時間を再計算（手動入力がない場合）
    pattern_number = record_data.pattern_number if record_data.pattern_number else existing.pattern_number
    pattern = pattern_service.get_pattern_by_user_month_number(
        current_user.user_id,
        monthly.year_month,
        pattern_number,
    )
    calculator = WorkTimeCalculator(monthly.standard_work_hours)
    record = daily_service.update_calculated_times(record.record_id, calculator, pattern)
    
    return DailyRecordResponse(
        record_id=record.record_id,
        user_id=record.user_id,
        monthly_record_id=record.monthly_record_id,
        record_date=record.record_date,
        work_type=record.work_type.value,
        leave_type=record.leave_type.value,
        pattern_number=record.pattern_number,
        start_time=record.start_time,
        end_time=record.end_time,
        late_minutes=record.late_minutes,
        early_leave_minutes=record.early_leave_minutes,
        work_minutes=record.work_minutes,
        overtime_minutes=record.overtime_minutes,
        night_overtime_minutes=record.night_overtime_minutes,
        holiday_work_minutes=record.holiday_work_minutes,
        extra_holiday_work_minutes=record.extra_holiday_work_minutes,
        note=record.note,
        is_note_required=record.is_note_required,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="日次記録削除")
async def delete_daily_record(
    record_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    日次記録を削除
    """
    daily_service = get_daily_record_service()
    monthly_service = get_monthly_record_service()
    
    # レコードの存在確認
    existing = daily_service.get_record(record_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日次記録が見つかりません",
        )
    
    # 月次記録の所有権とロック状態チェック
    monthly = monthly_service.get_record(existing.monthly_record_id)
    if not monthly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="月次記録が見つかりません",
        )
    
    if monthly.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    if not monthly.can_edit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="承認済みのため編集できません",
        )
    
    daily_service.delete_record(record_id)
