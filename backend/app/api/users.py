"""
ユーザー管理APIエンドポイント
ユーザーのCRUD操作を提供（管理者権限必要）
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..schemas.user import UserCreate, UserUpdate, UserResponse, TokenData
from ..services.auth import get_auth_service, get_current_user, require_admin
from ..services.dynamodb import DynamoDBService
from ..services.user import UserService


router = APIRouter(prefix="/api/users", tags=["ユーザー管理"])


def get_user_service() -> UserService:
    """ユーザーサービスを取得"""
    db_service = DynamoDBService()
    auth_service = get_auth_service()
    return UserService(db_service, auth_service)


@router.get("", response_model=List[UserResponse], summary="ユーザー一覧取得")
async def list_users(
    current_user: TokenData = Depends(require_admin),
):
    """
    全ユーザーを取得（管理者権限必要）
    """
    user_service = get_user_service()
    users = user_service.list_users()
    
    return [
        UserResponse(
            user_id=u.user_id,
            email=u.email,
            name=u.name,
            department=u.department,
            is_approver=u.is_approver,
            is_admin=u.is_admin,
            is_active=u.is_active,
            roles=u.get_roles(),
            created_at=u.created_at,
            updated_at=u.updated_at,
        )
        for u in users
    ]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="ユーザー作成")
async def create_user(
    user_data: UserCreate,
    current_user: TokenData = Depends(require_admin),
):
    """
    新規ユーザーを作成（管理者権限必要）
    """
    user_service = get_user_service()
    
    try:
        user = user_service.create_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            department=user_data.department,
            is_approver=user_data.is_approver,
            is_admin=user_data.is_admin,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        department=user.department,
        is_approver=user.is_approver,
        is_admin=user.is_admin,
        is_active=user.is_active,
        roles=user.get_roles(),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/{user_id}", response_model=UserResponse, summary="ユーザー取得")
async def get_user(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """
    指定したユーザーを取得
    自分自身または管理者のみアクセス可能
    """
    # 自分自身か管理者のみ
    if current_user.user_id != user_id and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセス権限がありません",
        )
    
    user_service = get_user_service()
    user = user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        department=user.department,
        is_approver=user.is_approver,
        is_admin=user.is_admin,
        is_active=user.is_active,
        roles=user.get_roles(),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/{user_id}", response_model=UserResponse, summary="ユーザー更新")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: TokenData = Depends(require_admin),
):
    """
    ユーザー情報を更新（管理者権限必要）
    """
    user_service = get_user_service()
    
    try:
        user = user_service.update_user(
            user_id=user_id,
            email=user_data.email,
            name=user_data.name,
            department=user_data.department,
            is_approver=user_data.is_approver,
            is_admin=user_data.is_admin,
            is_active=user_data.is_active,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        department=user.department,
        is_approver=user.is_approver,
        is_admin=user.is_admin,
        is_active=user.is_active,
        roles=user.get_roles(),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="ユーザー削除")
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(require_admin),
):
    """
    ユーザーを削除（管理者権限必要）
    """
    # 自分自身は削除不可
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="自分自身は削除できません",
        )
    
    user_service = get_user_service()
    success = user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
