import html as html_lib
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from thumbnail_generator import NoteThumbnailGenerator

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
    """noteタイムライン集客用・無料お役立ち記事＆1280x670サムネイル画像の自動生成・自動投稿エージェント
    .env の NOTE_EMAIL / NOTE_PASSWORD を使用して、全自動ログイン＆アイキャッチ画像設定＆クリック可能なリンク付き記事公開を行う。
    """

    def __init__(self):
        os.makedirs(MARKETING_DIR, exist_ok=True)
        os.makedirs(PROFILE_DIR, exist_ok=True)
        self.thumb_gen = NoteThumbnailGenerator()

    def fetch_published_titles(self) -> list[dict]:
        try:
            req = urllib.request.Request(NOTE_CREATOR_API_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8")).get("data", {})
                return [
                    {
                        "key": c.get("key"),
                        "title": c.get("name"),
                        "eyecatch": c.get("eyecatch"),
                        "created_at": c.get("publishAt", ""),
                        "url": f"https://note.com/toproad_1989/n/{c.get('key')}"
                    }
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

        thumb_path = self.thumb_gen.generate_free_article_thumbnail(niche, day=day)
        return {
            "day": day,
            "title": title,
            "hashtags": hashtags,
            "file_path": out_file,
            "thumbnail_path": thumb_path,
            "body": body
        }

    def _body_to_rich_html(self, body_text: str) -> str:
        paragraphs = []
        for line in body_text.strip().split("\n"):
            escaped = html_lib.escape(line.strip())
            if not escaped:
                paragraphs.append("<p><br></p>")
            else:
                linked = re.sub(
                    r"(https://[^\s<]+)",
                    r'<a href="\1" target="_blank" rel="noopener">\1</a>',
                    escaped
                )
                paragraphs.append(f"<p>{linked}</p>")
        return "".join(paragraphs)

    def _insert_rich_body(self, page, body_text: str, replace_existing: bool = False):
        body_box = page.locator('.ProseMirror, div[contenteditable="true"]').first
        body_box.click()
        time.sleep(0.5)
        if replace_existing:
            page.keyboard.press("Control+A")
            time.sleep(0.3)
            page.keyboard.press("Backspace")
            time.sleep(0.5)

        rich_html = self._body_to_rich_html(body_text)
        page.evaluate(
            """([htmlStr, plainStr]) => {
                const editor = document.querySelector('.ProseMirror') || document.querySelector('div[contenteditable="true"]');
                editor.focus();
                const dt = new DataTransfer();
                dt.setData('text/html', htmlStr);
                dt.setData('text/plain', plainStr);
                const pasteEvent = new ClipboardEvent('paste', {
                    bubbles: true,
                    cancelable: true,
                    clipboardData: dt
                });
                editor.dispatchEvent(pasteEvent);
            }""",
            [rich_html, body_text]
        )
        time.sleep(2)

    def _upload_eyecatch(self, page, thumbnail_path: str) -> bool:
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            return False
        for attempt in range(2):
            try:
                page.wait_for_selector('button[data-id="ButtonIcon"]', timeout=8000)
                btns = page.locator('button[data-id="ButtonIcon"]')
                for i in range(btns.count()):
                    b = btns.nth(i)
                    box = b.bounding_box()
                    if box and 40 < box["y"] < 260:
                        b.click()
                        break
                time.sleep(2.0)
                upload_btn = page.locator('button:has-text("画像をアップロード")').first
                if upload_btn.is_visible(timeout=5000):
                    with page.expect_file_chooser(timeout=10000) as fc_info:
                        upload_btn.click()
                    fc_info.value.set_files(thumbnail_path)
                    time.sleep(3.5)
                    save_crop_btn = page.locator('button:has-text("保存")').last
                    if save_crop_btn.is_visible(timeout=8000):
                        save_crop_btn.click()
                        time.sleep(6)
                    return True
            except Exception as e:
                print(f"[Note Auto-Publisher] Eyecatch upload attempt {attempt + 1} warning: {e}")
                time.sleep(2)
        return False

    def fix_existing_free_article_links(self, note_key: str, niche: dict, day: int) -> dict:
        art = self.generate_daily_free_lead_article(day=day, niche=niche)
        print(f"[Note Auto-Publisher] Upgrading links & thumbnail in {note_key} ({art['title'][:25]}...)...")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                channel="chrome",
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
                no_viewport=True
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(f"https://editor.note.com/notes/{note_key}/edit/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            if art.get("thumbnail_path"):
                self._upload_eyecatch(page, art["thumbnail_path"])
            self._insert_rich_body(page, art["body"], replace_existing=True)
            page.screenshot(path=SCREENSHOT_PATH)

            pub_step = page.locator('button:has-text("公開に進む")').first
            if pub_step.is_visible():
                pub_step.click()
                time.sleep(4)
                final_btn = page.locator('button:has-text("更新する"), button:has-text("投稿する"), button:has-text("公開")').last
                if final_btn.is_visible():
                    final_btn.click()
                    time.sleep(6)
            page.screenshot(path=SCREENSHOT_PATH)
            context.close()
            return {"note_key": note_key, "url": f"https://note.com/toproad_1989/n/{note_key}"}

    def auto_publish_headless(self, article: dict) -> dict:
        existing = self.fetch_published_titles()
        for item in existing:
            if item["title"] == article["title"]:
                return {
                    "status": "already_published",
                    "url": item["url"],
                    "title": item["title"],
                    "thumbnail_path": article.get("thumbnail_path")
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

            # 1. 直接新規記事エディタへ移動し、未ログインならログイン画面で認証する
            page.goto("https://editor.note.com/new", wait_until="domcontentloaded", timeout=30000)
            time.sleep(4)
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
                    page.goto("https://editor.note.com/new", wait_until="domcontentloaded", timeout=30000)
                    time.sleep(5)

            page.screenshot(path=SCREENSHOT_PATH)

            # 2. アイキャッチ（サムネイル画像 1280x670px）を自動アップロード
            if article.get("thumbnail_path"):
                self._upload_eyecatch(page, article["thumbnail_path"])

            # 3. タイトル入力
            title_box = page.locator('textarea[placeholder*="タイトル"], [placeholder*="タイトル"], [data-placeholder*="タイトル"]').first
            title_box.wait_for(state="visible", timeout=30000)
            title_box.click()
            title_box.fill(article["title"])
            time.sleep(1)

            # 4. 本文入力（クリック可能なHTMLリンク付きでペースト）
            self._insert_rich_body(page, article["body"], replace_existing=False)

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

            m = re.search(r"/notes/(n[a-z0-9]+)", final_url)
            if m:
                public_url = f"https://note.com/toproad_1989/n/{m.group(1)}"
            else:
                latest_notes = self.fetch_published_titles()
                public_url = latest_notes[0]["url"] if latest_notes else final_url
            return {
                "status": "published",
                "url": public_url,
                "title": article["title"],
                "thumbnail_path": article.get("thumbnail_path"),
                "screenshot": SCREENSHOT_PATH
            }

    def publish_daily_lead_if_needed(self, day: int, niches: list[dict]) -> dict:
        existing = self.fetch_published_titles()
        today_str = datetime.now().astimezone().strftime("%Y-%m-%d")
        for item in existing:
            if item.get("created_at", "").startswith(today_str) and item.get("key") != "n5d0e28a74f91":
                return {
                    "status": "already_published_today",
                    "url": item["url"],
                    "title": item["title"]
                }

        existing_titles = {item["title"] for item in existing}
        target_niche = niches[0]
        for n in niches:
            candidate_title = f"【無料コピペOK】{n['title']}をAIとGASで自動化して月{n['avg_hours_saved_monthly']}時間浮かす実践レシピ"
            if candidate_title not in existing_titles:
                target_niche = n
                break

        art = self.generate_daily_free_lead_article(day=day, niche=target_niche)
        return self.auto_publish_headless(art)


if __name__ == "__main__":
    from researcher_agent import ResearcherAgent
    niches = ResearcherAgent().run_market_analysis()["high_demand_niches"]
    agent = NoteAutoPublisherAgent()
    if "--auto-post" in sys.argv:
        res = agent.publish_daily_lead_if_needed(day=8, niches=niches)
        print(json.dumps(res, ensure_ascii=False))
    elif "--fix-all-links" in sys.argv:
        r1 = agent.fix_existing_free_article_links("n70171b631e61", niches[0], day=5)
        r2 = agent.fix_existing_free_article_links("n9a7bd90cf282", niches[1], day=7)
        r3 = agent.fix_existing_free_article_links("n2b36747c935d", niches[2], day=8)
        print(json.dumps({"fixed": [r1, r2, r3]}, ensure_ascii=False))
    else:
        art = agent.generate_daily_free_lead_article(day=8, niche=niches[2])
        print("Generated:", art["file_path"], art["thumbnail_path"])
