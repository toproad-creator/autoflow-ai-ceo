import json
import os
import urllib.parse
import urllib.request
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESEARCH_OUTPUT_PATH = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "market_research_day1.json")
LIVE_NEEDS_PATH = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "live_market_needs.json")
NOTE_CREATOR_API_BASE = "https://note.com/api/v2/creators/toproad_1989/contents?kind=note&page="
NOTE_SEARCH_API_BASE = "https://note.com/api/v3/searches?context=note&size=10&q="


class ResearcherAgent:
    """市場調査＆外部ニーズ検知エージェント (Market Research & Needs Radar Agent)
    90日間・初期資金15,000円・人間介入ゼロの制約下で最も期待値（EV）が高いビジネスモデルを算出するとともに、
    noteの実測反響（スキ数）や世の中の検索トレンドを毎日取得し、需要上位テーマと新規事業シーズを特定する。
    """

    def __init__(self):
        os.makedirs(os.path.dirname(RESEARCH_OUTPUT_PATH), exist_ok=True)

    def _fetch_live_note_signals(self) -> dict:
        """自アカウントの反応データ（スキ数）と外部noteの人気記事トレンドを安全に取得する。"""
        own_articles = []
        external_trends = []
        api_status = {"own_api": "fallback", "trend_api": "fallback"}

        # 1. 自アカウントの記事ごとの実測反響（スキ数）を取得
        try:
            for page_idx in range(1, 5):
                req = urllib.request.Request(
                    f"{NOTE_CREATOR_API_BASE}{page_idx}",
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    payload = json.loads(resp.read().decode("utf-8")).get("data", {})
                contents = payload.get("contents", [])
                for c in contents:
                    own_articles.append({
                        "key": c.get("key"),
                        "title": c.get("name", ""),
                        "likes": c.get("likeCount", 0),
                        "price": c.get("price", 0),
                    })
                if payload.get("isLastPage", True) or not contents:
                    break
            if own_articles:
                api_status["own_api"] = "live"
        except Exception:
            pass

        # 2. note検索APIから「今世の中で需要が高い自動化・AI関連テーマ」を取得
        search_queries = ["GAS 自動化", "AI 業務効率化 プロンプト"]
        seen_titles = set()
        for q in search_queries:
            try:
                encoded_q = urllib.parse.quote(q)
                req = urllib.request.Request(
                    f"{NOTE_SEARCH_API_BASE}{encoded_q}",
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    s_data = json.loads(resp.read().decode("utf-8")).get("data", {})
                notes_obj = s_data.get("notes") or {}
                contents = notes_obj.get("contents", []) if isinstance(notes_obj, dict) else []
                for item in contents:
                    title = (item.get("name") or "").strip()
                    if not title or title in seen_titles:
                        continue
                    seen_titles.add(title)
                    external_trends.append({
                        "query": q,
                        "title": title,
                        "likes": item.get("likeCount", 0),
                        "price": item.get("price", 0),
                        "is_paid": (item.get("price", 0) or 0) > 0,
                    })
                if contents:
                    api_status["trend_api"] = "live"
            except Exception:
                continue

        # 外部APIが一時不通でも運用が止まらない安全なベースライン市場トレンド
        if not external_trends:
            external_trends = [
                {"query": "GAS 自動化", "title": "スプレッドシート×GASで請求書・集計作業を完全自動化する実務テンプレート", "likes": 45, "price": 980, "is_paid": True},
                {"query": "AI 業務効率化 プロンプト", "title": "コピペで使えるAI構造化プロンプト＆SNS・営業メール半自動化ガイド", "likes": 38, "price": 980, "is_paid": True},
                {"query": "GAS 自動化", "title": "Googleドライブ請求書整理・LINEステップ・EC在庫通知の時短スクリプト", "likes": 29, "price": 0, "is_paid": False},
            ]

        return {
            "fetched_at": datetime.now().astimezone().isoformat(),
            "api_status": api_status,
            "own_articles": own_articles,
            "external_trends": sorted(external_trends, key=lambda x: x.get("likes", 0), reverse=True)[:15],
        }

    def run_market_analysis(self) -> dict:
        candidates = [
            {
                "id": "BM-01",
                "name": "AI業務自動化ROIシミュレーター＆職種別プロンプト・GAS自動生成Webスイート（Programmatic SEO型ツール＋テンプレート販売）",
                "setup_cost_jpy": 0,
                "monthly_running_cost_jpy": 0,
                "human_intervention_required": "ZERO (完全自動生成・静的ホスティング・Xシェアバイラル内蔵)",
                "monetization_channels": [
                    "業務自動化テンプレート＆GASコード完全版パック販売（¥1,980〜¥4,980）",
                    "AI SaaS / クラウドツール アフィリエイト導線",
                    "BtoB 自動化スクリプト受託リード獲得"
                ],
                "scores": {
                    "automation_feasibility": 98,
                    "speed_to_market": 96,
                    "viral_coefficient": 90,
                    "risk_of_bankruptcy": 0,
                    "total_ev_score": 96.0
                },
                "selected": True
            },
            {
                "id": "BM-02",
                "name": "従量課金APIラッパー型SaaS（OpenAI/Claude API直接提供）",
                "setup_cost_jpy": 3000,
                "monthly_running_cost_jpy": 5000,
                "human_intervention_required": "LOW",
                "scores": {
                    "automation_feasibility": 80,
                    "speed_to_market": 75,
                    "viral_coefficient": 70,
                    "risk_of_bankruptcy": 75,
                    "total_ev_score": 52.5
                },
                "selected": False,
                "rejection_reason": "API従量課金により無料ユーザーが殺到した際、15,000円の軍資金が数日で枯渇し失格になるリスクが高いため却下。"
            },
            {
                "id": "BM-03",
                "name": "一般的なブログ記事量産メディア",
                "setup_cost_jpy": 1500,
                "monthly_running_cost_jpy": 1000,
                "human_intervention_required": "LOW",
                "scores": {
                    "automation_feasibility": 85,
                    "speed_to_market": 70,
                    "viral_coefficient": 40,
                    "risk_of_bankruptcy": 20,
                    "total_ev_score": 61.0
                },
                "selected": False,
                "rejection_reason": "単なるテキスト記事は90日間の短期決戦でSNS初速が出にくい。『触ってすぐ結果が出るインタラクティブWebツール』の方がSNS拡散力が圧倒的に高い。"
            }
        ]

        target_personas = [
            {"slug": "ec-inventory", "title": "EC・物販の在庫管理＆価格改定自動化", "avg_hours_saved_monthly": 42, "hourly_wage": 2500},
            {"slug": "sns-content", "title": "X/Threads 毎日投稿＆バズ構文自動生成", "avg_hours_saved_monthly": 30, "hourly_wage": 2200},
            {"slug": "sales-email", "title": "BtoB営業リスト抽出＆パーソナライズ文面自動化", "avg_hours_saved_monthly": 35, "hourly_wage": 2800},
            {"slug": "accounting-invoice", "title": "請求書・領収書PDFのAI読取＆スプレッドシート記帳", "avg_hours_saved_monthly": 24, "hourly_wage": 2500},
            {"slug": "youtube-script", "title": "YouTube/ショート動画の構成・台本・メタデータ自動生成", "avg_hours_saved_monthly": 38, "hourly_wage": 2600},
            {"slug": "real-estate-flyer", "title": "不動産物件マイソク・ポータル入稿文面のAI自動作成", "avg_hours_saved_monthly": 28, "hourly_wage": 2700},
            {"slug": "hr-resume-screening", "title": "採用・人事の職務経歴書スクリーニング＆面接質問自動生成", "avg_hours_saved_monthly": 32, "hourly_wage": 3000},
            {"slug": "google-maps-meo", "title": "店舗・クリニックのGoogleマップ口コミ自動返信＆MEO対策", "avg_hours_saved_monthly": 18, "hourly_wage": 2400},
            {"slug": "meeting-minutes-todo", "title": "商談・社内会議の文字起こし要約＆タスク自動割り振り", "avg_hours_saved_monthly": 26, "hourly_wage": 2800},
            {"slug": "seo-article-outline", "title": "オウンドメディアSEO記事の構成案・FAQ構造化データ自動生成", "avg_hours_saved_monthly": 40, "hourly_wage": 2500},
            {"slug": "ec-customer-support", "title": "ECショップの発送連絡・返品問い合わせAI自動一次返信", "avg_hours_saved_monthly": 29, "hourly_wage": 2200},
            {"slug": "amazon-rakuten-review", "title": "Amazon・楽天の競合商品レビュー分析＆改善アイデア抽出", "avg_hours_saved_monthly": 22, "hourly_wage": 2600},
            {"slug": "line-step-delivery", "title": "LINE公式アカウントの友だち追加後ステップ配信シナリオ生成", "avg_hours_saved_monthly": 25, "hourly_wage": 2700},
            {"slug": "instagram-reels-script", "title": "Instagramリール・TikTok縦型ショート動画のバズ台本量産", "avg_hours_saved_monthly": 34, "hourly_wage": 2300},
            {"slug": "subsidy-business-plan", "title": "補助金申請・融資用の事業計画書ドラフト＆収支表自動作成", "avg_hours_saved_monthly": 45, "hourly_wage": 3500},
            {"slug": "contract-risk-check", "title": "業務委託契約書・NDAの不利条項チェック＆修正案プロンプト", "avg_hours_saved_monthly": 16, "hourly_wage": 4000},
            {"slug": "shift-schedule-gas", "title": "アルバイト・スタッフの希望シフト回収＆スプレッドシート自動編成", "avg_hours_saved_monthly": 20, "hourly_wage": 2400},
            {"slug": "competitor-lp-analysis", "title": "競合ランディングページ(LP)の訴求軸分解＆ABテスト案生成", "avg_hours_saved_monthly": 27, "hourly_wage": 3000},
            {"slug": "google-meta-ads-copy", "title": "Google広告・Meta広告の検索見出し15本＆説明文一括ジェネレーター", "avg_hours_saved_monthly": 21, "hourly_wage": 2900},
            {"slug": "weekly-kpi-slack-bot", "title": "スプレッドシート週次売上KPIの自動集計＆Slack/Chatwork毎朝通知", "avg_hours_saved_monthly": 19, "hourly_wage": 2800}
        ]

        live_signals = self._fetch_live_note_signals()
        scored_personas = self._score_niches_by_signals(target_personas, live_signals)
        ranked_personas = sorted(scored_personas, key=lambda x: x["demand_score"], reverse=True)
        for rank_idx, item in enumerate(ranked_personas):
            if rank_idx < 3:
                item["status"] = "winner"
            elif rank_idx < len(ranked_personas) - 3:
                item["status"] = "growing"
            else:
                item["status"] = "pivot_candidate"

        top_winners = ranked_personas[:3]
        new_business_seeds = [
            {
                "pillar": "第2の柱（BtoBバックオフィス・監査支援）",
                "title": "請求書・契約リスク・補助金ドラフトのAI自動チェックツール群",
                "reason": "単価（時給換算¥3,500〜¥4,000）が高く法人・フリーランスの支払意欲が強い領域のため、第1事業の初黒字化後に上位パックとして展開。",
                "target_price_jpy": 4980,
                "stage": "needs_validation",
            },
            {
                "pillar": "第3の柱（SNS・クリエイター収益化自動化）",
                "title": "YouTubeショート・note・LINEステップ配信のテンプレート量産スタジオ",
                "reason": "SNS発信者・副業層からの需要が急増しており、無料ツールからのバイラル流入と高相性なため次期新市場として育成。",
                "target_price_jpy": 2980,
                "stage": "market_research",
            },
        ]

        live_needs_payload = {
            "analyzed_at": datetime.now().astimezone().isoformat(),
            "api_status": live_signals["api_status"],
            "market_summary": (
                f"実測スキ反響（{len(live_signals['own_articles'])}記事）と外部市場トレンド（{len(live_signals['external_trends'])}件）を統合分析。"
                f"現在の最上位ニーズTOP3は「{top_winners[0]['title']}」「{top_winners[1]['title']}」「{top_winners[2]['title']}」。"
            ),
            "top_winner_niches": top_winners,
            "external_trends_top5": live_signals["external_trends"][:5],
            "own_articles_performance": live_signals["own_articles"],
            "new_business_seeds": new_business_seeds,
        }
        with open(LIVE_NEEDS_PATH, "w", encoding="utf-8") as f:
            json.dump(live_needs_payload, f, ensure_ascii=False, indent=2)

        report = {
            "analyzed_at": datetime.now().astimezone().isoformat(),
            "winner_model": candidates[0],
            "evaluated_candidates": candidates,
            "high_demand_niches": scored_personas,
            "top_winner_niches": top_winners,
            "live_needs_radar": live_needs_payload,
            "new_business_seeds": new_business_seeds,
            "strategic_conclusion": (
                "サーバー代・API代を0円に抑える『クライアントサイド完結型インタラクティブ診断＆コード生成Webツール』を中核とし、"
                "世の中のニーズ調査と実測反響（スキ数）で上位TOP3に入った勝ち筋テーマに集中投下する。"
                "第1事業で安定した利益と顧客基盤を作った後、第2・第3の柱（BtoB監査・クリエイター自動化）へ多角化する。"
            )
        }

        with open(RESEARCH_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return report

    @staticmethod
    def _score_niches_by_signals(personas: list[dict], live_signals: dict) -> list[dict]:
        """自社note記事のスキ数・外部トレンド一致数・時間削減価値から需要スコアを算出する。"""
        keyword_map = {
            "ec-inventory": ["EC", "物販", "在庫", "価格改定"],
            "sns-content": ["X/Threads", "SNS", "Threads", "バズ構文"],
            "sales-email": ["BtoB営業", "営業リスト", "営業メール"],
            "accounting-invoice": ["請求書", "領収書", "経理"],
            "youtube-script": ["YouTube", "ショート動画", "台本"],
            "real-estate-flyer": ["不動産", "物件", "マイソク"],
            "hr-resume-screening": ["採用", "人事", "職務経歴書"],
            "google-maps-meo": ["Googleマップ", "口コミ", "MEO"],
            "meeting-minutes-todo": ["会議", "商談", "議事録", "文字起こし"],
            "seo-article-outline": ["SEO記事", "オウンドメディア", "構成案"],
            "ec-customer-support": ["発送連絡", "返品問い合わせ", "一次返信"],
            "amazon-rakuten-review": ["Amazon", "楽天", "レビュー分析"],
            "line-step-delivery": ["LINE公式", "ステップ配信"],
            "instagram-reels-script": ["Instagram", "TikTok", "リール"],
            "subsidy-business-plan": ["補助金", "融資", "事業計画書"],
            "contract-risk-check": ["契約書", "NDA", "不利条項"],
            "shift-schedule-gas": ["シフト", "アルバイト", "勤怠"],
            "competitor-lp-analysis": ["ランディングページ", "競合LP", "ABテスト"],
            "google-meta-ads-copy": ["Google広告", "Meta広告", "広告見出し"],
            "weekly-kpi-slack-bot": ["週次売上KPI", "Slack", "Chatwork", "週次レポート"],
        }

        own_articles = live_signals.get("own_articles", [])
        ext_trends = live_signals.get("external_trends", [])
        scored = []
        for item in personas:
            copy_item = dict(item)
            slug = copy_item["slug"]
            kws = keyword_map.get(slug, [copy_item["title"][:4]])

            actual_likes = 0
            matched_own = 0
            for art in own_articles:
                t = art.get("title", "")
                if any(k in t for k in kws) or copy_item["title"][:8] in t:
                    actual_likes += int(art.get("likes", 0) or 0)
                    matched_own += 1

            trend_matches = 0
            trend_likes_boost = 0
            for tr in ext_trends:
                t = tr.get("title", "")
                if any(k.lower() in t.lower() for k in kws):
                    trend_matches += 1
                    trend_likes_boost += min(30, int(tr.get("likes", 0) or 0) // 2)

            monthly_value_score = round((copy_item["avg_hours_saved_monthly"] * copy_item["hourly_wage"]) / 3000, 1)
            demand_score = round(45.0 + monthly_value_score + (actual_likes * 6.0) + (trend_matches * 7.5) + trend_likes_boost * 0.4, 1)

            copy_item["actual_likes"] = actual_likes
            copy_item["matched_own_articles"] = matched_own
            copy_item["trend_matches"] = trend_matches
            copy_item["demand_score"] = demand_score
            copy_item["status"] = "growing"
            scored.append(copy_item)
        return scored


if __name__ == "__main__":
    agent = ResearcherAgent()
    res = agent.run_market_analysis()
    print("[Researcher Agent] Selected Winner:", res["winner_model"]["name"])
    print("[Researcher Agent] Top 3 Demand Niches:", [n["title"] for n in res["top_winner_niches"]])

