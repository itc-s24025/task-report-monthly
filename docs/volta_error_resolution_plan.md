# Volta エラー解消計画書

**作成日**: 2026 年 1 月 26 日  
**プロジェクト**: task-report-monthly  
**場所**: `/home/masapo/PycharmProjects/task-report-monthly`

---

## 1. 現状分析

### エラー内容

```
Volta error: Could not locate executable `pnpm` in your project.
Please ensure that all project dependencies are installed with `npm install` or `yarn install`
```

### 環境情報

- **Volta**: v2.0.2 (インストール済み)
- **Node.js**: v24.11.0 (インストール済み)
- **pnpm**: インストールされていない
- **package.json**: 存在するが、`pnpm ^10.28.0` のみが依存関係として記載
- **ロックファイル**: 存在しない (package-lock.json, pnpm-lock.yaml, yarn.lock なし)

### 問題の原因

1. `package.json` に `pnpm` が依存関係として記載されているが、これは誤った設定
   - pnpm はパッケージマネージャーであり、プロジェクトの依存関係ではない
2. pnpm が Volta 経由でインストールされていないため、実行できない
3. このプロジェクトは Python プロジェクトであり、Node.js 依存関係は不要の可能性が高い

---

## 2. 解決方針

### オプション A: package.json を削除（推奨）

**理由**: このプロジェクトは Python/Flask プロジェクトであり、Node.js 依存関係は不要

**メリット**:

- シンプルで確実
- プロジェクトの本質に沿った構成
- 今後のエラーを防止

**デメリット**:

- 将来的にフロントエンドツール（Tailwind CSS、Vite など）を使う場合は再度設定が必要

### オプション B: Volta 経由で pnpm をインストール

**理由**: package.json を維持したい場合

**メリット**:

- Node.js エコシステムを活用できる準備が整う
- 将来的な拡張性

**デメリット**:

- 現状では不要な依存関係を追加
- メンテナンスコストが増加

---

## 3. 実施計画（オプション A: 推奨）

### ステップ 1: package.json のバックアップと削除

```bash
# バックアップを作成
cp package.json package.json.backup

# package.jsonを削除
rm package.json
```

### ステップ 2: 動作確認

```bash
# Pythonアプリケーションが正常に動作することを確認
python --version
pip list
python apps/app.py  # または該当する起動スクリプト
```

### ステップ 3: .gitignore の確認

```bash
# package.jsonが不要なら、将来的に誤って追加されないよう設定
echo "package.json" >> .gitignore  # 必要に応じて
```

---

## 4. 実施計画（オプション B: 代替案）

### ステップ 1: Volta 経由で pnpm をインストール

```bash
# pnpmをVoltaでインストール
volta install pnpm

# バージョン確認
pnpm --version
```

### ステップ 2: package.json の修正

```json
{
  "name": "task-report-monthly",
  "version": "1.0.0",
  "description": "IT業務における作業実績を日々記録し、月次で集計・報告するためのWebアプリケーション",
  "private": true,
  "scripts": {
    "test": "echo \"No tests specified\""
  },
  "volta": {
    "node": "24.11.0",
    "pnpm": "10.28.0"
  }
}
```

### ステップ 3: 動作確認

```bash
pnpm --version
node --version
```

---

## 5. 推奨事項

### 本プロジェクトに対する推奨

**オプション A（package.json 削除）を推奨**

理由:

1. これは Python/Flask プロジェクトである
2. README には Node.js 関連の記述がない
3. static ファイルや templates は既に存在し、ビルドプロセスは不要
4. シンプルさを保つことで、メンテナンス性が向上

### 将来的に Node.js が必要になった場合

その時点で適切な package.json を作成すれば良い:

```bash
pnpm init
pnpm add -D tailwindcss postcss autoprefixer  # 例
```

---

## 6. 実施後の確認項目

- [ ] volta エラーが解消されている
- [ ] Python アプリケーションが正常に起動する
- [ ] 既存の機能（タスク登録・一覧・削除）が動作する
- [ ] ドキュメント（README.md）の内容と整合性がある

---

## 7. リスク評価

| リスク                                          | 影響度 | 対策                                               |
| ----------------------------------------------- | ------ | -------------------------------------------------- |
| package.json 削除により何かの機能が動かなくなる | 低     | バックアップを作成済み。問題があればすぐに復元可能 |
| 将来的に Node.js ツールが必要になる             | 低     | その時点で再設定すれば良い（pnpm init）            |
| チーム内で認識齟齬が発生                        | 中     | この計画書を共有し、変更理由を明確にする           |

---

## 8. 実施タイミング

**即時実施可能**

理由:

- バックアップ作成により安全性を確保
- 変更内容がシンプルで明確
- 既存の Python 環境に影響しない

---

## 9. 補足: Volta とは

Volta は node.js と npm/yarn/pnpm のバージョン管理ツールです。

- プロジェクトごとに異なる Node.js バージョンを使い分けられる
- `package.json`の`volta`フィールドで自動的にバージョンを切り替える
- グローバルツールの管理も可能

このプロジェクトでは Volta は既にインストールされていますが、
Python プロジェクトのため現状では不要です。

---

**結論**: オプション A（package.json 削除）で進めることを推奨します。
