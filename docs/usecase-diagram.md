# ユースケース図

勤務月報システムのユースケースを示します。

## システム全体のユースケース図

```mermaid
flowchart LR
    subgraph Actors
        General[一般ユーザー<br>入力者]
        Approver[承認者]
        Admin[システム管理者]
    end

    subgraph TimeCardSystem[勤務月報システム]
        subgraph Authentication[認証]
            UC1([ログイン])
            UC2([ログアウト])
        end

        subgraph MonthlyManagement[月次記録管理]
            UC3([月次記録作成])
            UC4([月次記録閲覧])
            UC5([月次記録編集])
            UC6([月報申請])
        end

        subgraph DailyManagement[日次記録管理]
            UC7([日次記録入力])
            UC8([日次記録閲覧])
            UC9([日次記録編集])
            UC10([日次記録削除])
        end

        subgraph PatternManagement[勤務パターン管理]
            UC11([勤務パターン登録])
            UC12([勤務パターン編集])
            UC13([前月パターンコピー])
        end

        subgraph ApprovalWorkflow[承認ワークフロー]
            UC14([承認待ち一覧閲覧])
            UC15([月報承認])
            UC16([月報差し戻し])
            UC17([承認取り消し])
        end

        subgraph UserManagement[ユーザー管理]
            UC18([ユーザー一覧閲覧])
            UC19([ユーザー登録])
            UC20([ユーザー編集])
            UC21([ユーザー削除])
        end

        subgraph TimeCalculation[時間計算]
            UC22([勤務時間自動計算])
            UC23([残業時間計算])
            UC24([月次集計])
        end
    end

    %% 一般ユーザーのユースケース
    General --> UC1
    General --> UC2
    General --> UC3
    General --> UC4
    General --> UC5
    General --> UC6
    General --> UC7
    General --> UC8
    General --> UC9
    General --> UC10
    General --> UC11
    General --> UC12
    General --> UC13

    %% 承認者のユースケース（一般ユーザーの機能も使用可能）
    Approver --> UC1
    Approver --> UC2
    Approver --> UC3
    Approver --> UC4
    Approver --> UC5
    Approver --> UC6
    Approver --> UC7
    Approver --> UC8
    Approver --> UC9
    Approver --> UC10
    Approver --> UC11
    Approver --> UC12
    Approver --> UC13
    Approver --> UC14
    Approver --> UC15
    Approver --> UC16
    Approver --> UC17

    %% 管理者のユースケース
    Admin --> UC1
    Admin --> UC2
    Admin --> UC18
    Admin --> UC19
    Admin --> UC20
    Admin --> UC21

    %% 内部ユースケースの関係
    UC7 -.->|include| UC22
    UC9 -.->|include| UC22
    UC22 -.->|include| UC23
    UC6 -.->|include| UC24
```

## 詳細ユースケース説明

### 認証関連

| ユースケース | アクター | 説明 |
|------------|---------|------|
| UC1: ログイン | 全ユーザー | メールアドレスとパスワードでシステムにログイン |
| UC2: ログアウト | 全ユーザー | システムからログアウト |

### 月次記録管理

| ユースケース | アクター | 説明 |
|------------|---------|------|
| UC3: 月次記録作成 | 一般、承認者 | 新規月次記録を作成。氏名、所属、標準就労時間を設定 |
| UC4: 月次記録閲覧 | 一般、承認者 | 自分の月次記録を閲覧。承認者は他ユーザーの記録も閲覧可能 |
| UC5: 月次記録編集 | 一般、承認者 | 月次記録の基本情報を編集。承認済みは編集不可 |
| UC6: 月報申請 | 一般、承認者 | 月報を承認者に申請。申請時に集計が実行される |

### 日次記録管理

| ユースケース | アクター | 説明 |
|------------|---------|------|
| UC7: 日次記録入力 | 一般、承認者 | 日ごとの勤務データを入力。時間は自動計算される |
| UC8: 日次記録閲覧 | 一般、承認者 | 日次記録の詳細を閲覧 |
| UC9: 日次記録編集 | 一般、承認者 | 日次記録を編集。計算値の手動上書きも可能 |
| UC10: 日次記録削除 | 一般、承認者 | 日次記録を削除 |

### 勤務パターン管理

| ユースケース | アクター | 説明 |
|------------|---------|------|
| UC11: 勤務パターン登録 | 一般、承認者 | 始業/終業時刻、休憩時間を設定。最大3パターンまで |
| UC12: 勤務パターン編集 | 一般、承認者 | 既存パターンの時間を変更 |
| UC13: 前月パターンコピー | 一般、承認者 | 前月のパターンを当月にコピー |

### 承認ワークフロー

| ユースケース | アクター | 説明 |
|------------|---------|------|
| UC14: 承認待ち一覧閲覧 | 承認者 | 承認待ちの月報一覧を表示 |
| UC15: 月報承認 | 承認者 | 月報を承認。承認後はデータがロック |
| UC16: 月報差し戻し | 承認者 | 月報を差し戻し。コメント付与可能 |
| UC17: 承認取り消し | 承認者 | 承認済み月報の承認を取り消し |

### ユーザー管理

| ユースケース | アクター | 説明 |
|------------|---------|------|
| UC18: ユーザー一覧閲覧 | 管理者 | 全ユーザーの一覧を表示 |
| UC19: ユーザー登録 | 管理者 | 新規ユーザーを作成。権限を設定 |
| UC20: ユーザー編集 | 管理者 | ユーザー情報、権限を変更 |
| UC21: ユーザー削除 | 管理者 | ユーザーを削除 |

### 時間計算（システム内部）

| ユースケース | 説明 |
|------------|------|
| UC22: 勤務時間自動計算 | 出退勤時刻から実労働時間を計算。休憩時間を減算 |
| UC23: 残業時間計算 | 標準就労時間を超えた時間を残業として計算。深夜、休日残業を分類 |
| UC24: 月次集計 | 日次記録から月間の勤務日数、労働時間、残業時間等を集計 |

## 権限マトリクス

```mermaid
flowchart TB
    subgraph Permissions[権限マトリクス]
        subgraph GeneralPerms[一般ユーザー権限]
            G1[自分の月次記録CRUD]
            G2[自分の日次記録CRUD]
            G3[自分の勤務パターンCRUD]
            G4[月報申請]
        end

        subgraph ApproverPerms[承認者権限]
            A1[一般ユーザー権限全て]
            A2[他ユーザーの月次記録閲覧]
            A3[月報承認/差し戻し]
            A4[承認取り消し]
        end

        subgraph AdminPerms[管理者権限]
            D1[ユーザー一覧閲覧]
            D2[ユーザー登録]
            D3[ユーザー編集]
            D4[ユーザー削除]
            D5[権限設定]
        end
    end

    note1[承認者と管理者は<br>個別に設定可能]
    note2[承認だけ、管理だけ、<br>両方の権限を持つことが可能]
```

## ステート遷移図（月次記録）

```mermaid
stateDiagram-v2
    [*] --> Draft: 月次記録作成

    Draft --> Submitted: 申請
    Draft --> Draft: 編集

    Submitted --> Approved: 承認
    Submitted --> Rejected: 差し戻し

    Approved --> Draft: 承認取り消し
    Approved --> [*]: （ロック状態）

    Rejected --> Submitted: 再申請
    Rejected --> Draft: 編集

    note right of Draft
        編集可能
        日次入力可能
    end note

    note right of Submitted
        編集不可
        承認待ち
    end note

    note right of Approved
        編集不可（ロック）
        閲覧のみ可能
        承認者のみ取り消し可能
    end note

    note right of Rejected
        編集可能
        コメント確認可能
    end note
```
