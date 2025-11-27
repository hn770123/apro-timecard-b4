"""
勤務月報システム メインアプリケーション
FastAPI + AWS Lambda 対応

技術スタック:
- フロントエンド: Vue.js
- バックエンド実行環境: AWS Lambda
- バックエンド言語/フレームワーク: Python (FastAPI)
- データベース: Amazon DynamoDB
- インフラ管理: AWS / Serverless Framework
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from .config import get_settings
from .api import (
    auth_router,
    users_router,
    work_patterns_router,
    monthly_records_router,
    daily_records_router,
)


# 設定を取得
settings = get_settings()

# FastAPIアプリケーションを作成
app = FastAPI(
    title=settings.app_name,
    description="月間勤務時間の入力/チェック/集計/エクスポート機能を提供するWebアプリケーション",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを登録
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(work_patterns_router)
app.include_router(monthly_records_router)
app.include_router(daily_records_router)


@app.get("/api/health", tags=["ヘルスチェック"])
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "healthy", "app_name": settings.app_name}


# AWS Lambda ハンドラー
handler = Mangum(app, lifespan="off")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
