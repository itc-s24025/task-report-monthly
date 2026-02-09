# ItCol 月次作業報告ツール - アーキテクチャドキュメント

## システムアーキテクチャ全体図

```mermaid
graph TB
    subgraph Client["クライアント層"]
        Browser["🌐 Webブラウザ"]
    end

    subgraph Frontend["フロントエンド層<br/>Next.js + TypeScript"]
        NextApp["Next.js アプリケーション"]
        Pages["📄 ページコンポーネント"]
        Styles["🎨 スタイル<br/>CSS Modules"]
    end

    subgraph API["API層<br/>Flask REST"]
        FlaskApp["Flask アプリケーション"]
        Routes["🔌 ルートハンドラー<br/>GET / POST"]
    end

    subgraph DataLayer["データアクセス層<br/>SQLAlchemy ORM"]
        ORM["SQLAlchemy"]
        Models["📊 データモデル<br/>Todo"]
    end

    subgraph Database["データベース層<br/>PostgreSQL"]
        DB["PostgreSQL"]
        Tables["📋 テーブル<br/>Todo"]
    end

    Browser -->|HTTP/HTTPS| NextApp
    NextApp --> Pages
    NextApp --> Styles
    Pages -->|REST API| FlaskApp
    FlaskApp --> Routes
    Routes -->|オブジェクトマッピング| ORM
    ORM --> Models
    Models -->|SQL| DB
    DB --> Tables

    style Client fill:#fff9c4
    style Frontend fill:#e1f5ff
    style API fill:#f3e5f5
    style DataLayer fill:#e0e0e0
    style Database fill:#e8f5e9
```

---

## レイヤー別詳細設計

### 1. フロントエンド層 (Frontend)

```mermaid
graph TD
    A["Next.js<br/>フレームワーク"] --> B["ページコンポーネント<br/>app/page.tsx"]
    A --> C["レイアウトコンポーネント<br/>app/layout.tsx"]
    B --> D["スタイリング<br/>CSS Modules<br/>globals.css"]
    B --> E["静的ファイル<br/>public/"]

    B -->|API Call| F["バックエンドAPI<br/>http://localhost:5000"]

    style A fill:#bbdefb
    style B fill:#e1f5ff
    style C fill:#e1f5ff
    style D fill:#fff9c4
    style E fill:#fce4ec
    style F fill:#f3e5f5
```

**責務**:

- ユーザーインターフェース提供
- タスク入力フォーム
- タスク一覧表示
- レスポンシブデザイン

**技術スタック**:

- React + Next.js
- TypeScript
- CSS Modules

---

### 2. API層 (Flask Backend)

```mermaid
graph TD
    A["Flask アプリケーション<br/>app.py"] --> B["GET /"
    タスク一覧表示"]
    A --> C["POST /add<br/>タスク追加"]
    A --> D["POST /delete/<id><br/>タスク削除"]

    B --> E["SQLAlchemy<br/>Todo.query.all"]
    C --> F["SQLAlchemy<br/>Todo追加"]
    D --> G["SQLAlchemy<br/>Todo削除"]

    H["render_template<br/>index.html"] <--> B
    I["redirect<br/>home"] <--> C
    J["redirect<br/>home"] <--> D

    style A fill:#f3e5f5
    style B fill:#ffe0b2
    style C fill:#c8e6c9
    style D fill:#ffccbc
    style E fill:#e0e0e0
    style F fill:#e0e0e0
    style G fill:#e0e0e0
    style H fill:#fff9c4
    style I fill:#fff9c4
    style J fill:#fff9c4
```

**エンドポイント**:

| メソッド | URL          | 処理             | レスポンス        |
| -------- | ------------ | ---------------- | ----------------- |
| GET      | /            | タスク一覧を取得 | HTML (index.html) |
| POST     | /add         | 新規タスクを追加 | リダイレクト      |
| POST     | /delete/<id> | タスクを削除     | リダイレクト      |

**フロー**:

1. リクエスト受信
2. SQLAlchemy でデータベース操作
3. テンプレートにレンダリングまたはリダイレクト

---

### 3. データアクセス層 (SQLAlchemy ORM)

```mermaid
graph LR
    A["SQLAlchemy<br/>ORM"] -->|マッピング| B["Python<br/>Todoクラス"]
    B -->|SQL変換| C["PostgreSQL<br/>SQL"]

    D["Todo.query.all()"] --> A
    E["db.session.add()"] --> A
    F["db.session.delete()"] --> A
    G["db.session.commit()"] --> A

    A -->|SQLを実行| H["PostgreSQL<br/>ドライバー<br/>psycopg2"]
    H -->|接続| I["PostgreSQL<br/>データベース"]

    style A fill:#e0e0e0
    style B fill:#f3e5f5
    style C fill:#bbdefb
    style D fill:#c8e6c9
    style E fill:#c8e6c9
    style F fill:#ffccbc
    style G fill:#ffe0b2
    style H fill:#e8f5e9
    style I fill:#a5d6a7
```

**主要なメソッド**:

- `Todo.query.all()` - 全タスクを取得
- `db.session.add(todo)` - タスクを追加
- `db.session.delete(todo)` - タスクを削除
- `db.session.commit()` - 変更を確定

---

### 4. データベース層 (PostgreSQL)

```mermaid
graph TD
    A["PostgreSQL"] --> B["Database: todo_db"]
    B --> C["Schema: public"]
    C --> D["Table: todo"]

    D --> E["Column: id<br/>Type: INTEGER<br/>Primary Key<br/>Auto Increment"]
    D --> F["Column: title<br/>Type: VARCHAR<br/>Max Length: 100"]

    G["Connection"] -->|User: todo_user| A
    G -->|Password: todo_password| A
    G -->|Host: localhost| A

    style A fill:#a5d6a7
    style B fill:#e8f5e9
    style C fill:#e8f5e9
    style D fill:#c8e6c9
    style E fill:#fff9c4
    style F fill:#fff9c4
    style G fill:#bbdefb
```

**テーブル設計**:

```sql
CREATE TABLE todo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL
);
```

**接続情報**:

```
Host: localhost
Database: todo_db
User: todo_user
Password: todo_password
Port: 5432 (デフォルト)
```

---

## データフロー

### ユースケース1: タスク一覧表示

```mermaid
sequenceDiagram
    participant User as 👤 ユーザー
    participant Browser as 🌐 ブラウザ
    participant Frontend as 📄 Next.js
    participant API as 🔌 Flask API
    participant ORM as 🗄️ SQLAlchemy
    participant DB as 💾 PostgreSQL

    User->>Browser: ページにアクセス
    Browser->>Frontend: GET /
    Frontend->>API: GET /
    API->>ORM: Todo.query.all()
    ORM->>DB: SELECT * FROM todo
    DB-->>ORM: [Todo1, Todo2, ...]
    ORM-->>API: [Todo1, Todo2, ...]
    API-->>Frontend: render_template('index.html', todo_list=...)
    Frontend-->>Browser: HTML表示
    Browser-->>User: タスク一覧を表示
```

### ユースケース2: タスク追加

```mermaid
sequenceDiagram
    participant User as 👤 ユーザー
    participant Form as 📝 フォーム
    participant API as 🔌 Flask API
    participant ORM as 🗄️ SQLAlchemy
    participant DB as 💾 PostgreSQL

    User->>Form: タスク入力
    Form->>API: POST /add (title=タスク名)
    API->>ORM: new_todo = Todo(title=...)
    API->>ORM: db.session.add(new_todo)
    API->>ORM: db.session.commit()
    ORM->>DB: INSERT INTO todo VALUES (...)
    DB-->>ORM: 成功
    ORM-->>API: コミット完了
    API-->>Form: redirect /
    Form-->>User: 一覧画面にリダイレクト
```

### ユースケース3: タスク削除

```mermaid
sequenceDiagram
    participant User as 👤 ユーザー
    participant UI as 🖥️ UI
    participant API as 🔌 Flask API
    participant ORM as 🗄️ SQLAlchemy
    participant DB as 💾 PostgreSQL

    User->>UI: 削除ボタンをクリック
    UI->>API: POST /delete/3
    API->>ORM: todo = Todo.query.filter_by(id=3).first()
    ORM->>DB: SELECT * FROM todo WHERE id = 3
    DB-->>ORM: Todo(id=3, title=...)
    ORM-->>API: Todo object
    API->>ORM: db.session.delete(todo)
    API->>ORM: db.session.commit()
    ORM->>DB: DELETE FROM todo WHERE id = 3
    DB-->>ORM: 成功
    ORM-->>API: コミット完了
    API-->>UI: redirect /
    UI-->>User: 一覧画面を更新
```

---

## 技術スタック全体図

```mermaid
graph TB
    subgraph Frontend["フロントエンド"]
        React["React"]
        NextJS["Next.js"]
        TypeScript["TypeScript"]
        CSS["CSS Modules"]
    end

    subgraph Backend["バックエンド"]
        Flask["Flask"]
        Python["Python"]
        SQLAlchemy["SQLAlchemy"]
    end

    subgraph Database["データベース"]
        PostgreSQL["PostgreSQL"]
    end

    subgraph DevTools["開発ツール"]
        Node["Node.js 24.11.0"]
        pnpm["pnpm 10.28.0"]
        pip["pip (Python Package Manager)"]
    end

    React --> NextJS
    NextJS --> TypeScript
    TypeScript --> CSS

    Flask --> Python
    Python --> SQLAlchemy
    SQLAlchemy --> PostgreSQL

    pnpm --> Frontend
    pip --> Backend
    Node --> Frontend

    Frontend -->|HTTP/REST| Backend
    Backend -->|SQL| Database

    style Frontend fill:#e1f5ff
    style Backend fill:#f3e5f5
    style Database fill:#e8f5e9
    style DevTools fill:#fff9c4
```

---

## デプロイメント構成

```mermaid
graph TB
    subgraph Dev["開発環境"]
        DevFrontend["Next.js Dev Server<br/>localhost:3000"]
        DevBackend["Flask Dev Server<br/>localhost:5000"]
        DevDB["PostgreSQL<br/>localhost:5432"]
    end

    subgraph Docker["Docker環境"]
        DockerCompose["docker-compose"]
        ContainerBackend["Flask Container"]
        ContainerDB["PostgreSQL Container"]
    end

    subgraph Production["本番環境<br/>予定"]
        ProdFrontend["Vercel / Netlify"]
        ProdBackend["Heroku / AWS"]
        ProdDB["RDS / Cloud SQL"]
    end

    DevFrontend <--> DevBackend
    DevBackend <--> DevDB

    DockerCompose --> ContainerBackend
    DockerCompose --> ContainerDB
    ContainerBackend <--> ContainerDB

    Dev -->|セットアップ提供| Docker
    Docker -->|本番化| Production

    style Dev fill:#fff9c4
    style Docker fill:#e1f5ff
    style Production fill:#c8e6c9
```

---

## 環境変数設定

### バックエンド環境変数

```
USE_POSTGRESQL=1                    # PostgreSQL使用フラグ
FLASK_ENV=development               # 開発環境
FLASK_DEBUG=True                    # デバッグモード

# PostgreSQL接続情報
DB_USER=todo_user
DB_PASSWORD=todo_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=todo_db
```

---

## 今後の拡張性

### 新機能追加時のアーキテクチャ拡張

```mermaid
graph TB
    subgraph Current["現在の実装"]
        A["Todo管理"]
    end

    subgraph Future["将来の拡張"]
        B["タイマー機能"]
        C["カテゴリ分類"]
        D["月次集計"]
        E["ユーザー認証"]
        F["ファイルアップロード"]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F

    B --> G["時間計測API"]
    C --> H["タグ管理API"]
    D --> I["集計API"]
    E --> J["認証API"]
    F --> K["ファイルAPI"]

    style A fill:#c8e6c9
    style B fill:#fff9c4
    style C fill:#fff9c4
    style D fill:#fff9c4
    style E fill:#fff9c4
    style F fill:#fff9c4
```

---

**最終更新日**: 2026年2月2日
