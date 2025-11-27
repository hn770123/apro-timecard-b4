"""
ユーザーサービス
ユーザー管理のビジネスロジック
"""
import uuid
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from ..config import get_settings
from ..models.user import User
from ..services.dynamodb import DynamoDBService
from ..services.auth import AuthService


class UserService:
    """
    ユーザーサービスクラス
    ユーザーのCRUD操作とログイン認証を提供
    """
    
    def __init__(self, db_service: DynamoDBService, auth_service: AuthService):
        """
        サービスを初期化
        
        Args:
            db_service: DynamoDBサービス
            auth_service: 認証サービス
        """
        self.db_service = db_service
        self.auth_service = auth_service
        self.settings = get_settings()
        self.table = db_service.get_table(self.settings.users_table)

    def create_user(
        self,
        email: str,
        password: str,
        name: str,
        department: str,
        is_approver: bool = False,
        is_admin: bool = False,
    ) -> User:
        """
        ユーザーを作成
        
        Args:
            email: メールアドレス
            password: パスワード（平文）
            name: 氏名
            department: 所属
            is_approver: 承認者権限
            is_admin: 管理者権限
            
        Returns:
            作成されたユーザー
            
        Raises:
            ValueError: メールアドレスが既に存在する場合
        """
        # メールアドレスの重複チェック
        if self.get_user_by_email(email):
            raise ValueError("このメールアドレスは既に登録されています")
        
        # ユーザー作成
        user = User(
            user_id=str(uuid.uuid4()),
            email=email,
            password_hash=self.auth_service.get_password_hash(password),
            name=name,
            department=department,
            is_approver=is_approver,
            is_admin=is_admin,
        )
        
        # DynamoDBに保存
        self.table.put_item(Item=user.to_dict())
        
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """
        ユーザーをIDで取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            ユーザーまたはNone
        """
        try:
            response = self.table.get_item(Key={"user_id": user_id})
            if "Item" in response:
                return User.from_dict(response["Item"])
            return None
        except ClientError:
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        ユーザーをメールアドレスで取得
        
        Args:
            email: メールアドレス
            
        Returns:
            ユーザーまたはNone
        """
        try:
            response = self.table.query(
                IndexName="email-index",
                KeyConditionExpression=Key("email").eq(email),
            )
            if response["Items"]:
                return User.from_dict(response["Items"][0])
            return None
        except ClientError:
            return None

    def update_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        department: Optional[str] = None,
        is_approver: Optional[bool] = None,
        is_admin: Optional[bool] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[User]:
        """
        ユーザーを更新
        
        Args:
            user_id: ユーザーID
            その他: 更新するフィールド
            
        Returns:
            更新されたユーザーまたはNone
        """
        user = self.get_user(user_id)
        if not user:
            return None
        
        # フィールドを更新
        if email is not None:
            # メールアドレス重複チェック
            existing = self.get_user_by_email(email)
            if existing and existing.user_id != user_id:
                raise ValueError("このメールアドレスは既に登録されています")
            user.email = email
        if name is not None:
            user.name = name
        if department is not None:
            user.department = department
        if is_approver is not None:
            user.is_approver = is_approver
        if is_admin is not None:
            user.is_admin = is_admin
        if is_active is not None:
            user.is_active = is_active
        
        user.updated_at = datetime.now()
        
        # DynamoDBに保存
        self.table.put_item(Item=user.to_dict())
        
        return user

    def delete_user(self, user_id: str) -> bool:
        """
        ユーザーを削除（物理削除）
        
        Args:
            user_id: ユーザーID
            
        Returns:
            削除成功したかどうか
        """
        try:
            self.table.delete_item(Key={"user_id": user_id})
            return True
        except ClientError:
            return False

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        ユーザーを認証
        
        Args:
            email: メールアドレス
            password: パスワード
            
        Returns:
            認証成功時はユーザー、失敗時はNone
        """
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not user.is_active:
            return None
        if not self.auth_service.verify_password(password, user.password_hash):
            return None
        return user

    def list_users(self) -> list[User]:
        """
        全ユーザーを取得
        
        Returns:
            ユーザーリスト
        """
        try:
            response = self.table.scan()
            return [User.from_dict(item) for item in response.get("Items", [])]
        except ClientError:
            return []
