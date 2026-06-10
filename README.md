# CodeBridge Ringi — 稟議AIエージェント

日本企業向けの**稟議（りんぎ）AIエージェントシステム**。申請者が自然文で書くだけで、AIが稟議書の草案・承認タイプ・最適な承認者を自動で提案し、承認フローまでを一気通貫で効率化します。Microsoft（Azure）ハッカソン向けに開発したプロジェクトです。

> **🟢 現在は DEMOモードで公開中（ポートフォリオ用・課金0円）**
> ハッカソン終了に伴い Azure 課金を停止しているため、AI生成ステップはサンプル応答に差し替えています。
> **ログイン → 自然文入力 → 稟議書生成 → 承認** までの全フローは、APIキー無し・無料でそのまま体験できます。
> 実際に Azure OpenAI を動かす場合は `DEMO_MODE=0` を設定してください（[下記参照](#実際にaiを動かす場合)）。

---

## ✨ 主な機能

| 機能 | 概要 |
|---|---|
| 🤖 **稟議書の自動生成** | 自然文の申請内容から、タイトル・本文（背景／変更内容／リスク／承認依頼）・キーポイントをAIが起案 |
| 🏷 **承認タイプの自動判定** | 確認型／通知型／判断型／合議型をAIが分類 |
| 👤 **承認者のAIレコメンド** | 役職・役割から最適な承認者を1名提案（理由つき） |
| ✅ **承認フロー** | 承認 / 差し戻し / 再生成（フィードバックを反映して作り直し） |
| 🛠 **コード変更の自動反映（拡張機能）** | 「画面を変えたい」等の申請を検知し、AIがHTMLを修正→サンドボックス検証→承認時に自動適用 |
| 📊 **分析ダッシュボード** | 申請統計・承認ボトルネック・承認者別の傾向・自動化候補を可視化 |
| 🔐 **認証・権限管理** | JWT認証、役職（rank）ベースの権限、ユーザー／役職のCRUD、パスワード管理 |
| 💰 **コスト計測 / 監査ログ** | AI利用コストの月次集計、全操作の監査ログとCSVエクスポート |

### 承認タイプ
| タイプ | 意味 |
|---|---|
| 確認型 | 情報共有・報告 |
| 通知型 | 事後承認でよいもの |
| 判断型 | 上司の判断が必要 |
| 合議型 | 複数人での議論が必要 |

---

## 🧱 技術スタック

- **バックエンド**: FastAPI / Python
- **データベース**: SQLite
- **AI**: Azure OpenAI（o4-mini）
- **フロントエンド**: シングルページ HTML（ダークテーマ・ライトテーマ対応）
- **認証**: JWT（PyJWT / HS256、有効期限24時間・ステートレス）
- **インフラ**: Azure App Service + GitHub Actions（CI/CD）

## 🗺 アーキテクチャ

```
ブラウザ（SPA: frontend/index.html）
        │  REST / JWT
        ▼
FastAPI（api_main.py）
   ├─ core/auth.py              認証・DB操作（SQLite）
   ├─ core/ringi_orchestrator.py  稟議書をAI起案（Azure OpenAI）
   ├─ core/orchestrator.py      コード変更パイプライン
   ├─ core/sandbox.py           生成HTMLの安全な検証・適用
   └─ core/azure_client.py      Azure OpenAI クライアント（★課金経路の集約点）
```

申請の分析（`analyze_request`）も、コード変更パイプライン（`generate_code` ほか）も、AI呼び出しはすべて `core/azure_client.py::_call()` に集約されています。`DEMO_MODE` はこの1点を含めて確実に塞ぐ設計です。

---

## 🚀 ローカルで動かす（DEMOモード・0円）

```bash
git clone https://github.com/t-k-haru/codebridge-ringi.git
cd codebridge-ringi
pip install -r requirements.txt

# DEMO_MODE はデフォルトON（APIキー不要）
uvicorn api_main:app --host 0.0.0.0 --port 8000
```

ブラウザで `http://localhost:8000` を開き、下記アカウントでログインしてください。

### テストアカウント
| ロール | メール | パスワード |
|---|---|---|
| admin | admin@codebridge.ai | Admin1234! |
| manager | manager@codebridge.ai | Manager1234! |
| staff | staff@codebridge.ai | Staff1234! |

---

## 実際にAIを動かす場合

DEMOモードを切り、Azure OpenAI のキーを設定します。

```bash
# .env
DEMO_MODE=0
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=o4-mini
```

`DEMO_MODE=1`（デフォルト）のあいだは Azure OpenAI を一切呼ばず、課金は発生しません。

---

## 📁 ディレクトリ構成

```
api_main.py              FastAPI エントリーポイント・全APIエンドポイント
core/
  auth.py                ユーザー認証・DB操作（SQLite）
  ringi_orchestrator.py  Azure OpenAI で稟議書を自動生成
  orchestrator.py        コード変更パイプライン
  sandbox.py             生成コードの安全な検証・適用
  azure_client.py        Azure OpenAI クライアント
frontend/
  index.html             シングルページフロントエンド（SPA）
.github/workflows/
  deploy.yml             Azure App Service へのデプロイ（現在は手動実行のみ）
```

---

> 📌 **ポートフォリオ注記**: 本リポジトリはハッカソン提出後、Azure 課金を停止し DEMOモードで公開しています。ライブのAzure環境（旧本番URL）は停止済みです。
