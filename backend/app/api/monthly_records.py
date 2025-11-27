"""
月次記録APIエンドポイント
月次記録のCRUD操作と承認ワークフローを提供
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..schemas.monthly_record import (
    MonthlyRecordCreate,
    MonthlyRecordUpdate,
    MonthlyRecordResponse,
    ApprovalRequest,
)
from ..schemas.user import TokenData
from ..services.auth import get_current_user, require_approver
from ..services.dynamodb import DynamoDBService
from ..services.monthly_record import MonthlyRecordService
from ..services.daily_record import DailyRecordService


router = APIRouter(prefix="/api/monthly-records", tags=["月次記録"])


def get_monthly_record_service() -> MonthlyRecordService:
    """月次記録サービスを取得"""
    db_service = DynamoDBService()
    return MonthlyRecordService(db_service)


def get_daily_record_service() -> DailyRecordService:
    """日次記録サービスを取得"""
    db_service = DynamoDBService()
    return DailyRecordService(db_service)


@router.get("", response_model=List[MonthlyRecordResponse], summary="月次記録一覧取得")
async def list_monthly_records(
    current_user: TokenData = Depends(get_current_user),
):
    """
    自分の月次記録一覧を取得
    """
    service = get_monthly_record_service()
    records = service.get_records_by_user(current_user.user_id)
    
    return [
        MonthlyRecordResponse(
            record_id=r.record_id,
            user_id=r.user_id,
            year_month=r.year_month,
            name=r.name,
            department=r.department,
            standard_work_hours=r.standard_work_hours,
            status=r.status.value,
            approver_id=r.approver_id,
            approved_at=r.approved_at,
            approval_comment=r.approval_comment,
            total_work_days=r.total_work_days,
            total_work_minutes=r.total_work_minutes,
            total_overtime_minutes=r.total_overtime_minutes,
            total_night_overtime_minutes=r.total_night_overtime_minutes,
            total_holiday_work_minutes=r.total_holiday_work_minutes,
            total_extra_holiday_work_minutes=r.total_extra_holiday_work_minutes,
            total_late_minutes=r.total_late_minutes,
            total_early_leave_minutes=r.total_early_leave_minutes,
            total_paid_leave_days=r.total_paid_leave_days,
            total_absence_days=r.total_absence_days,
            total_special_leave_days=r.total_special_leave_days,
            total_condolence_leave_days=r.total_condolence_leave_days,
            is_locked=r.is_locked(),
            can_edit=r.can_edit(),
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in records
    ]


@router.post("", response_model=MonthlyRecordResponse, status_code=status.HTTP_201_CREATED, summary="月次記録作成")
async def create_monthly_record(
    record_data: MonthlyRecordCreate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    新規月次記録を作成
    """
    service = get_monthly_record_service()
    
    try:
        record = service.create_record(
            user_id=current_user.user_id,
            year_month=record_data.year_month,
            name=record_data.name,
            department=record_data.department,
            standard_work_hours=record_data.standard_work_hours,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return MonthlyRecordResponse(
        record_id=record.record_id,
        user_id=record.user_id,
        year_month=record.year_month,
        name=record.name,
        department=record.department,
        standard_work_hours=record.standard_work_hours,
        status=record.status.value,
        approver_id=record.approver_id,
        approved_at=record.approved_at,
        approval_comment=record.approval_comment,
        total_work_days=record.total_work_days,
        total_work_minutes=record.total_work_minutes,
        total_overtime_minutes=record.total_overtime_minutes,
        total_night_overtime_minutes=record.total_night_overtime_minutes,
        total_holiday_work_minutes=record.total_holiday_work_minutes,
        total_extra_holiday_work_minutes=record.total_extra_holiday_work_minutes,
        total_late_minutes=record.total_late_minutes,
        total_early_leave_minutes=record.total_early_leave_minutes,
        total_paid_leave_days=record.total_paid_leave_days,
        total_absence_days=record.total_absence_days,
        total_special_leave_days=record.total_special_leave_days,
        total_condolence_leave_days=record.total_condolence_leave_days,
        is_locked=record.is_locked(),
        can_edit=record.can_edit(),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("/pending", response_model=List[MonthlyRecordResponse], summary="承認待ち一覧取得")
async def list_pending_approvals(
    current_user: TokenData = Depends(require_approver),
):
    """
    承認待ちの月次記録一覧を取得（承認者権限必要）
    """
    service = get_monthly_record_service()
    records = service.get_pending_approvals()
    
    return [
        MonthlyRecordResponse(
            record_id=r.record_id,
            user_id=r.user_id,
            year_month=r.year_month,
            name=r.name,
            department=r.department,
            standard_work_hours=r.standard_work_hours,
            status=r.status.value,
            approver_id=r.approver_id,
            approved_at=r.approved_at,
            approval_comment=r.approval_comment,
            total_work_days=r.total_work_days,
            total_work_minutes=r.total_work_minutes,
            total_overtime_minutes=r.total_overtime_minutes,
            total_night_overtime_minutes=r.total_night_overtime_minutes,
            total_holiday_work_minutes=r.total_holiday_work_minutes,
            total_extra_holiday_work_minutes=r.total_extra_holiday_work_minutes,
            total_late_minutes=r.total_late_minutes,
            total_early_leave_minutes=r.total_early_leave_minutes,
            total_paid_leave_days=r.total_paid_leave_days,
            total_absence_days=r.total_absence_days,
            total_special_leave_days=r.total_special_leave_days,
            total_condolence_leave_days=r.total_condolence_leave_days,
            is_locked=r.is_locked(),
            can_edit=r.can_edit(),
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in records
    ]


@router.get("/{record_id}", response_model=MonthlyRecordResponse, summary="月次記録取得")
async def get_monthly_record(
    record_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    指定した月次記録を取得
    """
    service = get_monthly_record_service()
    record = service.get_record(record_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="月次記録が見つかりません",
        )
    
    # 自分のレコードか承認者のみアクセス可能
    if record.user_id != current_user.user_id and "approver" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    return MonthlyRecordResponse(
        record_id=record.record_id,
        user_id=record.user_id,
        year_month=record.year_month,
        name=record.name,
        department=record.department,
        standard_work_hours=record.standard_work_hours,
        status=record.status.value,
        approver_id=record.approver_id,
        approved_at=record.approved_at,
        approval_comment=record.approval_comment,
        total_work_days=record.total_work_days,
        total_work_minutes=record.total_work_minutes,
        total_overtime_minutes=record.total_overtime_minutes,
        total_night_overtime_minutes=record.total_night_overtime_minutes,
        total_holiday_work_minutes=record.total_holiday_work_minutes,
        total_extra_holiday_work_minutes=record.total_extra_holiday_work_minutes,
        total_late_minutes=record.total_late_minutes,
        total_early_leave_minutes=record.total_early_leave_minutes,
        total_paid_leave_days=record.total_paid_leave_days,
        total_absence_days=record.total_absence_days,
        total_special_leave_days=record.total_special_leave_days,
        total_condolence_leave_days=record.total_condolence_leave_days,
        is_locked=record.is_locked(),
        can_edit=record.can_edit(),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.put("/{record_id}", response_model=MonthlyRecordResponse, summary="月次記録更新")
async def update_monthly_record(
    record_id: str,
    record_data: MonthlyRecordUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    月次記録を更新
    """
    service = get_monthly_record_service()
    
    # 所有権チェック
    existing = service.get_record(record_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="月次記録が見つかりません",
        )
    
    if existing.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    try:
        record = service.update_record(
            record_id=record_id,
            name=record_data.name,
            department=record_data.department,
            standard_work_hours=record_data.standard_work_hours,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return MonthlyRecordResponse(
        record_id=record.record_id,
        user_id=record.user_id,
        year_month=record.year_month,
        name=record.name,
        department=record.department,
        standard_work_hours=record.standard_work_hours,
        status=record.status.value,
        approver_id=record.approver_id,
        approved_at=record.approved_at,
        approval_comment=record.approval_comment,
        total_work_days=record.total_work_days,
        total_work_minutes=record.total_work_minutes,
        total_overtime_minutes=record.total_overtime_minutes,
        total_night_overtime_minutes=record.total_night_overtime_minutes,
        total_holiday_work_minutes=record.total_holiday_work_minutes,
        total_extra_holiday_work_minutes=record.total_extra_holiday_work_minutes,
        total_late_minutes=record.total_late_minutes,
        total_early_leave_minutes=record.total_early_leave_minutes,
        total_paid_leave_days=record.total_paid_leave_days,
        total_absence_days=record.total_absence_days,
        total_special_leave_days=record.total_special_leave_days,
        total_condolence_leave_days=record.total_condolence_leave_days,
        is_locked=record.is_locked(),
        can_edit=record.can_edit(),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.post("/{record_id}/approval", response_model=MonthlyRecordResponse, summary="承認アクション")
async def approval_action(
    record_id: str,
    request: ApprovalRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """
    承認関連のアクションを実行
    
    - **submit**: 承認申請（本人のみ）
    - **approve**: 承認（承認者のみ）
    - **reject**: 差し戻し（承認者のみ）
    - **revoke**: 承認取り消し（承認者のみ）
    """
    service = get_monthly_record_service()
    daily_service = get_daily_record_service()
    
    existing = service.get_record(record_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="月次記録が見つかりません",
        )
    
    try:
        if request.action == "submit":
            # 本人のみ
            if existing.user_id != current_user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="自分の月報のみ申請できます",
                )
            
            # 集計を更新
            daily_records = daily_service.get_records_by_monthly(record_id)
            service.update_totals(record_id, daily_records)
            
            record = service.submit_for_approval(record_id)
            
        elif request.action == "approve":
            # 承認者のみ
            if "approver" not in current_user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="承認者権限が必要です",
                )
            record = service.approve(record_id, current_user.user_id, request.comment)
            
        elif request.action == "reject":
            # 承認者のみ
            if "approver" not in current_user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="承認者権限が必要です",
                )
            record = service.reject(record_id, current_user.user_id, request.comment)
            
        elif request.action == "revoke":
            # 承認者のみ
            if "approver" not in current_user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="承認者権限が必要です",
                )
            record = service.revoke_approval(record_id, current_user.user_id)
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不正なアクションです",
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return MonthlyRecordResponse(
        record_id=record.record_id,
        user_id=record.user_id,
        year_month=record.year_month,
        name=record.name,
        department=record.department,
        standard_work_hours=record.standard_work_hours,
        status=record.status.value,
        approver_id=record.approver_id,
        approved_at=record.approved_at,
        approval_comment=record.approval_comment,
        total_work_days=record.total_work_days,
        total_work_minutes=record.total_work_minutes,
        total_overtime_minutes=record.total_overtime_minutes,
        total_night_overtime_minutes=record.total_night_overtime_minutes,
        total_holiday_work_minutes=record.total_holiday_work_minutes,
        total_extra_holiday_work_minutes=record.total_extra_holiday_work_minutes,
        total_late_minutes=record.total_late_minutes,
        total_early_leave_minutes=record.total_early_leave_minutes,
        total_paid_leave_days=record.total_paid_leave_days,
        total_absence_days=record.total_absence_days,
        total_special_leave_days=record.total_special_leave_days,
        total_condolence_leave_days=record.total_condolence_leave_days,
        is_locked=record.is_locked(),
        can_edit=record.can_edit(),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )
