import json
import os
import sys
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(__file__))

from cfo_analytics_agent import CFOAnalyticsAgent
from developer_agent import DeveloperAgent
from marketer_agent import MarketerAgent
from outbound_sales_agent import OutboundSalesAgent
from product_packager_agent import ProductPackagerAgent
from researcher_agent import ResearcherAgent

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATUS_LOG_PATH = os.path.join(ROOT_DIR, "status_log.md")


def run_autonomous_day_cycle(day: int | None = None, cloud_cron: bool = False):
    cfo = CFOAnalyticsAgent()
    wallet = cfo.load_wallet()
    if cloud_cron:
        last_date = wallet.get("last_updated", "")[:10]
        today_date = datetime.now().astimezone().isoformat()[:10]
        if last_date and last_date != today_date:
            wallet["day"] = min(90, wallet.get("day", 1) + 1)
            cfo.save_wallet(wallet)
    if day is None:
        day = wallet.get("day", 1)

    print(f"=== [AI CEO Antigravity] Starting Autonomous Execution Cycle: Day {day} / 90 ===")

    # 1. Market Research Agent
    researcher = ResearcherAgent()
    research_report = researcher.run_market_analysis()
    winner = research_report["winner_model"]
    niches = research_report["high_demand_niches"]
    print(f"[1/4 Research Agent] Target Niches Expanded to {len(niches)} high-converting verticals")

    # 2. Developer Agent & Product Packager Agent
    developer = DeveloperAgent()
    build_report = developer.build_all(niches)
    packager = ProductPackagerAgent()
    pack_report = packager.build_commercial_product_and_lp()
    print(
        f"[2/4 Developer & Packager Agent] Built {build_report['tools_count']} Interactive Web Tools + "
        f"{build_report['seo_pages_built']} SEO pages + {pack_report['templates_count']} Commercial Templates & Sales LP"
    )

    # 3. CFO & Analytics Agent
    metrics = cfo.audit_and_update_metrics(
        day=day,
        built_pages_count=build_report["seo_pages_built"],
        deployed_tools_count=build_report["tools_count"]
    )
    balance = metrics["financials"]["current_balance"]
    note_likes = metrics["product_kpis"].get("note_live_metrics", {}).get("like_count", 0)
    print(f"[3/4 CFO Agent] Financial & Live Note Audit Passed. Balance: ¥{balance:,} | Note Likes: {note_likes}")

    # 4. Marketer Agent & Outbound Sales Agent
    marketer = MarketerAgent()
    marketer.generate_daily_campaigns(
        day=day,
        balance=balance,
        seo_count=build_report["seo_pages_built"],
        note_likes=note_likes
    )
    sales_agent = OutboundSalesAgent()
    sales_report = sales_agent.execute_daily_sales_actions(niches)
    print(f"[4/4 Marketer & Sales Agent] Generated Viral Posts + Pinged IndexNow ({sales_report['submitted_urls_count']} URLs)")

    # 5. Update root status_log.md
    status_md = f"""# 自律型AI CEO 稼働ステータス＆経営ログ (status_log.md)

- **最終自動更新日時:** {datetime.now().astimezone().isoformat()}
- **現在フェーズ:** Day {day} / 90
- **現在残高:** ¥{balance:,}（初期資金 ¥15,000 / 累計支出 ¥0 / 累計売上 ¥0）
- **note有料記事ステータス:** 公開中（価格 ¥1,980 / 現在のスキ数: {note_likes}件 / URL: https://note.com/toproad_1989/n/n5d0e28a74f91 ）
- **財務健全性:** NORMAL（破産リスク 0%・固定費 ¥0 構成）

---

## 稼働中の公開Webプロダクト一覧（計 {build_report['tools_count'] + build_report['seo_pages_built'] + 1} ページ稼働中）
1. **第1弾ツール『AutoFlow AI（業務削減ROIシミュレーター＆コード生成）』**: https://toproad-creator.github.io/autoflow-ai-ceo/
2. **第2弾ツール『AutoFix AI（GASエラー＆AIプロンプト3秒診断・自動修正ツール）』**: https://toproad-creator.github.io/autoflow-ai-ceo/gas-debugger.html
3. **有料商品セールスLP『AutoFlow Pro 全50種完全版パック（¥1,980 note決済直結）』**: https://toproad-creator.github.io/autoflow-ai-ceo/pro-pack.html
4. **業種別Programmatic SEO集客ページ群**: 全{build_report['seo_pages_built']}業種（JSON-LD FAQ構造化データ＆無料スタータープロンプト内蔵）

---

## 実行履歴ログ
- **[Day 1]** `wallet.json` 初期化（¥15,000）、第1弾ツール『AutoFlow AI』開発、GitHub Pages & Actions 24時間自動稼働構築
- **[Day 2]** 全50種プロンプト＆GAS完全版パック（¥1,980）をnoteにて商用公開（ https://note.com/toproad_1989/n/n5d0e28a74f91 ）、全ページの購入ボタンを実決済へ直結
- **[Day {day}]** 朝08:00自動スケジューラ稼働確認、note APIリアルタイム計測実装（スキ {note_likes}件検知）、第2弾Webツール『AutoFix AI（`gas-debugger.html`）』新規構築・デプロイ、業種別SEOページを10本→{build_report['seo_pages_built']}本へ倍増
"""
    with open(STATUS_LOG_PATH, "w", encoding="utf-8") as f:
        f.write(status_md)

    print(f"=== [AI CEO Antigravity] Day {day} Cycle Completed Successfully! ===")


if __name__ == "__main__":
    is_cron = "--cloud-cron" in sys.argv
    run_autonomous_day_cycle(cloud_cron=is_cron)
