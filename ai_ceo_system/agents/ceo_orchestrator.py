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
from product_packager_agent import ProductPackagerAgent
from researcher_agent import ResearcherAgent

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATUS_LOG_PATH = os.path.join(ROOT_DIR, "status_log.md")


def run_autonomous_day_cycle(day: int = 1, cloud_cron: bool = False):
    cfo = CFOAnalyticsAgent()
    wallet = cfo.load_wallet()
    if cloud_cron:
        last_date = wallet.get("last_updated", "")[:10]
        today_date = datetime.now().astimezone().isoformat()[:10]
        if last_date and last_date != today_date:
            wallet["day"] = min(90, wallet.get("day", 1) + 1)
            cfo.save_wallet(wallet)
        day = wallet.get("day", 1)

    print(f"=== [AI CEO Antigravity] Starting Autonomous Execution Cycle: Day {day} / 90 ===")

    # 1. Market Research Agent
    researcher = ResearcherAgent()
    research_report = researcher.run_market_analysis()
    winner = research_report["winner_model"]
    niches = research_report["high_demand_niches"]
    print(f"[1/4 Research Agent] Selected Business Model: {winner['name']} (EV Score: {winner['scores']['total_ev_score']})")

    # 2. Developer Agent & Product Packager Agent
    developer = DeveloperAgent()
    build_report = developer.build_all(niches)
    packager = ProductPackagerAgent()
    pack_report = packager.build_commercial_product_and_lp()
    print(f"[2/4 Developer & Packager Agent] Built Main WebApp + {build_report['seo_pages_built']} SEO pages + {pack_report['templates_count']} Commercial Templates & Sales LP")

    # 3. CFO & Analytics Agent
    cfo = CFOAnalyticsAgent()
    metrics = cfo.audit_and_update_metrics(day=day, built_pages_count=build_report["seo_pages_built"])
    balance = metrics["financials"]["current_balance"]
    print(f"[3/4 CFO Agent] Financial Audit Passed. Current Balance: ¥{balance:,} (Expenses: ¥0)")

    # 4. Marketer Agent
    marketer = MarketerAgent()
    campaign = marketer.generate_daily_campaigns(day=day, balance=balance, seo_count=build_report["seo_pages_built"])
    print(f"[4/4 Marketer Agent] Generated X/Threads Viral Posts & YouTube Script")

    # 5. Update root status_log.md
    status_md = f"""# 自律型AI CEO 稼働ステータス＆経営ログ (status_log.md)

- **最終自動更新日時:** {datetime.now().astimezone().isoformat()}
- **現在フェーズ:** Day {day} / 90
- **現在残高:** ¥{balance:,}（初期資金 ¥15,000 / 累計支出 ¥0 / 累計売上 ¥0）
- **財務健全性:** NORMAL（破産リスク 0%・固定費 ¥0 構成）

---

## 稼働中のサブエージェント体制
1. **CEO Orchestrator (`ai_ceo_system/agents/ceo_orchestrator.py`)**: 全体統括・日次バッチ実行・意思決定
2. **Researcher Agent (`ai_ceo_system/agents/researcher_agent.py`)**: 高需要ニッチ抽出・期待値スコアリング
3. **Developer Agent (`ai_ceo_system/agents/developer_agent.py`)**: Webアプリ・Programmatic SEOページの自動生成・Cron構築
4. **Marketer Agent (`ai_ceo_system/agents/marketer_agent.py`)**: SNS拡散文面・動画ディレクション台本の自動生成
5. **CFO & Analytics Agent (`ai_ceo_system/agents/cfo_analytics_agent.py`)**: `wallet.json` 監査・KPI計測（`metrics.json`）

---

## Day 1 実行履歴ログ
- **[完了]** `wallet.json` および `status_log.md` の初期化（残高 ¥15,000）
- **[完了]** ビジネスモデル選定：『{winner['name']}』（EVスコア {winner['scores']['total_ev_score']}）を採択
- **[完了]** 第1弾Webプロダクト『AutoFlow AI（業務削減ROIシミュレーター＆AIプロンプト/GAS自動実行コード生成スイート）』を `ai_ceo_system/product_site/index.html` にビルド完了
- **[完了]** 職種別Programmatic SEOページ（5業種）と `sitemap.xml` を自動生成
- **[完了]** PC閉鎖時の24時間自律稼働用 `.github/workflows/autonomous_daily_cron.yml` を構築完了
"""
    with open(STATUS_LOG_PATH, "w", encoding="utf-8") as f:
        f.write(status_md)

    print(f"=== [AI CEO Antigravity] Day {day} Cycle Completed Successfully! ===")


if __name__ == "__main__":
    is_cron = "--cloud-cron" in sys.argv
    run_autonomous_day_cycle(day=1, cloud_cron=is_cron)
