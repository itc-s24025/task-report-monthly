# Monorepo 構造への移行計画書

**作成日**: 2026 年 1 月 26 日  
**プロジェクト**: task-report-monthly  
**目標**: Pyton バックエンドと Next.js フロントエンドを monorepo 構造で統一管理

---

## 1. 現在の構造

```
task-report-monthly/
├── apps/
│   ├── backend/          (Flask + Python)
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── setup.sh
│   │   ├── docker-compose.yml
│   │   └── ...
│   └── frontend/         (Next.js)
│       ├── package.json
│       ├── app/
│       └── ...
├── .venv/               (Python仮想環境)
├── package.json.backup
└── docs/
```

### 現在の問題点

- バックエンド（Python）とフロントエンド（Node.js）が分離
- 毎回 2 つのターミナルで起動が必要
- 依存関係管理が別々
- ビルド・デプロイプロセスが不統一

---

## 2. 目標となる Monorepo 構造

```
task-report-monthly/
├── packages/
│   ├── backend/
│   │   ├── src/
│   │   │   ├── app.py
│   │   │   ├── models/
│   │   │   ├── routes/
│   │   │   └── ...
│   │   ├── requirements.txt
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── package.json        (← Pythonプロジェクト用のメタデータ)
│   │
│   └── frontend/
│       ├── src/
│       ├── app/
│       ├── package.json
│       ├── tsconfig.json
│       ├── Dockerfile
│       └── ...
│
├── root-level/
│   ├── package.json            (← monorepo管理用)
│   ├── pnpm-workspace.yaml     (← pnpm workspaces設定)
│   ├── docker-compose.yml      (← 両方を同時起動)
│   ├── Makefile               (← 便利コマンド)
│   └── .github/workflows/      (← CI/CD)
│
├── docs/
├── .gitignore
├── .env.example
└── README.md
```

---

## 3. Monorepo 化のメリット

| メリット           | 説明                                             |
| ------------------ | ------------------------------------------------ |
| **統一管理**       | 依存関係、ビルド、デプロイを一箇所で管理         |
| **シンプル起動**   | 1 コマンドで全サービス起動可能                   |
| **コード共有**     | バックエンド・フロントエンド間でコードを共有可能 |
| **原子的コミット** | 関連する変更を 1 つのコミットで管理              |
| **一括テスト**     | 全プロジェクトの統合テストが容易                 |
| **デプロイ簡素化** | Docker Compose で統一デプロイ                    |

---

## 4. 実装方針

### フェーズ 1: ディレクトリ構造の整理（低リスク）

```bash
# 1. packages/ ディレクトリを作成
mkdir -p packages

# 2. 既存のapps/backend → packages/backend に移動
mv apps/backend packages/

# 3. 既存のapps/frontend → packages/frontend に移動
mv apps/frontend packages/

# 4. 空のappsディレクトリを削除
rmdir apps
```

### フェーズ 2: Root-level 設定（medium risk）

```
作成予定ファイル:
- pnpm-workspace.yaml (root)
- package.json (root)
- docker-compose.yml (root)
- Makefile (root)
- .env.example
```

### フェーズ 3: Python 側の整理（medium risk）

```
packages/backend/内で:
- requirements.txt を pyproject.toml に統合（オプション）
- setup.py の追加（オプション）
- package.json の追加（pnpm workspacesで統一管理）
```

### フェーズ 4: CI/CD and Scripts（low risk）

```
作成予定ファイル:
- Makefile でコマンド統一
- Docker Compose で両方起動
- GitHub Actions設定
```

---

## 5. 実装手順（詳細）

### Step 1: ディレクトリ構成変更

```bash
# プロジェクトルートで実行
cd /home/masapo/PycharmProjects/task-report-monthly

# Step 1-1: packages ディレクトリ作成
mkdir -p packages

# Step 1-2: ファイル移動
mv apps/backend packages/
mv apps/frontend packages/

# Step 1-3: 空の apps ディレクトリ削除
rmdir apps

# 結果確認
ls -la
# → packages/ ディレクトリが作成されている
```

### Step 2: Root-level package.json 作成

```json
{
  "name": "task-report-monthly",
  "version": "1.0.0",
  "description": "IT業務における月次作業報告ツール",
  "private": true,
  "type": "module",
  "workspaces": ["packages/*"],
  "scripts": {
    "dev": "pnpm -r dev",
    "build": "pnpm -r build",
    "start": "pnpm -r start",
    "lint": "pnpm -r lint",
    "test": "pnpm -r test",
    "backend:dev": "pnpm -F backend dev",
    "frontend:dev": "pnpm -F frontend dev",
    "docker:up": "docker-compose up -d",
    "docker:down": "docker-compose down",
    "docker:build": "docker-compose build"
  },
  "volta": {
    "node": "24.11.0",
    "pnpm": "10.28.0"
  }
}
```

### Step 3: Root-level pnpm-workspace.yaml 作成

```yaml
packages:
  - "packages/*"

catalog:
  react: 19.2.3
  react-dom: 19.2.3
  typescript: ^5
  next: 16.1.3
  eslint: ^9
  flask: ">=3.0.0,<4.0.0"
  sqlalchemy: ">=3.1.0,<4.0.0"
```

### Step 4: Root-level docker-compose.yml 作成

```yaml
version: "3.8"

services:
  backend:
    build:
      context: ./packages/backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      USE_POSTGRESQL: 1
    depends_on:
      - postgres
    volumes:
      - ./packages/backend:/app

  frontend:
    build:
      context: ./packages/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:5000
    depends_on:
      - backend
    volumes:
      - ./packages/frontend:/app
      - /app/node_modules

  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: todo_db
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: todo_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Step 5: Makefile 作成

```makefile
.PHONY: help install dev build test lint clean docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install        - Install all dependencies"
	@echo "  make dev            - Start development servers"
	@echo "  make backend:dev    - Start backend only"
	@echo "  make frontend:dev   - Start frontend only"
	@echo "  make build          - Build all packages"
	@echo "  make lint           - Lint all packages"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean all build artifacts"
	@echo "  make docker:build   - Build Docker images"
	@echo "  make docker:up      - Start services with Docker"
	@echo "  make docker:down    - Stop Docker services"

install:
	pnpm install

dev:
	pnpm dev

backend:dev:
	pnpm -F backend dev

frontend:dev:
	pnpm -F frontend dev

build:
	pnpm build

lint:
	pnpm lint

test:
	pnpm test

clean:
	rm -rf packages/*/node_modules
	rm -rf packages/backend/.venv
	rm -rf packages/*/dist
	rm -rf packages/frontend/.next

docker:build:
	docker-compose build

docker:up:
	docker-compose up -d

docker:down:
	docker-compose down
```

### Step 6: 各 package 内の package.json 更新

**packages/backend/package.json:**

```json
{
  "name": "@task-report-monthly/backend",
  "version": "1.0.0",
  "description": "Flask backend for task report system",
  "private": true,
  "scripts": {
    "dev": "python app.py",
    "build": "echo 'No build needed for Python'",
    "start": "python app.py"
  }
}
```

**packages/frontend/package.json:**

```json
{
  "name": "@task-report-monthly/frontend",
  "version": "0.1.0",
  "description": "Next.js frontend for task report system",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  },
  "dependencies": {
    "next": "16.1.3",
    "react": "19.2.3",
    "react-dom": "19.2.3"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.1.3",
    "typescript": "^5"
  },
  "volta": {
    "node": "24.11.0",
    "pnpm": "10.28.0"
  }
}
```

---

## 6. 移行実行計画

### 優先度と実装順序

| 優先度 | タスク                           | 難度 | 影響度 | 実装者     |
| ------ | -------------------------------- | ---- | ------ | ---------- |
| 1      | ディレクトリ構造変更             | 低   | 高     | 自動化可能 |
| 2      | Root-level package.json 作成     | 低   | 高     | 手動       |
| 3      | pnpm-workspace.yaml 作成         | 低   | 高     | 手動       |
| 4      | 各 packages/\*/package.json 更新 | 低   | 中     | 手動       |
| 5      | docker-compose.yml 作成          | 中   | 中     | 手動       |
| 6      | Makefile 作成                    | 低   | 低     | 手動       |
| 7      | CI/CD 設定                       | 高   | 低     | 手動       |

---

## 7. リスク評価と対策

| リスク                           | 影響度 | 対策                                           |
| -------------------------------- | ------ | ---------------------------------------------- |
| ファイル移動で変更履歴が失われる | 中     | Git で全変更を記録。必要に応じてリベース       |
| 既存スクリプトが動作しなくなる   | 中     | パスを相対パス化し、プロジェクトルートから実行 |
| 依存関係の競合                   | 低     | pnpm workspaces が自動で解決                   |
| チームメンバーが戸惑う           | 低     | README.md と CONTRIBUTING.md を更新            |

---

## 8. 段階的な移行戦略

### 案 A: 一括移行（推奨）

- メリット: 素早く完了
- デメリット: 一度に多くの変更

### 案 B: 段階的移行

- Step 1: ディレクトリ構造のみ変更
- Step 2: Root-level package.json 追加
- Step 3: Docker 統合
- Step 4: CI/CD 設定

**推奨**: **案 A（一括移行）** - 既に Git で管理されているので変更履歴は保持される

---

## 9. 移行後のワークフロー

### 開発環境セットアップ

```bash
# 1回だけ実行
pnpm install

# 全サービス起動（1コマンド）
make dev

# または個別起動
make backend:dev  # ターミナル1
make frontend:dev # ターミナル2
```

### Docker 環境

```bash
# ビルドして起動
make docker:build
make docker:up

# 停止
make docker:down
```

---

## 10. 成功基準

- ✅ 全ファイルが Git で正常に追跡される
- ✅ `pnpm install` で全依存関係がインストール可能
- ✅ `make dev` で両サービスが起動可能
- ✅ `docker-compose up` でコンテナ化できる
- ✅ 既存の機能が全て正常に動作

---

## 11. 次のステップ

実装を開始しますか？以下から選択してください：

**オプション A**: 完全な一括移行（推奨）

```bash
# 実装フェーズ1～4を自動実行
```

**オプション B**: 段階的移行

```bash
# Step 1 のみ実行して確認後、次に進む
```

---

**結論**: Monorepo 化により、開発効率が大幅に向上します。推奨は**一括移行**です。
