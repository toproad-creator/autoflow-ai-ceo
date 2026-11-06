import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

MARKETING_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "marketing_outputs")
PROFILE_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "note_browser_profile")
SCREENSHOT_PATH = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "note_autopost_latest.png")
PAID_NOTE_URL = "https://note.com/toproad_1989/n/n5d0e28a74f91"
WEB_TOOL_URL = "https://toproad-creator.github.io/autoflow-ai-ceo/"
NOTE_CREATOR_API_URL = "https://note.com/api/v2/creators/toproad_1989/contents?kind=note&page=1"


class NoteAutoPublisherAgent:
    """noteタイムライン集客用・無料お役立ち記事の自動執筆＆自動投稿エージェント
    .env の NOTE_EMAIL / NOTE_PASSWORD を使用して、全自動ログイン＆記事公開を行う。
    """

    def __init__(self):
        os.makedirs(MARKETING_DIR, exist_ok=True)
        os.makedirs(PROFILE_DIR, exist_ok=True)

    def fetch_published_titles(self) -> list[dict]:
        try:
            req = urllib.request.Request(NOTE_CREATOR_API_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8")).get("data", {})
                return [
                    {"key": c.get("key"), "title": c.get("name"), "url": f"https://note.com/toproad_1989/n/{c.get('key')}"}
                    for c in data.get("contents", [])
                ]
        except Exception:
            return []

    def generate_daily_free_lead_article(self, day: int, niche: dict) -> dict:
        title = f"【無料コピペOK】{niche['title']}をAIとGASで自動化して月{niche['avg_hours_saved_monthly']}時間浮かす実践レシピ"
        yearly_yen = niche["avg_hours_saved_monthly"] * 12 * niche["hourly_wage"]

        body = f"""毎日のルーティン業務で「{niche['title']}」に時間を奪われていませんか？

実は、この作業は「構造化AIプロンプト」と「Googleスプレッドシートの自動実行スクリプト（GAS）」を組み合わせることで、人間の手作業の85%以上を自動化できます。

月間平均で【約{niche['avg_hours_saved_monthly']}時間】、時給{niche['hourly_wage']:,}円換算で【年間 約{yearly_yen:,}円相当】の時間を生み出す具体的な手順を、この記事で無料公開します。

■ 1. まずはあなたの業務削減額を30秒で無料診断
「自分の作業時間だと年間いくら浮くのか？」を0秒で計算し、その場で専用コードを出力できる無料Webシミュレーターを公開しています（登録不要・完全無料）👇
{WEB_TOOL_URL}

■ 2. コピペで使える！「{niche['title']}」専用AIプロンプト
ChatGPT / Claude / Gemini のどれでも使える構造化プロンプトです。以下のテキストをそのままコピーしてAIに貼り付けてください。

【命令書】
あなたは「{niche['title']}」の専門データアナリスト兼業務自動化エキスパートです。
以下の入力データを解析し、スプレッドシートへそのまま貼り付け可能なタブ区切り（TSV）形式で構造化して出力してください。
1. 前置きや挨拶は一切省き、データのみを出力すること
2. 異常値や確認が必要な項目には先頭に [要確認] タグを付与すること
3. 末尾に業務改善のネクストアクションを3行以内で提案すること

■ 3. GASでエラーが出た時の「3秒診断ツール」も無料公開中
「AIが出したGASコードをスプレッドシートに貼ったら赤字のエラー（TypeErrorや6分制限）が出た…」という方のために、エラー原因と修正済みコードを3秒で出力する無料ツールも公開しました👇
https://toproad-creator.github.io/autoflow-ai-ceo/gas-debugger.html

■ 4. 全10業種・50種類のプロンプト＆GAS完全版パック（¥1,980）
「最初からエラー対策・自動メール通知済みの完成品50種類をまとめて手に入れたい」という方向けに、全10カテゴリ・50選の完全版パッケージを公開しています。時給2,500円ならたった48分の時短で元が取れる買い切りパックです👇
{PAID_NOTE_URL}
"""
        hashtags = ["AI", "ChatGPT", "業務効率化", "GAS", "プロンプト"]
        out_file = os.path.join(MARKETING_DIR, f"free_note_lead_day{day}.txt")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"【タイトル】\n{title}\n\n【ハッシュタグ】\n{' '.join('#'+h for h in hashtags)}\n\n【本文】\n{body}")

        return {
            "day": day,
            "title": title,
            "hashtags": hashtags,
            "file_path": out_file,
            "body": body
        }

    def auto_publish_headless(self, article: dict) -> dict:
        existing = self.fetch_published_titles()
        for item in existing:
            if item["title"] == article["title"]:
                return {
                    "status": "already_published",
                    "url": item["url"],
                    "title": item["title"]
                }

        email = os.getenv("NOTE_EMAIL", "").strip()
        password = os.getenv("NOTE_PASSWORD", "").strip()
        if not email or not password:
            return {"status": "waiting_for_credentials", "message": ".env に NOTE_EMAIL と NOTE_PASSWORD が未設定です"}

        print("[Note Auto-Publisher] Starting automated Chrome login & publish...")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                channel="chrome",
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
                no_viewport=True
            )
            page = context.pages[0] if context.pages else context.new_page()

            # 1. ログイン確認＆自動ログイン
            page.goto("https://note.com/login", wait_until="networkidle", timeout=45000)
            time.sleep(2)
            if "login" in page.url:
                inputs = page.locator("input")
                if inputs.count() >= 2:
                    inputs.nth(0).click()
                    inputs.nth(0).press_sequentially(email, delay=40)
                    time.sleep(0.5)
                    inputs.nth(1).click()
                    inputs.nth(1).press_sequentially(password, delay=40)
                    time.sleep(1.0)
                    btn = page.locator('button:has-text("ログイン")').first
                    btn.click()
                    time.sleep(7)
                    page.screenshot(path=SCREENSHOT_PATH)

            # 2. トップページの「投稿」ボタンをクリック、または新規作成画面へ移動
            post_btn = page.locator('a:has-text("投稿"), button:has-text("投稿")').first
            if post_btn.is_visible():
                post_btn.click()
                time.sleep(5)
            else:
                page.goto("https://editor.note.com/new", wait_until="networkidle", timeout=45000)
                time.sleep(5)
            page.screenshot(path=SCREENSHOT_PATH)

            # 3. タイトル入力
            title_box = page.locator('textarea[placeholder*="タイトル"], [placeholder*="タイトル"], [data-placeholder*="タイトル"]').first
            title_box.wait_for(state="visible", timeout=45000)
            title_box.click()
            title_box.fill(article["title"])
            time.sleep(1)

            # 4. 本文入力
            body_box = page.locator('.ProseMirror, div[contenteditable="true"]').first
            body_box.click()
            page.keyboard.insert_text(article["body"])
            time.sleep(2)

            # 5. 公開に進む
            page.locator('button:has-text("公開に進む")').first.click()
            time.sleep(4)

            # 6. ハッシュタグ入力
            try:
                tag_input = page.locator('input[placeholder*="ハッシュタグ"], input[placeholder*="タグ"]').first
                if tag_input.is_visible(timeout=5000):
                    for tag in article["hashtags"]:
                        tag_input.click()
                        tag_input.fill(tag)
                        page.keyboard.press("Enter")
                        time.sleep(0.5)
            except Exception:
                pass

            time.sleep(1)
            page.screenshot(path=SCREENSHOT_PATH)

            # 7. 投稿するボタンをクリック
            final_btn = page.locator('button:has-text("投稿する"), button:has-text("公開")').last
            final_btn.click()
            time.sleep(7)
            page.screenshot(path=SCREENSHOT_PATH)
            final_url = page.url
            context.close()

            m = re.search(r"(n[a-z0-9]+)", final_url)
            public_url = f"https://note.com/toproad_1989/n/{m.group(1)}" if m else final_url
            return {"status": "published", "url": public_url, "title": article["title"], "screenshot": SCREENSHOT_PATH}

    def publish_daily_lead_if_needed(self, day: int, niches: list[dict]) -> dict:
        idx = (day - 5) % len(niches) if day >= 5 else 0
        art = self.generate_daily_free_lead_article(day=day, niche=niches[idx])
        return self.auto_publish_headless(art)


if __name__ == "__main__":
    from researcher_agent import ResearcherAgent
    niches = ResearcherAgent().run_market_analysis()["high_demand_niches"]
    agent = NoteAutoPublisherAgent()
    art = agent.generate_daily_free_lead_article(day=5, niche=niches[0])
    if "--auto-post" in sys.argv:
        res = agent.auto_publish_headless(art)
        print(json.dumps(res, ensure_ascii=False))
    else:
        print("Generated:", art["file_path"])
