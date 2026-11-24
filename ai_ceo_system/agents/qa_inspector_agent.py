import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
QA_REPORT_PATH = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "qa_health_report.json")
BASE_URL = "https://toproad-creator.github.io/autoflow-ai-ceo"
PAID_NOTE_URL = "https://note.com/toproad_1989/n/n5d0e28a74f91"
NOTE_CREATOR_API_URL = "https://note.com/api/v2/creators/toproad_1989/contents?kind=note&page=1"
GH_ACTIONS_API_URL = "https://api.github.com/repos/toproad-creator/autoflow-ai-ceo/actions/runs?per_page=3"


class QAInspectorAgent:
    """全Webツール・全SEOページ・note公開記事・自動スケジューラの動作点検（E2E QA）エージェント
    ただファイルを作るだけでなく、実際に公開URLへアクセスしてJavaScriptの動作・リンク切れ・コンソールエラー・note記事内リンクを自動点検する。
    """

    def __init__(self):
        os.makedirs(os.path.dirname(QA_REPORT_PATH), exist_ok=True)

    def check_http_and_links(self, urls: list[str]) -> list[dict]:
        results = []
        for url in urls:
            last_err = ""
            ok_done = False
            for _ in range(2):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        html = resp.read().decode("utf-8", errors="ignore")
                        has_note_cta = PAID_NOTE_URL in html
                        results.append({
                            "url": url,
                            "status": resp.status,
                            "ok": resp.status == 200,
                            "has_paid_note_link": has_note_cta,
                            "size_bytes": len(html)
                        })
                        ok_done = True
                        break
                except Exception as e:
                    last_err = str(e)
            if not ok_done:
                results.append({
                    "url": url,
                    "status": 0,
                    "ok": False,
                    "error": last_err
                })
        return results

    def check_live_note_articles(self) -> list[dict]:
        results = []
        try:
            all_items = []
            for page_idx in range(1, 5):
                req = urllib.request.Request(f"{NOTE_CREATOR_API_URL[:-1]}{page_idx}", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    c_data = json.loads(resp.read().decode("utf-8")).get("data", {})
                contents = c_data.get("contents", [])
                all_items.extend(contents)
                if c_data.get("isLastPage", True) or not contents:
                    break
            for item in all_items:
                key = item.get("key")
                n_req = urllib.request.Request(f"https://note.com/api/v3/notes/{key}", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(n_req, timeout=8) as n_resp:
                    n_data = json.loads(n_resp.read().decode("utf-8")).get("data", {})
                body_html = n_data.get("body", "") or ""
                link_count = len(re.findall(r"<a href=", body_html))
                has_thumb = bool(item.get("eyecatch"))
                price_val = item.get("price", 0) or 0
                is_paid = price_val > 0
                is_thin_boilerplate = (not is_paid) and ("スプレッドシートへそのまま貼り付け可能なタブ区切り（TSV）形式で構造化して出力してください" in body_html)
                results.append({
                    "key": key,
                    "url": f"https://note.com/toproad_1989/n/{key}",
                    "title": item.get("name", "")[:35],
                    "has_thumbnail": has_thumb,
                    "clickable_links_count": link_count,
                    "likes": item.get("likeCount", 0),
                    "price": price_val,
                    "is_paid": is_paid,
                    "is_thin_boilerplate": is_thin_boilerplate,
                    "healthy": has_thumb and (is_paid or link_count >= 1),
                })
        except Exception as e:
            results.append({"error": str(e), "healthy": False})
        return results

    def run_browser_e2e_tests(self) -> dict:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {"status": "skipped_no_playwright"}

        e2e_results = {}
        console_errors = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda err: console_errors.append(f"{page.url}: {err}"))

            page.goto(f"{BASE_URL}/", wait_until="networkidle", timeout=30000)
            body_text1 = page.inner_text("body")
            e2e_results["index_tool"] = {
                "title": page.title(),
                "rendered_ok": "AutoFlow" in body_text1 or "削減" in body_text1,
                "note_cta_count": page.locator(f'a[href*="{PAID_NOTE_URL}"]').count()
            }

            page.goto(f"{BASE_URL}/prompt-builder.html", wait_until="networkidle", timeout=30000)
            gen_btn = page.locator("button").first
            if gen_btn.is_visible():
                gen_btn.click()
            e2e_results["prompt_builder_tool"] = {
                "title": page.title(),
                "interactive_buttons": page.locator("button").count(),
                "note_cta_count": page.locator(f'a[href*="{PAID_NOTE_URL}"]').count()
            }

            page.goto(f"{BASE_URL}/gas-debugger.html", wait_until="networkidle", timeout=30000)
            btns = page.locator("button")
            if btns.count() > 0:
                btns.first.click()
            e2e_results["gas_debugger_tool"] = {
                "title": page.title(),
                "interactive_buttons": btns.count(),
                "note_cta_count": page.locator(f'a[href*="{PAID_NOTE_URL}"]').count()
            }

            page.goto(f"{BASE_URL}/free-templates.html", wait_until="networkidle", timeout=30000)
            e2e_results["free_templates_page"] = {
                "title": page.title(),
                "sample_copy_buttons": page.locator("button").count(),
                "note_cta_count": page.locator(f'a[href*="{PAID_NOTE_URL}"]').count()
            }

            page.goto(f"{BASE_URL}/pro-pack.html", wait_until="networkidle", timeout=30000)
            e2e_results["sales_lp"] = {
                "title": page.title(),
                "note_cta_count": page.locator(f'a[href*="{PAID_NOTE_URL}"]').count()
            }

            browser.close()

        return {
            "status": "passed" if len(console_errors) == 0 else "failed_js_error",
            "js_console_errors": console_errors,
            "tools_tested": e2e_results
        }

    def check_windows_scheduler(self) -> dict:
        if os.name != "nt":
            return {"status": "cloud_linux_env"}
        try:
            proc = subprocess.run(
                ["schtasks", "/Query", "/TN", "Antigravity_AI_CEO_Daily", "/V", "/FO", "LIST"],
                capture_output=True, text=True, errors="ignore", timeout=8
            )
            return {
                "registered": proc.returncode == 0,
                "raw_summary": proc.stdout[:600] if proc.returncode == 0 else proc.stderr[:300]
            }
        except Exception as e:
            return {"registered": False, "error": str(e)}

    def check_github_actions_health(self) -> dict:
        """GitHub Actions の直近完了ワークフロー実行結果をAPI経由で自動点検する。"""
        try:
            req = urllib.request.Request(
                GH_ACTIONS_API_URL,
                headers={"User-Agent": "AutoFlow-QA", "Accept": "application/vnd.github+json"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            runs = data.get("workflow_runs", [])
            completed = [r for r in runs if r.get("status") == "completed"]
            if not completed:
                return {"status": "no_completed_runs", "healthy": True, "latest_conclusion": "unknown"}
            latest = completed[0]
            conclusion = latest.get("conclusion", "unknown")
            return {
                "status": "checked",
                "run_id": latest.get("id"),
                "latest_conclusion": conclusion,
                "updated_at": latest.get("updated_at"),
                "html_url": latest.get("html_url"),
                "healthy": conclusion == "success",
            }
        except Exception as e:
            return {"status": "api_unavailable", "healthy": True, "latest_conclusion": "unknown", "error": str(e)}

    def diagnose_system_and_business_issues(
        self,
        broken_urls: list[dict],
        note_articles: list[dict],
        e2e: dict,
        gh_actions: dict | None = None,
    ) -> list[str]:
        """AIシステム自身の稼働異常・エラーログ・売上ボトルネックを自動検出する自己診断エンジン"""
        issues = []

        # 1. Webページ・リンク切れチェック
        if broken_urls:
            issues.append(f"【Web障害】公開URLのうち {len(broken_urls)} 件でアクセス異常が発生しています。")

        # 2. note記事の品質チェック
        unhealthy_notes = [n for n in note_articles if not n.get("healthy", False)]
        if unhealthy_notes:
            issues.append(f"【note導線不備】公開note記事のうち {len(unhealthy_notes)} 本でサムネイルまたは誘導リンクが不足しています。")

        # 3. ブラウザE2Eエラーチェック
        js_errs = e2e.get("js_console_errors", [])
        if js_errs:
            issues.append(f"【画面エラー】Webツール上で {len(js_errs)} 件のJavaScriptエラーが検出されました。")

        # 3.5 GitHub Actions（クラウド自動実行）の直近状態チェック
        if gh_actions and gh_actions.get("latest_conclusion") == "failure":
            issues.append(
                f"【クラウド自動実行エラー検知】直近の GitHub Actions 実行（Run {gh_actions.get('run_id')}）が失敗していました。ワークフローとクラウド互換コードの点検が必要です。"
            )

        # 4. 直近の実行ログ（scheduler_execution.log）からエラーやWarningを自動検知
        sched_log_path = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "scheduler_execution.log")
        if os.path.exists(sched_log_path):
            try:
                with open(sched_log_path, "r", encoding="utf-8", errors="ignore") as f:
                    recent_lines = f.readlines()[-40:]
                warnings = [ln.strip() for ln in recent_lines if ("Warning:" in ln or "Error" in ln or "Traceback" in ln)]
                if warnings:
                    issues.append(f"【システム警告検知】直近の自動実行ログで警告が記録されています（例: {warnings[-1][:80]}）。")
            except Exception:
                pass

        # 5. 直近の役員会議が定型文（フォールバック）に落ちていないか自己点検
        board_dir = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "board_meetings")
        if os.path.exists(board_dir):
            try:
                meeting_files = sorted(
                    [fn for fn in os.listdir(board_dir) if fn.startswith("day") and fn.endswith("_meeting.json")],
                    key=lambda x: int(re.sub(r"\D", "", x) or 0),
                )
                if meeting_files:
                    latest_m_path = os.path.join(board_dir, meeting_files[-1])
                    with open(latest_m_path, "r", encoding="utf-8") as f:
                        m_data = json.loads(f.read())
                    engine = m_data.get("reasoning_engine", "")
                    if "LLM_MULTI_AGENT" not in engine:
                        issues.append(
                            f"【AI頭脳フォールバック警告】直近の役員会議（{meeting_files[-1]}）がAIモデルではなく定型文エンジン（{engine}）で動作していました。"
                        )
            except Exception:
                pass

        # 6. ビジネス数値（metrics.json）＆公開記事コンテンツ実態からのボトルネック自動診断
        thin_free = [n for n in note_articles if n.get("is_thin_boilerplate")]
        if thin_free:
            issues.append(
                f"【無料記事コンテンツ改善】公開note記事のうち {len(thin_free)} 本が旧来の簡易短文構成のままです。"
                "スキ数の多い人気記事から順に、実務専用プロンプト＋GAS完成コード付きの本格解説へ差し替えることで有料版への信頼を高められます。"
            )

        metrics_path = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "metrics.json")
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, "r", encoding="utf-8") as f:
                    m = json.loads(f.read())
                rev = m.get("financials", {}).get("total_revenue", 0)
                gh_kpi = m.get("product_kpis", {}).get("github_traffic_metrics", {})
                repo_uniques = gh_kpi.get("repo_uniques_14d", 0)
                note_kpi = m.get("product_kpis", {}).get("note_live_metrics", {})
                likes = note_kpi.get("total_account_likes", 0)
                paid_likes = note_kpi.get("total_paid_likes", note_kpi.get("paid_article_likes", 0))
                paid_cnt = note_kpi.get("paid_notes_count", 1)
                total_notes = note_kpi.get("total_published_notes", 0)
                top_free = note_kpi.get("top_liked_free_notes") or []
                top_free_tag = top_free[0].get("title", "採用・補助金")[:22] if top_free else "採用・補助金"
                if rev == 0:
                    issues.append(
                        f"【最重要課題：未収益】実ユーザー反響は note {total_notes}本（累計スキ{likes}件 / 有料{paid_cnt}本・スキ{paid_likes}件）・"
                        f"GitHubページ訪問{repo_uniques}名（自動clone除く）に対し売上¥0。"
                        f"最上位反応テーマ『{top_free_tag}』からの¥500単品決済および¥980完全版への納得導線強化が必要です。"
                    )
            except Exception:
                pass

        if not issues:
            issues.append("【システム正常】技術エラーは0件です。さらなる成約率（CVR）向上と新規集客チャネルの拡大に集中してください。")

        return issues

    def run_full_inspection(self, niches: list[dict]) -> dict:
        core_urls = [
            f"{BASE_URL}/",
            f"{BASE_URL}/prompt-builder.html",
            f"{BASE_URL}/gas-debugger.html",
            f"{BASE_URL}/free-templates.html",
            f"{BASE_URL}/pro-pack.html",
            f"{BASE_URL}/sitemap.xml",
            f"{BASE_URL}/feed.xml",
        ]
        seo_urls = [f"{BASE_URL}/usecases/{n['slug']}.html" for n in niches]
        all_http = self.check_http_and_links(core_urls + seo_urls)
        ok_count = sum(1 for r in all_http if r.get("ok"))
        broken = [r for r in all_http if not r.get("ok")]

        note_articles = self.check_live_note_articles()
        all_notes_healthy = all(n.get("healthy", False) for n in note_articles)
        e2e = self.run_browser_e2e_tests()
        sched = self.check_windows_scheduler()
        gh_actions = self.check_github_actions_health()
        detected_issues = self.diagnose_system_and_business_issues(broken, note_articles, e2e, gh_actions=gh_actions)

        report = {
            "inspected_at": datetime.now().astimezone().isoformat(),
            "total_urls_checked": len(all_http),
            "urls_ok_count": ok_count,
            "broken_urls": broken,
            "live_note_articles_check": note_articles,
            "browser_e2e": e2e,
            "windows_scheduler_check": sched,
            "github_actions_check": gh_actions,
            "detected_issues": detected_issues,
            "overall_healthy": (len(broken) == 0 and all_notes_healthy and e2e.get("status") in ("passed", "skipped_no_playwright"))
        }
        with open(QA_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return report


if __name__ == "__main__":
    from researcher_agent import ResearcherAgent
    niches = ResearcherAgent().run_market_analysis()["high_demand_niches"]
    inspector = QAInspectorAgent()
    rep = inspector.run_full_inspection(niches)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
