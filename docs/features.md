# ItCol 月次作業報告ツール - 機能仕様書

## 機能概要図

```mermaid
graph TB
    App["📱 ItCol 月次作業報告ツール"] --> Core["コア機能<br/>現在実装済み"]
    App --> Future["拡張機能<br/>将来実装予定"]

    Core --> C1["タスク管理<br/>✅ 登録"]
    Core --> C2["タスク管理<br/>✅ 表示"]
    Core --> C3["タスク管理<br/>✅ 削除"]

    Future --> F1["⏱️ タイマー"]
    Future --> F2["🏷️ カテゴリ"]
    Future --> F3["📊 月次集計"]
    Future --> F4["📄 レポート"]
    Future --> F5["🖨️ 印刷"]

    style App fill:#e1f5ff
    style Core fill:#c8e6c9
    style Future fill:#fff9c4
    style C1 fill:#a5d6a7
    style C2 fill:#a5d6a7
    style C3 fill:#a5d6a7
    style F1 fill:#ffb74d
    style F2 fill:#ffb74d
    style F3 fill:#ffb74d
    style F4 fill:#ffb74d
    style F5 fill:#ffb74d
```

---

## ✅ 実装済み機能

### 1. タスク登録機能

```
機能名: タスク新規登録
ステータス: ✅ 実装完了
エンドポイント: POST /add
対応URL: /add
```

**入力画面**:

```mermaid
graph TD
    A["タスク入力フォーム"] --> B["テキスト入力欄<br/>Max 100文字"]
    B --> C["送信ボタン"]
    C --> D["POST /add"]
    D --> E["リダイレクト /<br/>一覧画面へ"]

    style A fill:#e1f5ff
    style B fill:#fff9c4
    style C fill:#c8e6c9
    style D fill:#f3e5f5
    style E fill:#bbdefb
```

**処理フロー**:

1. ユーザーがフォームにタスク名を入力
2. 「追加」ボタンをクリック
3. `POST /add` リクエストを送信
4. バックエンド: 新しい `Todo` オブジェクトを作成
5. データベースに保存（INSERT）
6. 確認後、一覧画面にリダイレクト

**データベース処理**:

```python
# app.py内のコード
@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")        # フォーム値取得
    new_todo = Todo(title=title)             # Todoオブジェクト作成
    db.session.add(new_todo)                 # セッションに追加
    db.session.commit()                      # データベースコミット
    return redirect(url_for("home"))         # ホームにリダイレクト
```

---

### 2. タスク一覧表示機能

```
機能名: タスク一覧表示
ステータス: ✅ 実装完了
エンドポイント: GET /
表示URL: /
```

**表示画面構成**:

```mermaid
graph TD
    A["ホームページ GET /"] --> B["ヘッダー"]
    A --> C["DB情報表示"]
    A --> D["タスク入力フォーム"]
    A --> E["タスク一覧"]

    B --> B1["ページタイトル"]
    C --> C1["使用中DB<br/>PostgreSQL"]
    C --> C2["データベース名<br/>todo_db"]
    C --> C3["ユーザー<br/>todo_user"]

    D --> D1["テキスト入力"]
    D --> D2["追加ボタン"]

    E --> E1["タスク1"]
    E --> E2["タスク2"]
    E --> E3["削除ボタン"]

    style A fill:#e1f5ff
    style E fill:#c8e6c9
    style E1 fill:#a5d6a7
    style E2 fill:#a5d6a7
    style E3 fill:#ffccbc
```

**処理フロー**:

1. ユーザーがホームページ `/` にアクセス
2. バックエンド: `Todo.query.all()` で全タスクを取得
3. データベースから全レコードを読込
4. テンプレートにデータを渡す
5. HTMLレンダリング
6. ブラウザに表示

**データベース処理**:

```python
# app.py内のコード
@app.route("/", methods=["GET", "POST"])
def home():
    todo_list = Todo.query.all()            # 全タスク取得

    db_info = {
        'type': 'PostgreSQL',
        'database': 'todo_db',
        'user': 'todo_user',
        'host': 'localhost'
    }

    return render_template("index.html", todo_list=todo_list, db_info=db_info)
```

---

### 3. タスク削除機能

```
機能名: タスク削除
ステータス: ✅ 実装完了
エンドポイント: POST /delete/<id>
トリガー: 各タスクの削除ボタン
```

**削除フロー**:

```mermaid
graph TD
    A["タスク一覧画面"] --> B["削除ボタン<br/>クリック"]
    B --> C["POST /delete/3"]
    C --> D["バックエンド処理"]
    D --> E["ID=3のタスクを<br/>データベースから検索"]
    E --> F["該当タスクを削除"]
    F --> G["コミット"]
    G --> H["リダイレクト /"]
    H --> I["一覧画面を再表示<br/>削除済み"]

    style A fill:#e1f5ff
    style B fill:#ffccbc
    style C fill:#f3e5f5
    style D fill:#e0e0e0
    style E fill:#fff9c4
    style F fill:#ffccbc
    style G fill:#fff9c4
    style H fill:#bbdefb
    style I fill:#c8e6c9
```

**処理フロー**:

1. ユーザーが削除ボタンをクリック
2. `POST /delete/<id>` リクエストを送信
3. バックエンド: IDで該当タスクを検索
4. 検索結果を取得
5. データベースから削除（DELETE）
6. 変更をコミット
7. 一覧画面にリダイレクト

**データベース処理**:

```python
# app.py内のコード
@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()  # IDで検索
    db.session.delete(todo)                          # 削除
    db.session.commit()                              # コミット
    return redirect(url_for("home"))                 # ホームへリダイレクト
```

---

## ❌ 未実装機能（開発計画）

### フェーズ2: タイマー機能

```
機能名: タイマー機能
ステータス: ❌ 未実装
優先度: 高
概要: 作業時間の自動計測
```

**予定機能**:

```mermaid
graph TB
    A["⏱️ タイマー機能"] --> B["開始ボタン"]
    A --> C["停止ボタン"]
    A --> D["リセットボタン"]
    A --> E["タイム表示<br/>HH:MM:SS"]

    B --> F["タイマー開始"]
    C --> G["タイマー一時停止"]
    D --> H["タイマーリセット"]

    F --> I["経過時間を記録"]
    G --> I
    I --> J["タスクに時間を<br/>自動保存"]

    style A fill:#fff9c4
    style E fill:#ffe0b2
    style J fill:#c8e6c9
```

**データベース拡張**:

```sql
ALTER TABLE todo ADD COLUMN time_spent INTEGER;  -- 秒単位
ALTER TABLE todo ADD COLUMN started_at TIMESTAMP;
ALTER TABLE todo ADD COLUMN paused_at TIMESTAMP;
```

---

### フェーズ2: カテゴリ分類機能

```
機能名: カテゴリ分類機能
ステータス: ❌ 未実装
優先度: 中
概要: タスクをカテゴリで分類
```

**予定機能**:

```mermaid
graph TD
    A["🏷️ カテゴリ機能"] --> B["新規カテゴリ作成"]
    A --> C["タスクにカテゴリ付け"]
    A --> D["カテゴリでフィルタリング"]

    B --> B1["カテゴリ一覧"]
    C --> C1["ドロップダウン選択"]
    D --> D1["表示切替"]

    D1 --> E["カテゴリ別表示"]

    style A fill:#fff9c4
    style B1 fill:#bbdefb
    style C1 fill:#e1f5ff
    style E fill:#c8e6c9
```

**データベース拡張**:

```sql
CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL
);

ALTER TABLE todo ADD COLUMN category_id INTEGER;
ALTER TABLE todo ADD FOREIGN KEY (category_id)
    REFERENCES category(id) ON DELETE SET NULL;
```

**予定カテゴリ例**:

- 📚 学習
- 💻 実装
- 🧪 テスト
- 📝 ドキュメント
- 🐛 デバッグ
- 📞 会議

---

### フェーズ3: 月次集計機能

```
機能名: 月次集計機能
ステータス: ❌ 未実装
優先度: 高
概要: プロジェクト別、カテゴリ別の集計
```

**予定集計結果**:

```mermaid
graph TB
    A["📊 月次集計"] --> B["プロジェクト別"]
    A --> C["カテゴリ別"]
    A --> D["日別"]

    B --> B1["プロジェクトA: 20時間"]
    B --> B2["プロジェクトB: 15時間"]
    C --> C1["学習: 10時間"]
    C --> C2["実装: 20時間"]
    D --> D1["2月1日: 8時間"]
    D --> D2["2月2日: 12時間"]

    B1 --> E["月次レポートへ"]
    B2 --> E
    C1 --> E

    style A fill:#fff9c4
    style E fill:#c8e6c9
```

**SQL集計例**:

```sql
-- プロジェクト別集計
SELECT project_id, SUM(time_spent)
FROM todo
WHERE DATE_TRUNC('month', created_at) = CURRENT_DATE
GROUP BY project_id;

-- カテゴリ別集計
SELECT category_id, SUM(time_spent)
FROM todo
WHERE DATE_TRUNC('month', created_at) = CURRENT_DATE
GROUP BY category_id;
```

---

### フェーズ3: レポート画面

```
機能名: 月次レポート画面
ステータス: ❌ 未実装
優先度: 高
概要: 月次集計結果をグラフ表示
```

**レポート構成**:

```mermaid
graph TD
    A["📄 月次レポート画面"] --> B["サマリー<br/>合計時間<br/>タスク数"]
    A --> C["グラフ表示"]
    A --> D["詳細表"]

    C --> C1["円グラフ<br/>カテゴリ別"]
    C --> C2["棒グラフ<br/>プロジェクト別"]
    C --> C3["折れ線グラフ<br/>日別推移"]

    B --> E["Print"]
    D --> E

    style A fill:#fff9c4
    style C1 fill:#e1f5ff
    style C2 fill:#bbdefb
    style C3 fill:#90caf9
    style E fill:#c8e6c9
```

**グラフライブラリ候補**:

- Chart.js
- Recharts
- Plotly.js
- D3.js

---

### フェーズ4: 印刷・エクスポート機能

```
機能名: A4印刷・エクスポート機能
ステータス: ❌ 未実装
優先度: 中
概要: 月次レポートの印刷/出力
```

**出力形式**:

```mermaid
graph TD
    A["🖨️ 出力機能"] --> B["A4印刷"]
    A --> C["PDF生成"]
    A --> D["CSV出力"]
    A --> E["Excel出力"]

    B --> F["print()関数"]
    C --> G["python-pdfkit"]
    D --> H["csv module"]
    E --> I["openpyxl"]

    style A fill:#fff9c4
    style B fill:#c8e6c9
    style C fill:#c8e6c9
    style D fill:#c8e6c9
    style E fill:#c8e6c9
```

---

## 機能マトリックス

| #   | 機能         | 説明               | ステータス | 優先度 | 難易度 | 工数(h) |
| --- | ------------ | ------------------ | ---------- | ------ | ------ | ------- |
| 1   | タスク登録   | タスクの新規登録   | ✅ 完了    | 必須   | 低     | 1       |
| 2   | タスク一覧   | 登録済みタスク表示 | ✅ 完了    | 必須   | 低     | 1       |
| 3   | タスク削除   | タスクの削除       | ✅ 完了    | 必須   | 低     | 1       |
| 4   | タイマー機能 | 作業時間計測       | ❌ 未実装  | 高     | 中     | 4       |
| 5   | カテゴリ分類 | タスク分類         | ❌ 未実装  | 中     | 中     | 3       |
| 6   | 月次集計     | 集計・分析         | ❌ 未実装  | 高     | 中     | 5       |
| 7   | レポート画面 | グラフ表示         | ❌ 未実装  | 高     | 高     | 6       |
| 8   | 印刷機能     | PDF/Excel出力      | ❌ 未実装  | 中     | 高     | 4       |

---

## 使用例

### 例1: 平日の業務ログ

```
2026年2月2日（月）
┌─────────────────────────────────────────┐
│ 09:00 - タスク登録「〇〇システム調査」    │ → タスク追加
│ 10:00 - タスク登録「△△コード実装」      │ → タスク追加
│ 11:30 - タスク登録「□□テスト実施」      │ → タスク追加
│ 14:00 - 月次集計確認                   │ → レポート表示
│ 16:00 - 報告書出力                     │ → PDF生成・印刷
└─────────────────────────────────────────┘
```

---

## 今後の拡張方針

```mermaid
graph LR
    A["v1.0<br/>基本機能"] --> B["v1.1<br/>タイマー"]
    B --> C["v1.2<br/>カテゴリ"]
    C --> D["v2.0<br/>レポート"]
    D --> E["v2.1<br/>印刷機能"]
    E --> F["v3.0<br/>企業版<br/>認証・権限"]

    style A fill:#c8e6c9
    style B fill:#fff9c4
    style C fill:#fff9c4
    style D fill:#fff9c4
    style E fill:#fff9c4
    style F fill:#e1f5ff
```

---

**最終更新日**: 2026年2月2日
