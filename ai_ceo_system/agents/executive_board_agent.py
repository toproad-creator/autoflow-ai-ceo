import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT_DIR, ".env"))
except ImportError:
    pass

BOARD_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "board_meetings")
LATEST_BOARD_MD = os.path.join(BOARD_DIR, "latest_board_meeting.md")


class ExecutiveBoardAgent:
    """利益創出特化型・自律AI役員会議エージェント (Autonomous Profit-First Executive Board)
    目的はただ一つ：「1円でも早く、1円でも多くの実売上・純利益を生み出すこと」。
    毎朝のオーケストレーター稼働時に、以下の5名の専門役員エージェントが実測データをもとに議論し、
    ボトルネックの特定・本日の改善策の決定・各実行エージェントへの実装命令を行う。
      - CEO (最高経営責任者): 最終意思決定・利益直結アクションの採択
      - CFO (最高財務・分析責任者): 残高・売上・PV・スキ数・GitHub利用数の冷徹な数値監査
      - CRO (最高収益・成約率責任者): 決済ページ(note ¥980)・Web導線・固定購入バー等の成約率(CVR)改善
      - CMO (最高集客・SNS・動画責任者): note無料記事・X(140字厳守)・YouTubeショート自動投稿による集客最大化
      - CTO/QA (最高技術・品質責任者): 全27ページ＆note記事の即時改修・E2E無欠陥保証
    """

    def __init__(self):
        os.makedirs(BOARD_DIR, exist_ok=True)

    def _load_diagnostic_context(self, day: int, detected_issues: list[str] | None = None) -> tuple[list[str], str]:
        issues = list(detected_issues) if detected_issues else []
        if not issues:
            qa_path = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "qa_health_report.json")
            if os.path.exists(qa_path):
                try:
                    with open(qa_path, "r", encoding="utf-8") as f:
                        qa_data = json.loads(f.read())
                    issues = qa_data.get("detected_issues", [])
                except Exception:
                    pass
        if not issues:
            issues = ["【自己診断】技術エラー0件。アクセス・スキ数から有料決済（¥980）への転換率改善が最優先課題。"]

        prev_summary = "（初回または前回記録なし）"
        try:
            prev_files = sorted(
                [fn for fn in os.listdir(BOARD_DIR) if fn.startswith("day") and fn.endswith("_meeting.json")],
                key=lambda x: int(re.sub(r"\D", "", x) or 0),
            )
            for fn in reversed(prev_files):
                d_num = int(re.sub(r"\D", "", fn) or 0)
                if d_num < day:
                    with open(os.path.join(BOARD_DIR, fn), "r", encoding="utf-8") as f:
                        pdata = json.loads(f.read())
                    prev_summary = f"Day {d_num} 議題: {pdata.get('agenda', '')} / ゴール: {pdata.get('ceo_final_decision', {}).get('primary_goal', '')}"
                    break
        except Exception:
            pass

        return issues, prev_summary

    def _load_market_needs_context(self, research_report: dict | None = None) -> tuple[str, list[str], list[dict]]:
        """市場ニーズ調査（live_market_needs.json または research_report）から上位需要TOP3と新規事業シーズを取得する。"""
        radar = (research_report or {}).get("live_needs_radar") or {}
        if not radar:
            needs_path = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "live_market_needs.json")
            if os.path.exists(needs_path):
                try:
                    with open(needs_path, "r", encoding="utf-8") as f:
                        radar = json.loads(f.read())
                except Exception:
                    radar = {}
        summary = radar.get("market_summary", "実測スキ・外部トレンドから業務自動化テンプレートの需要を継続計測中。")
        top_winners = radar.get("top_winner_niches") or (research_report or {}).get("top_winner_niches") or []
        top_titles = [w.get("title", "") for w in top_winners[:3] if w.get("title")]
        seeds = radar.get("new_business_seeds") or (research_report or {}).get("new_business_seeds") or []
        return summary, top_titles, seeds

    def _call_llm_board_debate(
        self,
        day: int,
        balance: int,
        total_revenue: int,
        price_jpy: int,
        total_notes: int,
        total_likes: int,
        paid_likes: int,
        gh_clones: int,
        gh_uniques: int,
        latest_note_title: str,
        detected_issues: list[str] | None = None,
        prev_summary: str = "",
        needs_summary: str = "",
        top_need_titles: list[str] | None = None,
    ) -> dict | None:
        """OpenAI gpt-4o-mini (またはフォールバックとしてGemini) を使い、実測値と市場ニーズ・専門AI社員の観点をもとに5人のAI役員が議論・意思決定する。"""
        issues_bullet = "\n".join(f"- {iss}" for iss in (detected_issues or []))
        top_needs_str = " / ".join(top_need_titles or []) or "EC在庫管理 / 補助金・事業計画 / 採用スクリーニング"
        prompt = f"""あなたは「90日間・初期資金15,000円・人間介入ゼロのAI起業対決」を戦う自律AI企業組織の会議シミュレーターです。
組織の唯一の目的は「1円でも早く、1円でも多くの実売上・純利益を生み出すこと」です。人間に許可を求めたり確認したりせず、AIエージェント自身で問題点を見つけ、考え、決め、実行命令を下してください。

【本日の実測データ (Day {day} / 90)】
- 軍資金残高: ¥{balance:,}（累計売上: ¥{total_revenue:,}）
- 有料商品（全50種プロンプト＆GAS完全版パック）の現在価格: 先着10部限定 ¥{price_jpy:,}（通常¥1,980から50%OFF、無料試し読み1万字・実物2本公開中）
- GitHub無料Webツール＆プログラム利用数(直近14日): {gh_clones}回（ユニーク {gh_uniques}名）
- note公開済み記事数: {total_notes}本 / アカウント累計スキ: {total_likes}件（うち有料記事スキ: {paid_likes}件）
- 最新公開した無料記事タイトル: {latest_note_title}

【世の中のニーズ調査＆反響ランキング（専門AI社員レポート）】
- 市場調査サマリー: {needs_summary}
- 今もっとも求められている需要TOP3（選択と集中先）: {top_needs_str}
- 稼働中の専門AI社員（4名）: 🔍市場ニーズ調査AI / 🎯セールスコピー改善AI / 💎LTV・商品階段設計AI / 🚀新規事業開発AI（第1事業黒字化と並行し第2・第3の柱を検証中）

【システム自己診断（QA自動点検）で検出された現在の問題点・課題】
{issues_bullet}

【前回の役員会議の記録（同じ議論の繰り返しは厳禁・必ず一歩進んだ具体策を出すこと）】
- {prev_summary}

【重要ブランド方針（人間心理・信頼性の厳守）】
- 顧客向けのnote記事・noteプロフィール・Webサイト（全27ページ）には、「AI起業対決」「実験ログ」「初売上突破のため」といった売り手都合・実験台感のある言葉を一切出さず、実務家にとっての実用性・信頼感・時間短縮メリットだけを訴求すること。
- 「AI起業対決」の企画ストーリー発信は、集客チャネルである X（旧Twitter）と YouTubeショートのみに限定すること。

【出力要件】
以下の5名の役員エージェントが、上記の実測数値・世の中のニーズ調査（TOP3）・専門AI社員レポート・自己診断課題を踏まえて、選択と集中（売れない案をやめ当たりに集中）や商品の階段（無料→¥980→上位設計）も含め、本日即座に実行する改善策を会議で決定してください。専門用語・プログラミング用語は避け、ビジネス視点で具体的に記述してください。

必ず以下のキーを持つJSONオブジェクトのみを返してください（日本語）:
{{
  "agenda": "本日の役員会議の議題（1文・50文字以内）",
  "cfo_statement": "CFO（最高財務・データ分析責任者）の発言（実測数値と需要TOP3の冷徹な監査・選択と集中の指摘・120〜180文字）",
  "cro_statement": "CRO（最高収益・成約率改善責任者）の発言（需要TOP3訴求と3段階商品の階段で¥{price_jpy:,}決済へ繋げる具体策・140〜200文字）",
  "cmo_statement": "CMO（最高集客・SNS・ショート動画責任者）の発言（note無料記事・X140字投稿・YouTubeショートによる集客拡大策・140〜200文字）",
  "cto_statement": "CTO/QA（最高技術・品質保証責任者）の発言（会議決定のWebサイト・LP即時反映と自己修復・E2E品質保証宣言・120〜180文字）",
  "primary_goal": "AI社長（CEO）が決断した本日の最優先ゴール（1文）",
  "approved_actions": [
    "【CRO/ニーズ反映】本日即実行する需要TOP3集中＆商品階段オファー改善アクション1",
    "【CRO/CMO実装】本日即実行するnote・Web導線改善アクション2",
    "【CMO実装】本日即実行するX・ショート動画集客アクション3",
    "【CTO/進化エンジン実装】本日即実行するサイト即時反映・AI組織進化アクション4"
  ],
  "kpi_target": "次期達成ターゲット（noteスキ数、GitHub利用数、初決済の数値目標）"
}}"""

        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        if openai_key:
            try:
                body = json.dumps({
                    "model": "gpt-4o-mini",
                    "response_format": {"type": "json_object"},
                    "temperature": 0.4,
                    "messages": [
                        {
                            "role": "system",
                            "content": "あなたは利益創出を唯一の目的とする自律型AI役員会議エンジンです。必ず指定されたJSON形式のみで回答してください。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    data=body,
                    headers={
                        "Authorization": f"Bearer {openai_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                content = payload["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                required = (
                    "agenda",
                    "cfo_statement",
                    "cro_statement",
                    "cmo_statement",
                    "cto_statement",
                    "primary_goal",
                    "approved_actions",
                    "kpi_target",
                )
                if all(k in parsed for k in required) and isinstance(parsed["approved_actions"], list) and len(parsed["approved_actions"]) >= 4:
                    parsed["_engine"] = "LLM_MULTI_AGENT (gpt-4o-mini)"
                    return parsed
            except Exception as e:
                print(f"[ExecutiveBoard] OpenAI call warning (falling back): {e}")

        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if gemini_key:
            candidate_models = [
                "gemini-3-flash-preview",
                "gemma-4-31b-it",
                "gemma-4-26b-a4b-it",
                "gemini-3.1-flash-lite",
            ]
            for model_name in candidate_models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                    body = json.dumps({
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.4,
                        },
                    }).encode("utf-8")
                    req = urllib.request.Request(
                        url,
                        data=body,
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=45) as resp:
                        payload = json.loads(resp.read().decode("utf-8"))
                    parts = payload["candidates"][0]["content"]["parts"]
                    content = "".join(p.get("text", "") for p in parts if not p.get("thought")) or parts[-1].get("text", "")
                    match = re.search(r"\{.*\}", content, re.S)
                    if match:
                        parsed = json.loads(match.group(0))
                        required = (
                            "agenda",
                            "cfo_statement",
                            "cro_statement",
                            "cmo_statement",
                            "cto_statement",
                            "primary_goal",
                            "approved_actions",
                            "kpi_target",
                        )
                        if all(k in parsed for k in required) and isinstance(parsed["approved_actions"], list) and len(parsed["approved_actions"]) >= 4:
                            parsed["_engine"] = f"LLM_MULTI_AGENT ({model_name})"
                            print(f"[ExecutiveBoard] Successfully held AI board meeting using {model_name}")
                            return parsed
                except Exception as e:
                    print(f"[ExecutiveBoard] Gemini ({model_name}) call warning: {e}")

        return None

    def hold_daily_profit_board_meeting(
        self,
        day: int,
        balance: int,
        total_revenue: int,
        price_jpy: int,
        total_notes: int,
        total_likes: int,
        paid_likes: int,
        gh_clones: int,
        gh_uniques: int,
        latest_note_url: str,
        latest_note_title: str,
        detected_issues: list[str] | None = None,
        research_report: dict | None = None,
    ) -> dict:
        timestamp = datetime.now().astimezone().isoformat()
        issues_list, prev_summary = self._load_diagnostic_context(day, detected_issues)
        needs_summary, top_need_titles, new_business_seeds = self._load_market_needs_context(research_report)

        llm_result = self._call_llm_board_debate(
            day=day,
            balance=balance,
            total_revenue=total_revenue,
            price_jpy=price_jpy,
            total_notes=total_notes,
            total_likes=total_likes,
            paid_likes=paid_likes,
            gh_clones=gh_clones,
            gh_uniques=gh_uniques,
            latest_note_title=latest_note_title,
            detected_issues=issues_list,
            prev_summary=prev_summary,
            needs_summary=needs_summary,
            top_need_titles=top_need_titles,
        )

        if llm_result:
            reasoning_engine = llm_result["_engine"]
            agenda = llm_result["agenda"]
            cfo_statement = llm_result["cfo_statement"]
            cro_statement = llm_result["cro_statement"]
            cmo_statement = llm_result["cmo_statement"]
            cto_statement = llm_result["cto_statement"]
            ceo_decision = {
                "primary_goal": llm_result["primary_goal"],
                "approved_actions": llm_result["approved_actions"][:4],
                "kpi_target": llm_result["kpi_target"],
            }
        else:
            reasoning_engine = "AUTONOMOUS_DATA_DRIVEN_BOARD_ENGINE"
            top1_need = top_need_titles[0] if top_need_titles else "EC・物販の在庫管理＆価格改定自動化"
            agenda = f"売上{total_revenue}円突破へ：需要TOP3（{top1_need[:16]}等）集中×商品階段×サイト即時反映会議"
            cfo_statement = (
                f"【財務・数値監査報告】現在Day {day}、軍資金残高は¥{balance:,}（支出¥0）、累計売上は¥{total_revenue:,}です。"
                f"GitHub利用{gh_clones}回（ユニーク{gh_uniques}名）、note記事{total_notes}本・累計スキ{total_likes}件まで拡大していますが売上が0円です。"
                f"選択と集中として反響の薄いテストを止め、需要スコア上位3テーマへ全リソースを集中すべきです。"
            )
            cro_statement = (
                f"【成約率・商品階段改善】有料note（先着10部¥{price_jpy:,}）について、無料¥0→入門パック¥{price_jpy:,}→上位ビジネス導入設計¥4,980の『3段階商品の階段』をLPへ実装します。"
                f"さらに市場ニーズ調査で選ばれた『{top1_need}』などTOP3をサイト最上部に配置し、顧客が安心して即決できる導線へ改修します。"
            )
            cmo_statement = (
                f"【集客・動画・SNS拡散提案】顧客向けのWebページやnote記事では実用性と信頼感を最優先にし、"
                f"X投稿（140字制限厳守）とYouTubeショートでは『専門AI社員（市場ニーズ調査・セールスコピー・新規事業開発）を追加編成しサイトと商品を毎日自動進化させている過程』を発信して集客を最大化します。"
            )
            cto_statement = (
                f"【技術実装・自己進化報告】本日の会議決定と市場ニーズTOP3を会社進化エンジン経由で全27ページおよびセールスLP（pro-pack.html）へ即時反映し、"
                f"第2・第3の新規事業シーズの検証データも併せて更新・E2E検査0エラーでGitHub Pagesへデプロイします。"
            )
            ceo_decision = {
                "primary_goal": f"需要TOP3集中＆商品階段オファーのサイト即時反映による、先着10部¥{price_jpy:,}初決済達成",
                "approved_actions": [
                    f"【CRO/進化エンジン】市場ニーズTOP3（{top1_need[:18]}等）をトップページ＆LP最上部に昇格し選択と集中を実行",
                    f"【CRO実装】無料¥0 → 限定¥{price_jpy:,} → 上位¥4,980設計の『商品の階段』セクションをLPへ実装",
                    f"【CMO実装】X 140字投稿3パターンとYouTubeショートで本日の組織進化・改善内容を公開",
                    f"【CTO/QA実装】5役員＋4専門AI社員体制でサイト再ビルド・E2E全27URL点検・ルールブック自己更新を自動完了"
                ],
                "kpi_target": f"note累計スキ {total_likes}件 → 25件突破、GitHub利用 {gh_clones}回 → 400回突破、先着10部 ¥{price_jpy:,} の初決済獲得"
            }

        specialist_reports = [
            f"🔍 市場ニーズ調査AI: {needs_summary}",
            "🎯 セールスコピー改善AI: 顧客向け全ページから実験・対決表現を排除しつつ需要TOP3訴求へ差し替え",
            f"💎 LTV・商品階段設計AI: 無料¥0 → 入門完全版¥{price_jpy:,} → 上位ビジネス導入¥4,980の3段階導線を設計",
            f"🚀 新規事業開発AI: 第1事業黒字化と並行し、次期収益の柱（{len(new_business_seeds)}件）の市場検証を進行",
        ]

        meeting_record = {
            "day": day,
            "held_at": timestamp,
            "reasoning_engine": reasoning_engine,
            "Single_Objective": "MAXIMIZE_NET_PROFIT",
            "detected_issues": issues_list,
            "market_needs_summary": needs_summary,
            "top_need_titles": top_need_titles,
            "specialist_reports": specialist_reports,
            "metrics_snapshot": {
                "balance_jpy": balance,
                "total_revenue_jpy": total_revenue,
                "current_price_jpy": price_jpy,
                "total_published_notes": total_notes,
                "total_note_likes": total_likes,
                "paid_note_likes": paid_likes,
                "github_clones_14d": gh_clones,
                "github_unique_users_14d": gh_uniques,
                "latest_note_url": latest_note_url,
            },
            "agenda": agenda,
            "statements": {
                "CFO (最高財務・分析責任者)": cfo_statement,
                "CRO (最高収益・成約率責任者)": cro_statement,
                "CMO (最高集客・SNS・動画責任者)": cmo_statement,
                "CTO/QA (最高技術・品質責任者)": cto_statement,
            },
            "ceo_final_decision": ceo_decision,
        }

        json_path = os.path.join(BOARD_DIR, f"day{day}_meeting.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(meeting_record, f, ensure_ascii=False, indent=2)

        issues_md = "\n".join(f"- {iss}" for iss in issues_list)
        specialists_md = "\n".join(f"- {sp}" for sp in specialist_reports)
        md_content = f"""# 🏢 AI起業対決・利益創出役員会議 議事録（Day {day} / 90）

- **開催日時**: {timestamp}
- **推論エンジン**: `{reasoning_engine}`
- **組織の唯一の目的**: **利益（売上）を出すこと**
- **本日の議題**: {agenda}
- **現在の実測スコア**: 残高 ¥{balance:,} / 売上 ¥{total_revenue:,} / プログラム利用 {gh_clones}回（{gh_uniques}名） / note記事 {total_notes}本（累計スキ {total_likes}件） / 現在価格 **先着10部限定 ¥{price_jpy:,}**

---

## 🔍 専門AI社員レポート ＆ 世の中のニーズ調査
{specialists_md}

---

## 🛠️ システム自己診断（QA自動点検）で検出された課題
{issues_md}

---

## 🗣️ 各役員エージェントの分析と改善提案

### 📊 CFO（最高財務・データ分析責任者）
{cfo_statement}

### 💰 CRO（最高収益・成約率改善責任者）
{cro_statement}

### 📣 CMO（最高集客・SNS・ショート動画責任者）
{cmo_statement}

### 🛠️ CTO/QA（最高技術・品質保証責任者）
{cto_statement}

---

## ⚡ AI社長（CEO）の最終決断と本日即時実行した改善アクション

- **最優先ゴール**: **{ceo_decision['primary_goal']}**
- **本日即時実行された改善リスト**:
  1. {ceo_decision['approved_actions'][0]}
  2. {ceo_decision['approved_actions'][1]}
  3. {ceo_decision['approved_actions'][2]}
  4. {ceo_decision['approved_actions'][3]}
- **次期達成ターゲット**: {ceo_decision['kpi_target']}
"""
        with open(LATEST_BOARD_MD, "w", encoding="utf-8") as f:
            f.write(md_content)
        day_md_path = os.path.join(BOARD_DIR, f"day{day}_meeting.md")
        with open(day_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return meeting_record

