"""
認証APIエンドポイント
ログイン機能を提供
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..schemas.user import UserLogin, Token, UserResponse
from ..services.auth import AuthService, get_auth_service, get_current_user, TokenData
from ..services.dynamodb import DynamoDBService
from ..services.user import UserService


router = APIRouter(prefix="/api/auth", tags=["認証"])


def get_user_service() -> UserService:
    """ユーザーサービスを取得"""
    db_service = DynamoDBService()
    auth_service = get_auth_service()
    return UserService(db_service, auth_service)


@router.post("/login", response_model=Token, summary="ログイン")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    メールアドレスとパスワードでログイン
    
    - **username**: メールアドレス
    - **password**: パスワード
    
    成功時はJWTトークンを返す
    """
    user_service = get_user_service()
    
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = get_auth_service()
    access_token = auth_service.create_access_token(
        user_id=user.user_id,
        email=user.email,
        roles=user.get_roles(),
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse, summary="現在のユーザー情報")
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
):
    """
    現在ログイン中のユーザー情報を取得
    """
    user_service = get_user_service()
    
    user = user_service.get_user(current_user.user_id)
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
