# 勤務月報システム

月間勤務時間の入力/チェック/集計/エクスポート機能を提供するWebアプリケーション

## 技術スタック

- **フロントエンド**: Vue.js 3
- **バックエンド実行環境**: AWS Lambda
- **バックエンド言語/フレームワーク**: Python (FastAPI)
- **データベース**: Amazon DynamoDB
- **インフラ管理**: AWS / Serverless Framework

## 機能概要

- 月間勤務時間の入力/チェック/集計/エクスポート
- ログイン認証
- ユーザー権限管理
  - 一般（入力者）
  - 承認者
  - システム管理者（ユーザーの追加/変更）
- 月ごとの勤務入力
- 承認ワークフロー（承認済みデータはロック）

## プロジェクト構成

```
apro-timecard-b4/
├── backend/                  # バックエンド (Python/FastAPI)
│   ├── app/
│   │   ├── api/             # APIエンドポイント
│   │   ├── models/          # データモデル
│   │   ├── schemas/         # Pydanticスキーマ
│   │   ├── services/        # ビジネスロジック
│   │   ├── utils/           # ユーティリティ
│   │   ├── config.py        # 設定
│   │   └── main.py          # メインアプリケーション
│   ├── tests/               # テスト
│   ├── requirements.txt     # Python依存関係
│   └── serverless.yml       # Serverless Framework設定
├── frontend/                 # フロントエンド (Vue.js)
│   ├── src/
│   │   ├── components/      # コンポーネント
│   │   ├── views/           # ビュー
│   │   ├── stores/          # Piniaストア
│   │   ├── services/        # APIサービス
│   │   ├── router/          # Vue Router
│   │   ├── assets/          # 静的アセット
│   │   ├── App.vue          # ルートコンポーネント
│   │   └── main.js          # エントリーポイント
│   ├── package.json         # npm依存関係
│   └── vite.config.js       # Vite設定
└── docs/                     # ドキュメント
    ├── class-diagram.md     # クラス図
    ├── sequence-diagram.md  # シーケンス図
    ├── activity-diagram.md  # アクティビティ図
    └── usecase-diagram.md   # ユースケース図
```

## セットアップ

### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# ローカル起動
uvicorn app.main:app --reload

# テスト実行
pytest
```

### フロントエンド

```bash
cd frontend
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# テスト実行
npm test
```

### デプロイ (AWS)

```bash
cd backend
serverless deploy --stage prod
```

## API仕様

APIドキュメントは以下のURLで確認できます：
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`

## ライセンス

MIT License
