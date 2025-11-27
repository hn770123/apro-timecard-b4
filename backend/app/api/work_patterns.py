"""
勤務パターンAPIエンドポイント
勤務パターンのCRUD操作を提供
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..schemas.work_pattern import WorkPatternCreate, WorkPatternUpdate, WorkPatternResponse, BreakTimeSchema
from ..schemas.user import TokenData
from ..services.auth import get_current_user
from ..services.dynamodb import DynamoDBService
from ..services.work_pattern import WorkPatternService


router = APIRouter(prefix="/api/work-patterns", tags=["勤務パターン"])


def get_work_pattern_service() -> WorkPatternService:
    """勤務パターンサービスを取得"""
    db_service = DynamoDBService()
    return WorkPatternService(db_service)


@router.get("", response_model=List[WorkPatternResponse], summary="勤務パターン一覧取得")
async def list_work_patterns(
    year_month: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    指定した月の勤務パターンを取得
    """
    service = get_work_pattern_service()
    patterns = service.get_patterns_by_user_month(current_user.user_id, year_month)
    
    return [
        WorkPatternResponse(
            pattern_id=p.pattern_id,
            user_id=p.user_id,
            pattern_number=p.pattern_number,
            start_time=p.start_time,
            end_time=p.end_time,
            break_times=[
                BreakTimeSchema(start_time=bt.start_time, end_time=bt.end_time)
                for bt in p.break_times
            ],
            year_month=p.year_month,
            scheduled_work_minutes=p.get_scheduled_work_minutes(),
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in patterns
    ]


@router.post("", response_model=WorkPatternResponse, status_code=status.HTTP_201_CREATED, summary="勤務パターン作成")
async def create_work_pattern(
    pattern_data: WorkPatternCreate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    新規勤務パターンを作成
    既に同じパターン番号が存在する場合は更新
    """
    service = get_work_pattern_service()
    
    pattern = service.create_pattern(
        user_id=current_user.user_id,
        pattern_number=pattern_data.pattern_number,
        start_time=pattern_data.start_time,
        end_time=pattern_data.end_time,
        break_times=[bt.model_dump() for bt in pattern_data.break_times],
        year_month=pattern_data.year_month,
    )
    
    return WorkPatternResponse(
        pattern_id=pattern.pattern_id,
        user_id=pattern.user_id,
        pattern_number=pattern.pattern_number,
        start_time=pattern.start_time,
        end_time=pattern.end_time,
        break_times=[
            BreakTimeSchema(start_time=bt.start_time, end_time=bt.end_time)
            for bt in pattern.break_times
        ],
        year_month=pattern.year_month,
        scheduled_work_minutes=pattern.get_scheduled_work_minutes(),
        created_at=pattern.created_at,
        updated_at=pattern.updated_at,
    )


@router.get("/{pattern_id}", response_model=WorkPatternResponse, summary="勤務パターン取得")
async def get_work_pattern(
    pattern_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    指定した勤務パターンを取得
    """
    service = get_work_pattern_service()
    pattern = service.get_pattern(pattern_id)
    
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="勤務パターンが見つかりません",
        )
    
    # 自分のパターンのみアクセス可能
    if pattern.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    return WorkPatternResponse(
        pattern_id=pattern.pattern_id,
        user_id=pattern.user_id,
        pattern_number=pattern.pattern_number,
        start_time=pattern.start_time,
        end_time=pattern.end_time,
        break_times=[
            BreakTimeSchema(start_time=bt.start_time, end_time=bt.end_time)
            for bt in pattern.break_times
        ],
        year_month=pattern.year_month,
        scheduled_work_minutes=pattern.get_scheduled_work_minutes(),
        created_at=pattern.created_at,
        updated_at=pattern.updated_at,
    )


@router.put("/{pattern_id}", response_model=WorkPatternResponse, summary="勤務パターン更新")
async def update_work_pattern(
    pattern_id: str,
    pattern_data: WorkPatternUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    """
    勤務パターンを更新
    """
    service = get_work_pattern_service()
    
    # 所有権チェック
    existing = service.get_pattern(pattern_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="勤務パターンが見つかりません",
        )
    
    if existing.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    break_times = None
    if pattern_data.break_times is not None:
        break_times = [bt.model_dump() for bt in pattern_data.break_times]
    
    pattern = service.update_pattern(
        pattern_id=pattern_id,
        start_time=pattern_data.start_time,
        end_time=pattern_data.end_time,
        break_times=break_times,
    )
    
    return WorkPatternResponse(
        pattern_id=pattern.pattern_id,
        user_id=pattern.user_id,
        pattern_number=pattern.pattern_number,
        start_time=pattern.start_time,
        end_time=pattern.end_time,
        break_times=[
            BreakTimeSchema(start_time=bt.start_time, end_time=bt.end_time)
            for bt in pattern.break_times
        ],
        year_month=pattern.year_month,
        scheduled_work_minutes=pattern.get_scheduled_work_minutes(),
        created_at=pattern.created_at,
        updated_at=pattern.updated_at,
    )


@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT, summary="勤務パターン削除")
async def delete_work_pattern(
    pattern_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    勤務パターンを削除
    """
    service = get_work_pattern_service()
    
    # 所有権チェック
    existing = service.get_pattern(pattern_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="勤務パターンが見つかりません",
        )
    
    if existing.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    service.delete_pattern(pattern_id)


@router.post("/copy-from-previous", response_model=List[WorkPatternResponse], summary="前月パターンをコピー")
async def copy_patterns_from_previous_month(
    target_year_month: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    前月の勤務パターンを当月にコピー
    """
    service = get_work_pattern_service()
    patterns = service.copy_patterns_from_previous_month(
        user_id=current_user.user_id,
        target_year_month=target_year_month,
    )
    
    return [
        WorkPatternResponse(
            pattern_id=p.pattern_id,
            user_id=p.user_id,
            pattern_number=p.pattern_number,
            start_time=p.start_time,
            end_time=p.end_time,
            break_times=[
                BreakTimeSchema(start_time=bt.start_time, end_time=bt.end_time)
                for bt in p.break_times
            ],
            year_month=p.year_month,
            scheduled_work_minutes=p.get_scheduled_work_minutes(),
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in patterns
    ]
