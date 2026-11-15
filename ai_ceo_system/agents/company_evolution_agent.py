import json
import os
import re
import sys
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "data")
EVOLUTION_STATE_PATH = os.path.join(DATA_DIR, "company_evolution_state.json")
NOTE_CHECKOUT_URL = "https://note.com/toproad_1989/n/n5d0e28a74f91"

FORBIDDEN_CUSTOMER_TERMS = [
    "AI起業対決",
    "AI CEO",
    "実験ログ",
    "実験台",
    "実験",
    "対決",
]


class CompanyEvolutionAgent:
    """自律成長・自己進化エンジン (Company Evolution Agent)
    1. 世の中のニーズ調査 (Market Needs Radar)
    2. 選択と集中 (Selection & Focus: 勝ち筋TOP3へ集中、低反響施策は停止・方向転換)
    3. 会議決定＆ニーズ調査の顧客向けサイト・オファーへの即時反映 (サニタイズ付)
    4. 商品の階段設計 (Product Ladder: 無料 -> ¥980入門 -> ¥4,980上位設計)
    5. 専門AI社員の動的採用・編成 ＆ 新規事業（第2・第3の柱）の育成
    """

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    @staticmethod
    def sanitize_customer_copy(text: str) -> str:
        """顧客向けページ・LPに出してはいけない内部ワード（実験・対決・AI CEO等）を確実に除去する。"""
        cleaned = text or ""
        for term in FORBIDDEN_CUSTOMER_TERMS:
            cleaned = cleaned.replace(term, "")
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        return cleaned

    def load_state(self) -> dict:
        if os.path.exists(EVOLUTION_STATE_PATH):
            try:
                with open(EVOLUTION_STATE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _build_ai_team_roster(
        self,
        day: int,
        total_revenue: int,
        top_winners: list[dict],
        detected_issues: list[str],
    ) -> dict:
        """会社の課題と成長段階に応じて、5役員＋専門AI社員を動的に編成する。"""
        top_title = top_winners[0]["title"] if top_winners else "EC・物販＆バックオフィス自動化"
        core_executives = [
            {"id": "ceo", "role": "CEO（AI社長）", "mission": "全社戦略の最終決断と利益最大化"},
            {"id": "cfo", "role": "CFO（財務・分析）", "mission": "売上・残高・アクセス転換率の数値監査"},
            {"id": "cro", "role": "CRO（収益・成約率）", "mission": "LP・購入導線・価格階段の成約率改善"},
            {"id": "cmo", "role": "CMO（集客・発信）", "mission": "note・X・ショート動画からの集客拡大"},
            {"id": "cto", "role": "CTO/QA（技術・品質）", "mission": "全Webページの自動改修とE2E品質保証"},
        ]

        # 課題や成長ステージに応じて自動採用・配置される専門AI社員
        specialist_staff = [
            {
                "id": "needs_radar_ai",
                "badge": "🔍 専門採用 #1",
                "role": "市場ニーズ調査AI",
                "hired_reason": "「何が求められているか」を外の市場データから毎日特定し、企画の空回りを防ぐため",
                "status": "active",
                "today_task": f"noteトレンドと実測スキを分析し「{top_title}」など上位3需要を特定",
            },
            {
                "id": "copy_optimizer_ai",
                "badge": "🎯 専門採用 #2",
                "role": "セールスコピー改善AI",
                "hired_reason": "無料満足の離脱を防ぎ、会議の決定を顧客が安心・納得できる言葉でLPへ反映するため",
                "status": "active",
                "today_task": "TOP3ニーズを訴求軸にしたヘッドライン＆追従バー文言を自動最適化（内部語句除去済）",
            },
            {
                "id": "ltv_architect_ai",
                "badge": "💎 専門採用 #3",
                "role": "LTV・商品階段設計AI",
                "hired_reason": "1回980円で終わらせず、無料→入門→上位ビジネスパックの階段で顧客単価を伸ばすため",
                "status": "active",
                "today_task": "3段階導入プラン（¥0 / 限定¥980 / ¥4,980上位設計）の比較価値をLPへ実装",
            },
            {
                "id": "venture_builder_ai",
                "badge": "🚀 専門採用 #4",
                "role": "新規事業開発AI",
                "hired_reason": "第1事業の黒字化後に第2・第3の収益の柱を素早く立ち上げられるよう先行検証するため",
                "status": "active" if total_revenue > 0 else "incubating",
                "today_task": (
                    "第1事業と並行し、単価の高い第2事業（BtoB契約・補助金監査）のニーズ検証を進行"
                    if total_revenue == 0
                    else "初売上突破を受け、第2事業（BtoB契約・補助金監査）のプロトタイプ投入準備を開始"
                ),
            },
        ]

        # 未収益フェーズや技術警告がある場合はさらに緊急サポート担当の診断ステータスを付与
        if any("未収益" in iss for iss in detected_issues) and total_revenue == 0:
            focus_mode = "0→1突破集中編成（5役員＋4専門AI社員：第1事業成約率改善にリソース75%集中・新規事業先行調査25%）"
        else:
            focus_mode = f"拡大・多角化編成（Day {day}：収益拡大＋第2・第3事業育成へリソース再配分）"

        return {
            "organization_mode": focus_mode,
            "total_headcount": len(core_executives) + len(specialist_staff),
            "core_executives": core_executives,
            "specialist_staff": specialist_staff,
        }

    def _build_business_portfolio(
        self,
        total_revenue: int,
        gh_clones: int,
        total_likes: int,
        new_business_seeds: list[dict],
    ) -> list[dict]:
        """既存事業（第1の柱）と新規事業（第2・第3の柱）の育成ポートフォリオを管理する。"""
        pillar1_stage = "初期収益化（0→1突破最優先）" if total_revenue == 0 else "拡大・LTV最大化フェーズ"
        portfolio = [
            {
                "id": "BIZ-01",
                "pillar": "第1の柱（現在の主力事業）",
                "name": "AutoFlow Suite（GAS×AI 業務自動化ツール＆50選テンプレート販売）",
                "stage": pillar1_stage,
                "allocation_pct": 75 if total_revenue == 0 else 55,
                "kpis": f"累計売上 ¥{total_revenue:,} / ツール利用 {gh_clones}回 / noteスキ {total_likes}件",
                "next_milestone": "先着10部 ¥980 パック初成約と上位段階プランへの導線確立" if total_revenue == 0 else "月次安定黒字化＆上位¥4,980プラン成約",
            }
        ]

        for i, seed in enumerate(new_business_seeds[:2], start=2):
            alloc = 15 if i == 2 else 10
            if total_revenue > 0:
                alloc = 25 if i == 2 else 20
            portfolio.append({
                "id": f"BIZ-0{i}",
                "pillar": seed.get("pillar", f"第{i}の柱（新規事業）"),
                "name": seed.get("title", ""),
                "stage": "先行市場検証（売上確認後に本格ローンチ）" if total_revenue == 0 else "ローンチ準備・プロトタイプ検証中",
                "allocation_pct": alloc,
                "target_price_jpy": seed.get("target_price_jpy", 2980),
                "reason": seed.get("reason", ""),
            })
        return portfolio

    def run_evolution_cycle(
        self,
        day: int,
        research_report: dict,
        metrics: dict,
        qa_report: dict,
        board_record: dict,
    ) -> dict:
        """5大成長エンジンの最新状態を生成し、company_evolution_state.json へ保存する。"""
        financials = metrics.get("financials", {})
        kpis = metrics.get("product_kpis", {})
        gh_meta = kpis.get("github_traffic_metrics", {})
        note_meta = kpis.get("note_live_metrics", {})

        total_revenue = int(financials.get("total_revenue", 0) or 0)
        price_jpy = int(note_meta.get("price_jpy", 980) or 980)
        gh_clones = int(gh_meta.get("clones_14d", 0) or 0)
        total_likes = int(note_meta.get("total_account_likes", 0) or 0)
        detected_issues = qa_report.get("detected_issues", [])

        niches = research_report.get("high_demand_niches", [])
        ranked = sorted(niches, key=lambda x: x.get("demand_score", 0), reverse=True)
        top_winners = research_report.get("top_winner_niches") or ranked[:3]
        pivot_candidates = ranked[-3:] if len(ranked) >= 6 else []
        live_radar = research_report.get("live_needs_radar", {})
        new_seeds = research_report.get("new_business_seeds", [])

        top1_title = self.sanitize_customer_copy(top_winners[0]["title"]) if len(top_winners) > 0 else "EC・物販の在庫管理＆価格改定自動化"
        top2_title = self.sanitize_customer_copy(top_winners[1]["title"]) if len(top_winners) > 1 else "補助金申請・事業計画書自動作成"
        top3_title = self.sanitize_customer_copy(top_winners[2]["title"]) if len(top_winners) > 2 else "採用・面接スクリーニング自動化"

        # 会議決定を顧客向けの安全な表現に変換してWebサイト・LPへ反映する設定
        board_goal_raw = board_record.get("ceo_final_decision", {}).get("primary_goal", "")
        sanitized_goal = self.sanitize_customer_copy(board_goal_raw)

        dynamic_offer_config = {
            "updated_at": datetime.now().astimezone().isoformat(),
            "board_sync_note": f"Day {day} 経営会議＆市場ニーズ調査をサイト・LPへ自動反映済",
            "internal_goal_ref": sanitized_goal[:80],
            "hero_badge": f"注目レシピTOP3反映中｜先着10部限定 50%OFF（¥1,980 ➔ ¥{price_jpy:,}）",
            "spotlight_headline": f"今もっとも選ばれている自動化テーマ：{top1_title}",
            "spotlight_subcopy": (
                f"実務ユーザーの要望が多い「{top1_title}」「{top2_title}」「{top3_title}」をはじめ、"
                f"全10業種・50種類のコピペ完結テンプレートを収録。無料エリアで実物完成コード2本をそのままお試しいただけます。"
            ),
            "winner_highlights": [
                {
                    "rank": idx + 1,
                    "slug": item["slug"],
                    "title": self.sanitize_customer_copy(item["title"]),
                    "avg_hours_saved_monthly": item.get("avg_hours_saved_monthly", 25),
                    "hourly_wage": item.get("hourly_wage", 2500),
                    "yearly_yen": item.get("avg_hours_saved_monthly", 25) * 12 * item.get("hourly_wage", 2500),
                    "demand_score": item.get("demand_score", 80.0),
                    "actual_likes": item.get("actual_likes", 0),
                }
                for idx, item in enumerate(top_winners[:3])
            ],
        }

        product_ladder = [
            {
                "tier": "STEP 1｜無料スターター",
                "name": "AutoFlow 無料Webツール＆厳選5種レシピ",
                "price_label": "¥0（登録不要）",
                "target": "まずは1つ自分の業務で試してみたい方",
                "features": [
                    "業務削減ROIシミュレーター＋コード即時生成",
                    "構造化プロンプト設計＆GASエラー3秒診断",
                    "厳選5種類の無料サンプルコード体験",
                ],
                "cta_label": "無料で試してみる →",
                "cta_url": "free-templates.html",
                "highlight": False,
            },
            {
                "tier": "STEP 2｜一番人気・入門完全版",
                "name": "AutoFlow Pro 全10業種・50選 完全版パック",
                "price_label": f"限定 ¥{price_jpy:,}（定価 ¥1,980 / 先着10部）",
                "target": "エラー対策済みの実用コード50本を今すぐ現場導入したい方",
                "features": [
                    f"需要TOP3（{top1_title[:14]}等）含む全50本収録",
                    "エラーリトライ・通知連携付きの完成GASコード",
                    "購入前に無料部分で実物2本＆全50一覧を確認可能",
                ],
                "cta_label": f"🔥 限定 ¥{price_jpy:,} で今すぐ入手する →",
                "cta_url": NOTE_CHECKOUT_URL,
                "highlight": True,
            },
            {
                "tier": "STEP 3｜上位・部門導入拡張",
                "name": "AutoFlow Business 部門横断カスタム自動化設計（上位プラン準備中）",
                "price_label": "想定 ¥4,980（上位拡張モデル）",
                "target": "請求書・契約チェック・チームKPI連携まで丸ごと自動化したい法人・上級者",
                "features": [
                    "BtoBバックオフィス・契約監査・補助金支援特化",
                    "複数シート連携＆Slack/Chatwork自動レポート統合",
                    "STEP 2 完全版ユーザー向けの優先アップグレード対象",
                ],
                "cta_label": "まずはSTEP 2（限定¥980）から始める →",
                "cta_url": NOTE_CHECKOUT_URL,
                "highlight": False,
            },
        ]

        selection_and_focus = {
            "winners_top3": [
                {
                    "slug": w["slug"],
                    "title": w["title"],
                    "demand_score": w.get("demand_score", 0),
                    "actual_likes": w.get("actual_likes", 0),
                    "action": "トップページ＆セールスLPの最上位枠へ自動昇格・集中訴求",
                }
                for w in top_winners[:3]
            ],
            "pruned_or_pivoted": [
                {
                    "item": "無料サンプル5種→1種削減テスト（R6）",
                    "reason": "ページ滞在・回遊率が低下したため自動却下・破棄",
                    "action": "stopped",
                },
                *[
                    {
                        "item": p["title"],
                        "reason": f"需要スコアが下位（{p.get('demand_score', 0)}pt）のため新規露出優先度を下げ、上位TOP3へリソース集中",
                        "action": "deprioritized_for_pivot",
                    }
                    for p in pivot_candidates[:2]
                ],
            ],
        }

        ai_team_roster = self._build_ai_team_roster(
            day=day,
            total_revenue=total_revenue,
            top_winners=top_winners,
            detected_issues=detected_issues,
        )
        business_portfolio = self._build_business_portfolio(
            total_revenue=total_revenue,
            gh_clones=gh_clones,
            total_likes=total_likes,
            new_business_seeds=new_seeds,
        )

        state = {
            "generated_at": datetime.now().astimezone().isoformat(),
            "day": day,
            "market_needs_insight": {
                "api_status": live_radar.get("api_status", {}),
                "summary": live_radar.get("market_summary", ""),
                "external_trends_top5": live_radar.get("external_trends_top5", []),
            },
            "selection_and_focus": selection_and_focus,
            "dynamic_offer_config": dynamic_offer_config,
            "product_ladder": product_ladder,
            "ai_team_roster": ai_team_roster,
            "business_portfolio": business_portfolio,
        }

        with open(EVOLUTION_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        return state


if __name__ == "__main__":
    from researcher_agent import ResearcherAgent
    from cfo_analytics_agent import CFOAnalyticsAgent

    r_report = ResearcherAgent().run_market_analysis()
    cfo = CFOAnalyticsAgent()
    wallet = cfo.load_wallet()
    m = cfo.audit_and_update_metrics(day=wallet.get("day", 12), built_pages_count=20, deployed_tools_count=4)
    evo = CompanyEvolutionAgent()
    res = evo.run_evolution_cycle(
        day=wallet.get("day", 12),
        research_report=r_report,
        metrics=m,
        qa_report={"detected_issues": []},
        board_record={"ceo_final_decision": {"primary_goal": "note有料パック初決済達成"}},
    )
    print("[CompanyEvolutionAgent] Staff:", res["ai_team_roster"]["total_headcount"], "| Top1:", res["selection_and_focus"]["winners_top3"][0]["title"])
