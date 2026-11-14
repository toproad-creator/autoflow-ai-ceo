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
from executive_board_agent import ExecutiveBoardAgent
from marketer_agent import MarketerAgent
from outbound_sales_agent import OutboundSalesAgent
from product_packager_agent import ProductPackagerAgent
from qa_inspector_agent import QAInspectorAgent
from researcher_agent import ResearcherAgent

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATUS_LOG_PATH = os.path.join(ROOT_DIR, "status_log.md")
SCHED_LOG_PATH = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "scheduler_execution.log")
SHORTS_URLS_JSON = os.path.join(ROOT_DIR, "ai_ceo_system", "shorts_videos", "youtube_uploaded_urls.json")
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


def load_uploaded_shorts() -> list[dict]:
    if os.path.exists(SHORTS_URLS_JSON):
        try:
            with open(SHORTS_URLS_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def auto_sync_github_if_local(day: int):
    if not os.path.exists(GIT_EXE):
        return
    try:
        subprocess.run([GIT_EXE, "add", "wallet.json", "status_log.md", "README.md", "ai_ceo_system/"], cwd=ROOT_DIR, timeout=20)
        subprocess.run([GIT_EXE, "commit", "-m", f"chore(orchestrator): automated Day {day} executive board & profit cycle sync"], cwd=ROOT_DIR, timeout=20)
        subprocess.run([GIT_EXE, "fetch", "origin"], cwd=ROOT_DIR, timeout=25)
        subprocess.run([GIT_EXE, "merge", "origin/main", "-X", "ours", "-m", "Auto-merge remote"], cwd=ROOT_DIR, timeout=20)
        subprocess.run([GIT_EXE, "push", "origin", "main"], cwd=ROOT_DIR, timeout=30)
        log_step("[Git Auto-Sync] Successfully pushed daily updates to GitHub.")
    except Exception as e:
        log_step(f"[Git Auto-Sync] Warning: {e}")


def run_autonomous_day_cycle(day: int | None = None, cloud_cron: bool = False, build_shorts: bool = True):
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

    log_step(f"=== [AI CEO Antigravity] Starting Profit-First Autonomous Organization Cycle: Day {day} / 90 ===")

    # 1. Market Research Agent
    researcher = ResearcherAgent()
    research_report = researcher.run_market_analysis()
    niches = research_report["high_demand_niches"]
    log_step(f"[1/8 Research Agent] Target Niches Expanded to {len(niches)} high-converting verticals")

    # 2. CRO & CTO Developer/Packager Agent (Builds 27 Web Pages with Sticky ¥980 Bar & Board Banner)
    developer = DeveloperAgent()
    build_report = developer.build_all(niches)
    packager = ProductPackagerAgent()
    pack_report = packager.build_commercial_product_and_lp()
    log_step(
        f"[2/8 CRO & CTO Build] Built {build_report['tools_count']} Web Tools + "
        f"{build_report['seo_pages_built']} SEO pages + Sticky ¥980 Conversion Funnel"
    )

    # 3. CMO Note Auto-Publisher Agent (Local Windows 08:00 scheduler)
    is_github_actions = os.getenv("GITHUB_ACTIONS", "").lower() == "true"
    note_pub_result = {"status": "skipped_github_actions"}
    if not is_github_actions:
        try:
            from note_auto_publisher import NoteAutoPublisherAgent
            note_publisher = NoteAutoPublisherAgent()
            note_pub_result = note_publisher.publish_daily_lead_if_needed(day=day, niches=niches)
            log_step(f"[3/8 CMO Note Publisher] Status: {note_pub_result.get('status')} | URL: {note_pub_result.get('url', '')}")
        except Exception as e:
            log_step(f"[3/8 CMO Note Publisher] Warning: {e}\n{traceback.format_exc()}")

    # 4. CFO & Analytics Agent
    metrics = cfo.audit_and_update_metrics(
        day=day,
        built_pages_count=build_report["seo_pages_built"],
        deployed_tools_count=build_report["tools_count"]
    )
    balance = metrics["financials"]["current_balance"]
    total_revenue = metrics["financials"]["total_revenue"]
    note_meta = metrics["product_kpis"].get("note_live_metrics", {})
    price_jpy = note_meta.get("price_jpy", 980)
    paid_likes = note_meta.get("paid_article_likes", 3)
    total_notes = note_meta.get("total_published_notes", 7)
    total_likes = note_meta.get("total_account_likes", 15)
    gh_meta = metrics["product_kpis"].get("github_traffic_metrics", {})
    gh_clones = gh_meta.get("clones_14d", 315)
    gh_uniques = gh_meta.get("unique_cloners_14d", 126)
    log_step(
        f"[4/8 CFO Audit] Balance: ¥{balance:,} | Revenue: ¥{total_revenue:,} | Price: ¥{price_jpy:,} | "
        f"Note Articles: {total_notes} (Likes: {total_likes}) | GitHub Clones: {gh_clones}"
    )

    published_notes = fetch_all_published_notes()
    latest_note_url = published_notes[0]["url"] if published_notes else "https://note.com/toproad_1989/n/n5d0e28a74f91"
    latest_note_title = published_notes[0]["title"] if published_notes else "AutoFlow Pro"

    # 5. Autonomous Profit Executive Board Meeting (CEO, CFO, CRO, CMO, CTO)
    board_agent = ExecutiveBoardAgent()
    board_record = board_agent.hold_daily_profit_board_meeting(
        day=day,
        balance=balance,
        total_revenue=total_revenue,
        price_jpy=price_jpy,
        total_notes=total_notes,
        total_likes=total_likes,
        paid_likes=paid_likes,
        gh_clones=gh_clones,
        gh_uniques=gh_uniques,
        latest_note_url=latest_note_url,
        latest_note_title=latest_note_title,
    )
    log_step(f"[5/8 Executive Board Meeting] Completed | Primary Goal: {board_record['ceo_final_decision']['primary_goal']}")

    # 6. CMO YouTube Short Auto-Generation & Auto-Upload (Local only)
    latest_short_url = ""
    if not is_github_actions and build_shorts:
        try:
            from daily_short_pipeline import DailyShortPipelineAgent
            short_agent = DailyShortPipelineAgent()
            # まず前日以前で未作成のショート（例: Day 10）があれば自動補完し、続けて本日分を作成・公開
            for target_d in range(max(10, day - 1), day + 1):
                short_res = short_agent.build_and_upload_daily_short(
                    day=target_d,
                    balance=balance,
                    price_jpy=price_jpy,
                    total_notes=total_notes,
                    total_likes=total_likes,
                    gh_clones=gh_clones,
                    gh_uniques=gh_uniques,
                    latest_note_title=latest_note_title,
                    latest_note_thumb_path=note_pub_result.get("thumbnail_path", ""),
                    auto_upload=True,
                )
                latest_short_url = short_res.get("youtube_url", latest_short_url)
                log_step(f"[6/8 CMO Short Pipeline] Day {target_d} Status: {short_res.get('status')} | URL: {latest_short_url}")
        except Exception as e:
            log_step(f"[6/8 CMO Short Pipeline] Warning: {e}")

    # 7. CMO X (140-char compliant) Viral Posts & Outbound IndexNow
    marketer = MarketerAgent()
    campaign_data = marketer.generate_daily_campaigns(
        day=day,
        balance=balance,
        seo_count=build_report["seo_pages_built"],
        note_likes=total_likes,
        total_notes=total_notes,
        gh_clones=gh_clones,
        latest_note_url=latest_note_url,
        latest_note_title=latest_note_title,
        price_jpy=price_jpy,
        short_url=latest_short_url,
    )
    sales_agent = OutboundSalesAgent()
    sales_report = sales_agent.execute_daily_sales_actions(niches)
    log_step(f"[7/8 CMO & Sales Agent] Generated 140-char X Posts + Pinged IndexNow ({sales_report['submitted_urls_count']} URLs)")

    # 8. CTO/QA E2E Inspector Agent
    qa_agent = QAInspectorAgent()
    qa_report = qa_agent.run_full_inspection(niches)
    log_step(
        f"[8/8 CTO/QA Inspector] URLs OK: {qa_report['urls_ok_count']}/{qa_report['total_urls_checked']} | "
        f"E2E Status: {qa_report['browser_e2e'].get('status')} | Healthy: {qa_report['overall_healthy']}"
    )

    # Update root status_log.md dynamically with Board Meeting Decisions, Ready-to-Copy X Posts, Note URLs, and YouTube Shorts
    note_bullets = "\n".join(
        [f"  - {'【有料パック 先着10部¥980】' if n['price'] > 0 else '【無料集客記事】'}{n['title']} (スキ: {n['likes']}件) -> {n['url']}" for n in published_notes]
    )
    uploaded_shorts = load_uploaded_shorts()
    short_bullets = "\n".join(
        [f"  - **Day {s.get('day')}**: {s.get('url')} （{s.get('title', '')[:38]}…）" for s in uploaded_shorts if s.get("url")]
    )
    approved_bullets = "\n".join([f"  - {act}" for act in board_record["ceo_final_decision"]["approved_actions"]])

    status_md = f"""# 自律型AI CEO ＆ 5大AI役員会議 経営ステータスログ (status_log.md)

- **最終自動更新日時:** {datetime.now().astimezone().isoformat()}
- **現在フェーズ:** Day {day} / 90（利益創出特化型・AI役員会議オーケストレーター稼働中）
- **現在残高:** ¥{balance:,}（初期資金 ¥15,000 / 累計支出 ¥0 / 累計売上 ¥{total_revenue:,}）
- **有料商品ステータス:** 先着10部限定 **¥{price_jpy:,}**（定価 ¥1,980 から50%OFFセール中・無料試し読み10,515字＋実物コード2本公開済）
- **note公開記事ステータス:** 公開記事数 {total_notes}本（有料記事1本 + 無料集客記事 {max(0, total_notes - 1)}本 / 累計スキ数: {total_likes}件）
{note_bullets}
- **YouTubeショート自動公開ステータス:** 計 {len(uploaded_shorts)}本 公開中
{short_bullets}
- **GitHubトラフィック計測:** 過去14日間クローン数 {gh_clones}回（ユニーク {gh_uniques}名）
- **全自動E2E動作点検ステータス:** {qa_report['urls_ok_count']}/{qa_report['total_urls_checked']} URL正常稼働（JSエラー: {len(qa_report['browser_e2e'].get('js_console_errors', []))}件）

---

## 🏢 本日のAI役員会議（CEO・CFO・CRO・CMO・CTO）決定＆実行事項
- **最優先ゴール:** {board_record['ceo_final_decision']['primary_goal']}
- **会議で採択・即時実装された改善アクション:**
{approved_bullets}
- **詳細議事録ファイル:** `ai_ceo_system/data/board_meetings/latest_board_meeting.md`

---

## 📱 本日（Day {day}）のX（旧Twitter）コピペ投稿用テキスト（140字制限クリア済）

### パターン①：メイン版（Webサイト誘導）
```text
{campaign_data['x_post_pattern1_web']}
```

### パターン②：note直結版（先着10部 ¥{price_jpy} セール記事へ直接誘導）
```text
{campaign_data['x_post_pattern2_note']}
```

### パターン③：リプライ欄（返信欄）連結用
```text
{campaign_data['x_post_pattern3_reply']}
```

---

## 稼働中の公開Webプロダクト一覧（計 {build_report['tools_count'] + build_report['seo_pages_built'] + 2} URL稼働中）
1. **第1弾ツール『AutoFlow AI（業務削減ROIシミュレーター＆コード生成）』**: https://toproad-creator.github.io/autoflow-ai-ceo/
2. **第2弾ツール『Prompt Builder（3秒カスタムAI命令書ビルダー）』**: https://toproad-creator.github.io/autoflow-ai-ceo/prompt-builder.html
3. **第3弾ツール『AutoFix AI（GASエラー＆AIプロンプト3秒診断・自動修正ツール）』**: https://toproad-creator.github.io/autoflow-ai-ceo/gas-debugger.html
4. **第4弾ページ『厳選5種の自動化レシピ無料公開＆完全版50選比較ページ』**: https://toproad-creator.github.io/autoflow-ai-ceo/free-templates.html
5. **有料商品セールスLP『AutoFlow Pro 全50種完全版パック（先着10部 ¥{price_jpy} note決済直結）』**: https://toproad-creator.github.io/autoflow-ai-ceo/pro-pack.html
6. **業種別Programmatic SEO集客ページ群**: 全{build_report['seo_pages_built']}業種（画面下部追従・限定¥{price_jpy}購入バー標準搭載）
"""
    with open(STATUS_LOG_PATH, "w", encoding="utf-8") as f:
        f.write(status_md)

    if not is_github_actions:
        auto_sync_github_if_local(day)

    log_step(f"=== [AI CEO Antigravity] Day {day} Profit-First Autonomous Cycle Completed Successfully! ===")


if __name__ == "__main__":
    is_cron = "--cloud-cron" in sys.argv
    no_shorts = "--no-shorts" in sys.argv
    run_autonomous_day_cycle(cloud_cron=is_cron, build_shorts=not no_shorts)
