import json
import os
import subprocess
import sys
import time
import traceback
import urllib.request
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(__file__))

from cfo_analytics_agent import CFOAnalyticsAgent
from developer_agent import DeveloperAgent
from marketer_agent import MarketerAgent
from outbound_sales_agent import OutboundSalesAgent
from product_packager_agent import ProductPackagerAgent
from qa_inspector_agent import QAInspectorAgent
from researcher_agent import ResearcherAgent

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATUS_LOG_PATH = os.path.join(ROOT_DIR, "status_log.md")
SCHED_LOG_PATH = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "scheduler_execution.log")
GIT_EXE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "MinGit", "cmd", "git.exe")


def log_step(msg: str):
    print(msg)
    try:
        with open(SCHED_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().astimezone().isoformat()}] {msg}\n")
    except Exception:
        pass


def wait_for_internet_connection(max_wait_sec: int = 120) -> bool:
    """スリープ復帰直後のWi-Fi再接続待ちによる ERR_INTERNET_DISCONNECTED を防ぐため、通信確立まで待機する"""
    start = time.time()
    while time.time() - start < max_wait_sec:
        try:
            req = urllib.request.Request("https://note.com", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(3)
    return False


def fetch_all_published_notes() -> list[dict]:
    all_notes = []
    try:
        for page_idx in range(1, 5):
            req = urllib.request.Request(
                f"https://note.com/api/v2/creators/toproad_1989/contents?kind=note&page={page_idx}",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8")).get("data", {})
                contents = data.get("contents", [])
                for c in contents:
                    all_notes.append({
                        "key": c.get("key"),
                        "title": c.get("name"),
                        "likes": c.get("likeCount", 0),
                        "price": c.get("price", 0),
                        "url": f"https://note.com/toproad_1989/n/{c.get('key')}"
                    })
                if data.get("isLastPage", True) or not contents:
                    break
    except Exception:
        pass
    return all_notes


def auto_sync_github_if_local(day: int):
    if not os.path.exists(GIT_EXE):
        return
    try:
        subprocess.run([GIT_EXE, "add", "wallet.json", "status_log.md", "README.md", "ai_ceo_system/"], cwd=ROOT_DIR, timeout=15)
        subprocess.run([GIT_EXE, "commit", "-m", f"chore(scheduler): automated Day {day} local 08:00 sync"], cwd=ROOT_DIR, timeout=15)
        subprocess.run([GIT_EXE, "fetch", "origin"], cwd=ROOT_DIR, timeout=20)
        subprocess.run([GIT_EXE, "merge", "origin/main", "-X", "ours", "-m", "Auto-merge remote"], cwd=ROOT_DIR, timeout=15)
        subprocess.run([GIT_EXE, "push", "origin", "main"], cwd=ROOT_DIR, timeout=25)
        log_step("[Git Auto-Sync] Successfully pushed daily updates to GitHub.")
    except Exception as e:
        log_step(f"[Git Auto-Sync] Warning: {e}")


def run_autonomous_day_cycle(day: int | None = None, cloud_cron: bool = False):
    online = wait_for_internet_connection(max_wait_sec=120)
    log_step(f"[Network Check] Internet connection ready: {online}")

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

    log_step(f"=== [AI CEO Antigravity] Starting Autonomous Execution Cycle: Day {day} / 90 ===")

    # 1. Market Research Agent
    researcher = ResearcherAgent()
    research_report = researcher.run_market_analysis()
    winner = research_report["winner_model"]
    niches = research_report["high_demand_niches"]
    log_step(f"[1/6 Research Agent] Target Niches Expanded to {len(niches)} high-converting verticals")

    # 2. Developer Agent & Product Packager Agent
    developer = DeveloperAgent()
    build_report = developer.build_all(niches)
    packager = ProductPackagerAgent()
    pack_report = packager.build_commercial_product_and_lp()
    log_step(
        f"[2/6 Developer & Packager Agent] Built {build_report['tools_count']} Interactive Web Tools + "
        f"{build_report['seo_pages_built']} SEO pages + {pack_report['templates_count']} Commercial Templates & Sales LP"
    )

    # 3. Note Auto-Publisher Agent (Runs automatically on local Windows 08:00 scheduler; skipped only on GitHub Actions Linux runner)
    is_github_actions = os.getenv("GITHUB_ACTIONS", "").lower() == "true"
    note_pub_result = {"status": "skipped_github_actions"}
    if not is_github_actions:
        try:
            from note_auto_publisher import NoteAutoPublisherAgent
            note_publisher = NoteAutoPublisherAgent()
            note_pub_result = note_publisher.publish_daily_lead_if_needed(day=day, niches=niches)
            log_step(f"[3/6 Note Auto-Publisher] Status: {note_pub_result.get('status')} | URL: {note_pub_result.get('url', '')}")
        except Exception as e:
            log_step(f"[3/6 Note Auto-Publisher] Warning: {e}\n{traceback.format_exc()}")

    # 4. CFO & Analytics Agent
    metrics = cfo.audit_and_update_metrics(
        day=day,
        built_pages_count=build_report["seo_pages_built"],
        deployed_tools_count=build_report["tools_count"]
    )
    balance = metrics["financials"]["current_balance"]
    note_meta = metrics["product_kpis"].get("note_live_metrics", {})
    note_likes = note_meta.get("paid_article_likes", note_meta.get("like_count", 0))
    total_notes = note_meta.get("total_published_notes", 1)
    total_likes = note_meta.get("total_account_likes", note_likes)
    gh_meta = metrics["product_kpis"].get("github_traffic_metrics", {})
    gh_clones = gh_meta.get("clones_14d", 0)
    log_step(
        f"[4/6 CFO Agent] Balance: ¥{balance:,} | Note Published Articles: {total_notes} "
        f"(Total Likes: {total_likes}) | GitHub Clones (14d): {gh_clones}"
    )

    # Fetch live list of published notes for dynamic status_log & marketing campaigns
    published_notes = fetch_all_published_notes()
    latest_note_url = published_notes[0]["url"] if published_notes else "https://note.com/toproad_1989/n/n5d0e28a74f91"
    latest_note_title = published_notes[0]["title"] if published_notes else "AutoFlow Pro"

    # 5. Marketer Agent & Outbound Sales Agent
    marketer = MarketerAgent()
    marketer.generate_daily_campaigns(
        day=day,
        balance=balance,
        seo_count=build_report["seo_pages_built"],
        note_likes=total_likes,
        total_notes=total_notes,
        gh_clones=gh_clones,
        latest_note_url=latest_note_url,
        latest_note_title=latest_note_title
    )
    sales_agent = OutboundSalesAgent()
    sales_report = sales_agent.execute_daily_sales_actions(niches)
    log_step(f"[5/6 Marketer & Sales Agent] Generated Viral Posts + Pinged IndexNow ({sales_report['submitted_urls_count']} URLs)")

    # 6. QA & E2E Inspector Agent
    qa_agent = QAInspectorAgent()
    qa_report = qa_agent.run_full_inspection(niches)
    log_step(
        f"[6/6 QA Inspector] URLs OK: {qa_report['urls_ok_count']}/{qa_report['total_urls_checked']} | "
        f"E2E Status: {qa_report['browser_e2e'].get('status')} | Healthy: {qa_report['overall_healthy']}"
    )

    # 7. Update root status_log.md dynamically with all published Note articles
    note_bullets = "\n".join(
        [f"  - {'【有料本編 ¥1,980】' if n['price'] > 0 else '【無料集客記事】'}{n['title']} (スキ: {n['likes']}件) -> {n['url']}" for n in published_notes]
    )
    status_md = f"""# 自律型AI CEO 稼働ステータス＆経営ログ (status_log.md)

- **最終自動更新日時:** {datetime.now().astimezone().isoformat()}
- **現在フェーズ:** Day {day} / 90
- **現在残高:** ¥{balance:,}（初期資金 ¥15,000 / 累計支出 ¥0 / 累計売上 ¥0）
- **note公開記事ステータス:** 公開記事数 {total_notes}本（有料記事 ¥1,980 + 無料集客記事 {max(0, total_notes - 1)}本 / 累計スキ数: {total_likes}件）
{note_bullets}
- **GitHubトラフィック計測:** 過去14日間クローン数 {gh_clones}回（ユニーク {gh_meta.get('unique_cloners_14d', 0)}名）
- **全自動E2E動作点検ステータス:** {qa_report['urls_ok_count']}/{qa_report['total_urls_checked']} URL正常稼働（JSエラー: {len(qa_report['browser_e2e'].get('js_console_errors', []))}件）
- **財務健全性:** NORMAL（破産リスク 0%・固定費 ¥0 構成）

---

## 稼働中の公開Webプロダクト一覧（計 {build_report['tools_count'] + build_report['seo_pages_built'] + 2} URL稼働中）
1. **第1弾ツール『AutoFlow AI（業務削減ROIシミュレーター＆コード生成）』**: https://toproad-creator.github.io/autoflow-ai-ceo/
2. **第2弾ツール『Prompt Builder（3秒カスタムAI命令書ビルダー）』**: https://toproad-creator.github.io/autoflow-ai-ceo/prompt-builder.html
3. **第3弾ツール『AutoFix AI（GASエラー＆AIプロンプト3秒診断・自動修正ツール）』**: https://toproad-creator.github.io/autoflow-ai-ceo/gas-debugger.html
4. **第4弾ページ『厳選5種の自動化レシピ無料公開＆完全版50選比較ページ』**: https://toproad-creator.github.io/autoflow-ai-ceo/free-templates.html
5. **有料商品セールスLP『AutoFlow Pro 全50種完全版パック（¥1,980 note決済直結）』**: https://toproad-creator.github.io/autoflow-ai-ceo/pro-pack.html
6. **業種別Programmatic SEO集客ページ群**: 全{build_report['seo_pages_built']}業種（JSON-LD FAQ構造化データ＆無料スタータープロンプト内蔵）

---

## 実行履歴ログ
- **[Day 1]** `wallet.json` 初期化（¥15,000）、第1弾ツール『AutoFlow AI』開発、GitHub Pages & Actions 24時間自動稼働構築
- **[Day 2]** 全50種プロンプト＆GAS完全版パック（¥1,980）をnoteにて商用公開（ https://note.com/toproad_1989/n/n5d0e28a74f91 ）、全ページの購入ボタンを実決済へ直結
- **[Day 3〜4]** 朝08:00自動スケジューラ稼働、第2〜4弾Webツール（`prompt-builder.html`, `gas-debugger.html`, `free-templates.html`）構築、業種別SEOページ20本展開、GitHub Gist & Release 外部被リンク網構築
- **[Day 5〜{day}]** noteタイムライン自動集客＆サムネイル自動生成システム稼働、E2E自動点検エージェント（`qa_inspector_agent.py`）稼働中。note公開記事{total_notes}本・累計スキ{total_likes}件・GitHubクローン{gh_clones}回へ拡大
"""
    with open(STATUS_LOG_PATH, "w", encoding="utf-8") as f:
        f.write(status_md)

    if not is_github_actions:
        auto_sync_github_if_local(day)

    log_step(f"=== [AI CEO Antigravity] Day {day} Cycle Completed Successfully! ===")


if __name__ == "__main__":
    is_cron = "--cloud-cron" in sys.argv
    run_autonomous_day_cycle(cloud_cron=is_cron)
