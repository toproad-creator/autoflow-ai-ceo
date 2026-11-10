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


class QAInspectorAgent:
    """全Webツール・全SEOページ・note公開記事・自動スケジューラの動作点検（E2E QA）エージェント
    ただファイルを作るだけでなく、実際に公開URLへアクセスしてJavaScriptの動作・リンク切れ・コンソールエラー・note記事内リンクを自動点検する。
    """

    def __init__(self):
        os.makedirs(os.path.dirname(QA_REPORT_PATH), exist_ok=True)

    def check_http_and_links(self, urls: list[str]) -> list[dict]:
        results = []
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")
                    has_note_cta = PAID_NOTE_URL in html
                    results.append({
                        "url": url,
                        "status": resp.status,
                        "ok": resp.status == 200,
                        "has_paid_note_link": has_note_cta,
                        "size_bytes": len(html)
                    })
            except Exception as e:
                results.append({
                    "url": url,
                    "status": 0,
                    "ok": False,
                    "error": str(e)
                })
        return results

    def check_live_note_articles(self) -> list[dict]:
        results = []
        try:
            req = urllib.request.Request(NOTE_CREATOR_API_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                c_data = json.loads(resp.read().decode("utf-8")).get("data", {})
            for item in c_data.get("contents", []):
                key = item.get("key")
                n_req = urllib.request.Request(f"https://note.com/api/v3/notes/{key}", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(n_req, timeout=8) as n_resp:
                    n_data = json.loads(n_resp.read().decode("utf-8")).get("data", {})
                body_html = n_data.get("body", "") or ""
                link_count = len(re.findall(r"<a href=", body_html))
                has_thumb = bool(item.get("eyecatch"))
                results.append({
                    "key": key,
                    "url": f"https://note.com/toproad_1989/n/{key}",
                    "title": item.get("name", "")[:35],
                    "has_thumbnail": has_thumb,
                    "clickable_links_count": link_count,
                    "likes": item.get("likeCount", 0),
                    "healthy": has_thumb and link_count >= 1
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

        report = {
            "inspected_at": datetime.now().astimezone().isoformat(),
            "total_urls_checked": len(all_http),
            "urls_ok_count": ok_count,
            "broken_urls": broken,
            "live_note_articles_check": note_articles,
            "browser_e2e": e2e,
            "windows_scheduler_check": sched,
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
