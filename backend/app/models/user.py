"""
ユーザーモデル
ユーザー情報と権限を定義
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class UserRole(str, Enum):
    """
    ユーザー権限の列挙型
    一般: 入力者（自身のデータのみ入力可能）
    承認者: 他ユーザーの月報を承認可能
    管理者: ユーザーの追加/変更が可能
    """
    GENERAL = "general"  # 一般（入力者）
    APPROVER = "approver"  # 承認者
    ADMIN = "admin"  # システム管理者


@dataclass
class User:
    """
    ユーザーモデル
    ログイン情報と権限を管理
    
    承認者と管理者は個別に設定可能
    （承認だけ、管理だけ、両方可）
    """
    user_id: str  # ユーザーID（主キー）
    email: str  # メールアドレス（ログイン用）
    password_hash: str  # パスワードハッシュ
    name: str  # 氏名
    department: str  # 所属
    is_approver: bool = False  # 承認者権限
    is_admin: bool = False  # 管理者権限
    is_active: bool = True  # アカウント有効フラグ
    created_at: datetime = field(default_factory=datetime.now)  # 作成日時
    updated_at: datetime = field(default_factory=datetime.now)  # 更新日時

    def get_roles(self) -> list[str]:
        """
        ユーザーの権限リストを取得
        """
        roles = [UserRole.GENERAL.value]
        if self.is_approver:
            roles.append(UserRole.APPROVER.value)
        if self.is_admin:
            roles.append(UserRole.ADMIN.value)
        return roles

    def to_dict(self) -> dict:
        """
        辞書形式に変換（DynamoDB保存用）
        """
        return {
            "user_id": self.user_id,
            "email": self.email,
            "password_hash": self.password_hash,
            "name": self.name,
            "department": self.department,
            "is_approver": self.is_approver,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """
        辞書からインスタンスを生成
        """
        return cls(
            user_id=data["user_id"],
            email=data["email"],
            password_hash=data["password_hash"],
            name=data["name"],
            department=data["department"],
            is_approver=data.get("is_approver", False),
            is_admin=data.get("is_admin", False),
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
