"""
認証サービスのテスト
"""
import pytest
from backend.app.services.auth import AuthService


class TestAuthService:
    """認証サービスのテストクラス"""

    def test_password_hash_and_verify(self):
        """パスワードハッシュと検証のテスト"""
        auth_service = AuthService()
        
        password = "testpassword123"
        hashed = auth_service.get_password_hash(password)
        
        # ハッシュが元のパスワードと異なることを確認
        assert hashed != password
        
        # 正しいパスワードで検証成功
        assert auth_service.verify_password(password, hashed) is True
        
        # 間違ったパスワードで検証失敗
        assert auth_service.verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """アクセストークン生成のテスト"""
        auth_service = AuthService()
        
        token = auth_service.create_access_token(
            user_id="test-user-id",
            email="test@example.com",
            roles=["general", "approver"],
        )
        
        # トークンが文字列であることを確認
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token(self):
        """トークンデコードのテスト"""
        auth_service = AuthService()
        
        # トークンを生成
        token = auth_service.create_access_token(
            user_id="test-user-id",
            email="test@example.com",
            roles=["general", "approver"],
        )
        
        # トークンをデコード
        token_data = auth_service.decode_token(token)
        
        assert token_data.user_id == "test-user-id"
        assert token_data.email == "test@example.com"
        assert "general" in token_data.roles
        assert "approver" in token_data.roles

    def test_decode_invalid_token(self):
        """無効なトークンのデコードテスト"""
        auth_service = AuthService()
        
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.decode_token("invalid-token")
        
        assert exc_info.value.status_code == 401
