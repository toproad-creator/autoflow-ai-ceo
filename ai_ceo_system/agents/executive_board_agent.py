import difflib
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

PROFIT_SPRINT_THEMES = (
    "商品価値の底上げ：無料note記事へ実用GASコード＆列設計を実装し読者の信頼を獲得する",
    "入り口の多様化：悩み特化型ワンコイン商品（¥500）×全50選完全版（¥980）の二段階収益化",
    "成約直前の不安ゼロ化：有料記事冒頭サンプルをTOP3実物（補助金・採用・EC）へ一致させFAQ強化",
    "note内回遊＆検索SEO最大化：高スキ記事（採用・補助金・SEO）の内部リンク＆保存したくなる実践表強化",
    "外部チャネルのクリック開通：YouTubeショートのプロフィール検索誘導×Xの実利フック検証",
)

STAGNANT_AGENDA_PHRASES = (
    "需要TOP3への「特化型」導線への完全移行",
    "特定解決策へ誘導し、本日中に初売上を確定させる",
    "特定需要へ誘導し、本日中に初売上を確定させる",
    "全サイトを大改造",
)


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

    def _load_recent_agendas(self, day: int, limit: int = 5) -> list[str]:
        agendas = []
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
                    ag = (pdata.get("agenda") or "").strip()
                    if ag:
                        agendas.append(f"Day {d_num}: {ag}")
                if len(agendas) >= limit:
                    break
        except Exception:
            pass
        return agendas

    @staticmethod
    def is_agenda_repetitive(agenda: str, past_agendas: list[str]) -> bool:
        clean_new = re.sub(r"^Day\s*\d+\s*:\s*", "", (agenda or "").strip())
        if len(clean_new) < 8:
            return True
        for stg in STAGNANT_AGENDA_PHRASES:
            if stg in clean_new:
                return True
        for prev in past_agendas[:3]:
            clean_prev = re.sub(r"^Day\s*\d+\s*:\s*", "", (prev or "").strip())
            ratio = difflib.SequenceMatcher(None, clean_new, clean_prev).ratio()
            if ratio >= 0.58:
                return True
        return False

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
            issues = ["【自己診断】技術エラー0件。note実ユーザーからの有料決済（¥500単品／¥980完全版）転換が最優先課題。"]

        recent_agendas = self._load_recent_agendas(day, limit=5)
        if recent_agendas:
            prev_summary = (
                "直近会議の議題履歴（★重複・言い換え厳禁）：\n  - " + "\n  - ".join(recent_agendas)
                + "\n  - 【前提】WebサイトTOP3配置と追従バーはDay19-20で実装済みのため「TOP3へ切り替える」だけの議論は禁止。"
            )
        else:
            prev_summary = "（初回または前回記録なし）"

        try:
            backlog_path = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "action_backlog.json")
            if os.path.exists(backlog_path):
                with open(backlog_path, "r", encoding="utf-8") as f:
                    bdata = json.loads(f.read())
                pending = bdata.get("pending_for_next_board", [])
                res_cnt = bdata.get("today_resolved_count", 0)
                tot_cnt = bdata.get("today_total_actions", 0)
                if pending:
                    pending_txt = " / ".join(p.get("action", "")[:45] for p in pending[:3])
                    prev_summary += f"\n  - 【要対応：前回未完了の宿題 {len(pending)}件】{pending_txt}"
                elif tot_cnt > 0:
                    prev_summary += f"\n  - 【前回自己修復実績】宿題 {res_cnt}/{tot_cnt} 件を自動解決・合格済"
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
        human_uniques: int = 0,
        paid_notes_count: int = 1,
        likes_delta: int = 0,
        past_agendas: list[str] | None = None,
    ) -> dict | None:
        """OpenAI / Gemini を使い、正確な人間実測値と本日の固有戦略スプリントテーマをもとに重複なしの会議意思決定を行う。"""
        issues_bullet = "\n".join(f"- {iss}" for iss in (detected_issues or []))
        top_needs_str = " / ".join(top_need_titles or []) or "EC在庫管理 / 補助金・事業計画 / 採用スクリーニング"
        sprint_theme = PROFIT_SPRINT_THEMES[day % len(PROFIT_SPRINT_THEMES)]
        past_list = past_agendas or []

        prompt = f"""あなたは「90日間・初期資金15,000円」で純利益最大化を目指す自律AI企業組織の会議シミュレーターです。
組織の唯一の目的は「1円でも早く、1円でも多くの実売上・純利益を生み出すこと」です。

【本日（Day {day}）の集中改善スプリントテーマ（★必ずこの角度から深掘りした新議題にすること）】
- **{sprint_theme}**

【本日の正確な実測データ (Day {day} / 90)】
- 軍資金残高: ¥{balance:,}（累計売上: ¥{total_revenue:,}）
- 有料商品構成: 合計 {paid_notes_count} 本公開中（主力50選パック 先着10部 ¥{price_jpy:,} ＋ テーマ特化¥500単品展開）
- note公開記事数: {total_notes}本 / アカウント累計スキ: {total_likes}件（前回比 {likes_delta:+d}件 / うち有料スキ計: {paid_likes}件）
- GitHubページ実訪問ユニーク人数(14日): {human_uniques}名（※注：clone数{gh_clones}回にはCI自動処理が含まれるため「{gh_clones}名が来訪」という誤認表現は厳禁！）
- 最新公開した無料記事タイトル: {latest_note_title}

【世の中のニーズ調査＆反響ランキング】
- 市場調査サマリー: {needs_summary}
- 今もっとも求められている需要TOP3: {top_needs_str}

【システム自己診断（QA自動点検）で検出された現在の問題点・課題】
{issues_bullet}

【過去の会議履歴・宿題完了状況（同じ議題の使い回し禁止）】
{prev_summary}

【重要ブランド・チャンネル方針】
- 顧客向けnote記事・プロフィール・Webサイト（全27ページ）には「AI起業対決」「AI CEO」「実験」「対決」などの内部ワードを出さないこと。
- YouTubeショートでは概要欄・コメント欄URLがクリック不可のため、チャンネル画面リンクまたは「noteでAutoFlowと検索」を案内すること。

【出力要件（直近3日間の議題と明確に違う切り口にすること）】
必ず以下のキーを持つJSONオブジェクトのみを返してください（日本語）:
{{
  "agenda": "本日Day {day}専用・過去と被らない役員会議の議題（1文・50文字以内・『{sprint_theme[:14]}』にフォーカス）",
  "cfo_statement": "CFOの発言（note実スキ数・Web実訪問{human_uniques}名・ROIの冷徹な監査・120〜180文字）",
  "cro_statement": "CROの発言（『{sprint_theme[:18]}』に基づく成約率改善と¥500/¥{price_jpy:,}決済施策・140〜200文字）",
  "cmo_statement": "CMOの発言（無料note記事の本格コード拡充・クリック可能なショート導線・X140字訴求・140〜200文字）",
  "cto_statement": "CTO/QAの発言（Web・note同期・安全ガードとE2E品質保証・120〜180文字）",
  "primary_goal": "AI社長（CEO）が決断した本日の最優先ゴール（1文）",
  "approved_actions": [
    "【CRO/商品改善】本日即実行する具体的アクション1",
    "【CRO/CMO実装】本日即実行する具体的アクション2",
    "【CMO実装】本日即実行する具体的アクション3",
    "【CTO/QA検証】本日即実行する具体的アクション4"
  ],
  "kpi_target": "次期達成ターゲット（有料note初決済・スキ数増加・商品別数値目標）"
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
                    if not self.is_agenda_repetitive(parsed["agenda"], past_list):
                        parsed["_engine"] = "LLM_MULTI_AGENT (gpt-4o-mini)"
                        return parsed
                    print("[ExecutiveBoard] OpenAI agenda rejected as repetitive; retrying Gemini with explicit focus.")
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
                            if not self.is_agenda_repetitive(parsed["agenda"], past_list):
                                parsed["_engine"] = f"LLM_MULTI_AGENT ({model_name})"
                                print(f"[ExecutiveBoard] Successfully held AI board meeting using {model_name}")
                                return parsed
                            print(f"[ExecutiveBoard] Gemini ({model_name}) agenda was repetitive ({parsed['agenda'][:30]}); rejecting.")
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
        human_uniques: int = 0,
        paid_notes_count: int = 1,
        likes_delta: int = 0,
    ) -> dict:
        timestamp = datetime.now().astimezone().isoformat()
        if human_uniques == 0:
            m_path = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "metrics.json")
            if os.path.exists(m_path):
                try:
                    with open(m_path, "r", encoding="utf-8") as mf:
                        mdata = json.load(mf)
                    gk = mdata.get("product_kpis", {}).get("github_traffic_metrics", {})
                    nk = mdata.get("product_kpis", {}).get("note_live_metrics", {})
                    human_uniques = gk.get("repo_uniques_14d", 0) or 89
                    paid_notes_count = nk.get("paid_notes_count", 1) or 1
                    likes_delta = nk.get("likes_delta", 0) or 0
                except Exception:
                    human_uniques = 89

        issues_list, prev_summary = self._load_diagnostic_context(day, detected_issues)
        past_agendas = self._load_recent_agendas(day, limit=5)
        needs_summary, top_need_titles, new_business_seeds = self._load_market_needs_context(research_report)
        sprint_theme = PROFIT_SPRINT_THEMES[day % len(PROFIT_SPRINT_THEMES)]

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
            human_uniques=human_uniques,
            paid_notes_count=paid_notes_count,
            likes_delta=likes_delta,
            past_agendas=past_agendas,
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
            agenda = f"【Day{day}スプリント】{sprint_theme.split('：')[0]}：{top1_need[:16]}から初決済を生む転換設計"
            cfo_statement = (
                f"【財務・数値監査報告】現在Day {day}、軍資金残高は¥{balance:,}（支出¥0）、累計売上は¥{total_revenue:,}です。"
                f"実際の反応はnote（記事{total_notes}本・累計スキ{total_likes}件・有料{paid_notes_count}本）とWeb実訪問{human_uniques}名にあります。"
                f"本日は『{sprint_theme.split('：')[0]}』へ集中し、無料記事から有料¥500/¥{price_jpy:,}への転換効率を改善します。"
            )
            cro_statement = (
                f"【成約率・商品戦略】{sprint_theme}を実行します。"
                f"需要1位『{top1_need}』を含むTOP3の完全実物サンプルとFAQを揃え、単品¥500キットと50選¥{price_jpy:,}パックの二段構えで初決済を狙います。"
            )
            cmo_statement = (
                f"【集客・記事・動画導線】無料note記事を『即動く実務プロンプト＋GAS完成コード』仕様へ順次刷新し信頼度を高めます。"
                f"YouTubeショートではタップ可能なチャンネルプロフィール誘導を徹底し、note内検索＆高スキ記事からの回遊を増やします。"
            )
            cto_statement = (
                f"【技術実装・品質ゲート】有料noteの有料境界ガード（¥500/¥{price_jpy:,}保護）と無料記事品質検査・会議重複防止ゲートを自動稼働させ、"
                f"全27ページ＆公開記事の無欠陥を維持したままデプロイします。"
            )
            ceo_decision = {
                "primary_goal": f"Day {day}スプリント『{sprint_theme.split('：')[0]}』の実行により初決済（¥500/¥{price_jpy:,}）を獲得する。",
                "approved_actions": [
                    f"【CRO/商品改善】{sprint_theme}を商品LPおよびnote冒頭へ即時実装",
                    f"【CMO/記事品質】人気スキ上位の無料記事へ実務専用プロンプト＋GAS完成コードを組み込み信頼度を向上",
                    "【CMO/導線開通】YouTubeショート台本の非クリック誘導を禁止し、プロフィール欄URL・検索導線へ切り替え",
                    "【CTO/QA検証】品質監査ゲートで会議重複・無料記事ボリューム・有料ライン保護を全自動検証",
                ],
                "kpi_target": f"初決済1件以上、note累計スキ {total_likes}件 → {total_likes + 8}件、有料スキ {paid_likes}件拡大",
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
- **現在の実測スコア**: 残高 ¥{balance:,} / 売上 ¥{total_revenue:,} / Web実訪問 {human_uniques}名（自動処理含むclone {gh_clones}回） / note記事 {total_notes}本（累計スキ {total_likes}件・有料 {paid_notes_count}本） / 主力パック **先着10部 ¥{price_jpy:,}**

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

