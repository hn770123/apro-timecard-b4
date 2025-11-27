"""
認証サービス
JWT認証とパスワードハッシュ化を提供
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from ..config import get_settings
from ..schemas.user import TokenData


# パスワードハッシュ化コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2スキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class AuthService:
    """
    認証サービスクラス
    JWT生成/検証とパスワードハッシュ化を提供
    """
    
    def __init__(self):
        """設定を読み込み"""
        self.settings = get_settings()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        パスワードを検証
        
        Args:
            plain_password: 平文パスワード
            hashed_password: ハッシュ化されたパスワード
            
        Returns:
            検証結果
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        パスワードをハッシュ化
        
        Args:
            password: 平文パスワード
            
        Returns:
            ハッシュ化されたパスワード
        """
        return pwd_context.hash(password)

    def create_access_token(
        self,
        user_id: str,
        email: str,
        roles: list[str],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        アクセストークンを生成
        
        Args:
            user_id: ユーザーID
            email: メールアドレス
            roles: 権限リスト
            expires_delta: 有効期限（オプション）
            
        Returns:
            JWTトークン
        """
        to_encode = {
            "sub": user_id,
            "email": email,
            "roles": roles,
        }
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.settings.access_token_expire_minutes
            )
        
        to_encode["exp"] = expire
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm=self.settings.algorithm,
        )
        
        return encoded_jwt

    def decode_token(self, token: str) -> TokenData:
        """
        トークンをデコード
        
        Args:
            token: JWTトークン
            
        Returns:
            トークンデータ
            
        Raises:
            HTTPException: トークンが無効な場合
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証情報が無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm],
            )
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            roles: list = payload.get("roles", [])
            
            if user_id is None:
                raise credentials_exception
            
            return TokenData(user_id=user_id, email=email, roles=roles)
            
        except JWTError:
            raise credentials_exception


# 認証サービスのシングルトンインスタンス
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """認証サービスインスタンスを取得"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    現在のユーザーを取得（依存関係注入用）
    
    Args:
        token: JWTトークン（自動取得）
        
    Returns:
        トークンデータ
    """
    auth_service = get_auth_service()
    return auth_service.decode_token(token)


async def require_approver(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    承認者権限を要求（依存関係注入用）
    """
    if "approver" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="承認者権限が必要です",
        )
    return current_user


async def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    管理者権限を要求（依存関係注入用）
    """
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です",
        )
    return current_user
