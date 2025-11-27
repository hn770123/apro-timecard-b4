"""
ユーザースキーマ
APIリクエスト/レスポンス用のPydanticモデル
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """
    ユーザー作成リクエストスキーマ
    """
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, description="パスワード（8文字以上）")
    name: str = Field(..., min_length=1, description="氏名")
    department: str = Field(..., min_length=1, description="所属")
    is_approver: bool = Field(default=False, description="承認者権限")
    is_admin: bool = Field(default=False, description="管理者権限")


class UserUpdate(BaseModel):
    """
    ユーザー更新リクエストスキーマ
    """
    email: Optional[EmailStr] = Field(None, description="メールアドレス")
    name: Optional[str] = Field(None, min_length=1, description="氏名")
    department: Optional[str] = Field(None, min_length=1, description="所属")
    is_approver: Optional[bool] = Field(None, description="承認者権限")
    is_admin: Optional[bool] = Field(None, description="管理者権限")
    is_active: Optional[bool] = Field(None, description="アカウント有効フラグ")


class UserResponse(BaseModel):
    """
    ユーザーレスポンススキーマ
    パスワードハッシュは含まない
    """
    user_id: str = Field(..., description="ユーザーID")
    email: str = Field(..., description="メールアドレス")
    name: str = Field(..., description="氏名")
    department: str = Field(..., description="所属")
    is_approver: bool = Field(..., description="承認者権限")
    is_admin: bool = Field(..., description="管理者権限")
    is_active: bool = Field(..., description="アカウント有効フラグ")
    roles: list[str] = Field(..., description="権限リスト")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """
    ログインリクエストスキーマ
    """
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., description="パスワード")


class Token(BaseModel):
    """
    トークンレスポンススキーマ
    """
    access_token: str = Field(..., description="アクセストークン")
    token_type: str = Field(default="bearer", description="トークンタイプ")


class TokenData(BaseModel):
    """
    トークンデータスキーマ（内部使用）
    """
    user_id: Optional[str] = None
    email: Optional[str] = None
    roles: list[str] = Field(default_factory=list)
