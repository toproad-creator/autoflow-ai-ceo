import json
import os
import sys
import time
import urllib.request
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

sys.path.insert(0, os.path.dirname(__file__))
from thumbnail_generator import NoteThumbnailGenerator

PROFILE_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "note_browser_profile")
DATA_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "data")
WEB_TOOL_URL = "https://toproad-creator.github.io/autoflow-ai-ceo/"

PROFILE_BIO_140 = (
    "GAS×生成AIで、コピペ5分で使える業務自動化レシピと無料Webツールを開発・公開中。"
    "面倒な転記やデータ整理を仕組み化し、毎日の作業時間を削減する実践ガイドを発信しています👇 "
    f"{WEB_TOOL_URL}"
)


def fetch_public_profile() -> dict:
    req = urllib.request.Request(
        "https://note.com/api/v2/creators/toproad_1989",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8")).get("data", {})


def ensure_logged_in(page, target_url: str) -> bool:
    page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(6)
    is_logged_out = "login" in page.url or page.locator('a:has-text("ログイン")').first.is_visible(timeout=2000)
    if not is_logged_out:
        return True

    email = os.getenv("NOTE_EMAIL", "").strip()
    password = os.getenv("NOTE_PASSWORD", "").strip()
    if not email or not password:
        print("[SetupNoteProfile] Not logged in and NOTE_EMAIL/NOTE_PASSWORD missing.")
        return False

    page.goto("https://note.com/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    inputs = page.locator("input")
    if inputs.count() >= 2:
        inputs.nth(0).click()
        inputs.nth(0).press_sequentially(email, delay=40)
        time.sleep(0.5)
        inputs.nth(1).click()
        inputs.nth(1).press_sequentially(password, delay=40)
        time.sleep(1.0)
        page.locator('button:has-text("ログイン")').first.click()
        time.sleep(8)
        page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(6)

    if "login" in page.url:
        print(f"[SetupNoteProfile] Login could not complete automatically. Current URL: {page.url}")
        return False
    return True


def inspect_and_update_profile(inspect_only: bool = False) -> dict:
    gen = NoteThumbnailGenerator()
    avatar_path = gen.generate_profile_avatar()
    header_path = gen.generate_profile_header()
    print(f"[SetupNoteProfile] Images ready: avatar={avatar_path}, header={header_path}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            no_viewport=True,
        )
        page = context.pages[0] if context.pages else context.new_page()

        ok = ensure_logged_in(page, "https://note.com/toproad_1989")
        if not ok:
            page.screenshot(path=os.path.join(DATA_DIR, "note_profile_login_blocked.png"))
            context.close()
            return {"status": "login_blocked", "avatar_path": avatar_path, "header_path": header_path}

        # クリエイターページの「設定」ボタンをクリックしてプロフィール設定を開く（見つからなければ settings/profile へ）
        page.screenshot(path=os.path.join(DATA_DIR, "note_creator_home_inspect.png"))
        edit_btn = page.locator('button:has-text("設定"), a:has-text("設定")').first
        if edit_btn.is_visible(timeout=5000):
            print("[SetupNoteProfile] Found 設定 button on creator page, clicking...")
            edit_btn.click()
            time.sleep(5)
        else:
            print("[SetupNoteProfile] Navigating to settings/profile...")
            page.goto("https://note.com/settings/profile", wait_until="domcontentloaded", timeout=30000)
            time.sleep(8)

        page.screenshot(path=os.path.join(DATA_DIR, "note_profile_settings_inspect.png"))
        dom_info = page.evaluate(
            """() => {
                const inputs = Array.from(document.querySelectorAll('input, textarea')).map((el, idx) => ({
                    idx,
                    tag: el.tagName,
                    type: el.type || '',
                    name: el.name || '',
                    id: el.id || '',
                    placeholder: el.placeholder || '',
                    value: (el.value || '').slice(0, 60),
                    ariaLabel: el.getAttribute('aria-label') || ''
                }));
                const buttons = Array.from(document.querySelectorAll('button, [role="button"]')).map((b, idx) => {
                    const r = b.getBoundingClientRect();
                    return {
                        idx,
                        tag: b.tagName,
                        text: (b.innerText || '').trim().slice(0, 40),
                        ariaLabel: b.getAttribute('aria-label') || '',
                        x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)
                    };
                });
                return { url: location.href, inputs, buttons };
            }"""
        )

        if inspect_only:
            print(json.dumps(dom_info, ensure_ascii=False, indent=2))
            context.close()
            return {"status": "inspected", "dom_info": dom_info, "avatar_path": avatar_path, "header_path": header_path}

        def wait_form_unlocked():
            page.wait_for_function(
                "() => { const el = document.querySelector('textarea[name=\"editBiography\"]'); return el && !el.disabled; }",
                timeout=25000,
            )
            time.sleep(2)

        def confirm_crop_modal():
            for _ in range(2):
                modal = page.locator('[data-name="modal"]').last
                if modal.is_visible(timeout=4000):
                    save_in_modal = modal.locator('button:has-text("この画像を使う"), button:has-text("保存"), button:has-text("適用"), button:has-text("設定")').last
                    if save_in_modal.count() > 0:
                        save_in_modal.scroll_into_view_if_needed()
                        save_in_modal.click()
                        time.sleep(2)
                else:
                    break

        # 1. 表示名が Toproad のままであることを保証
        nick_input = page.locator('input[name="editNickname"]')
        bio_box = page.locator('textarea[name="editBiography"]')
        wait_form_unlocked()

        current_nick = nick_input.input_value(timeout=5000)
        if current_nick != "Toproad":
            nick_input.fill("Toproad")
            time.sleep(0.5)

        # 2. まず最初に自己紹介文（140字以内）を入力（Reactに確実に認識させる）
        bio_box.click()
        bio_box.fill("")
        bio_box.press_sequentially(PROFILE_BIO_140, delay=10)
        time.sleep(1)

        # 3. 次にヘッダー画像をアップロード（#headerImage）し、ロック解除まで完全に待つ
        header_input = page.locator('#headerImage')
        if header_input.count() > 0:
            header_input.set_input_files(header_path)
            time.sleep(2.5)
            confirm_crop_modal()
            wait_form_unlocked()

        # 4. 次にアイコン画像をアップロード（丸アイコンをクリック → モーダル操作 → ロック解除まで待つ）
        avatar_uploaded = False
        nick_box = nick_input.bounding_box()
        if nick_box:
            target_x = nick_box["x"] - 80
            target_y = nick_box["y"] + 25
            print(f"[SetupNoteProfile] Opening avatar modal at ({target_x}, {target_y})...")
            page.mouse.click(target_x, target_y)
            time.sleep(2.5)

            modal = page.locator('[data-name="modal"]').last
            if modal.is_visible(timeout=5000):
                modal_dom = modal.evaluate(
                    """(m) => ({
                        files: m.querySelectorAll('input[type="file"]').length,
                        buttons: Array.from(m.querySelectorAll('button')).map((b, i) => ({
                            i,
                            text: (b.innerText || '').trim(),
                            aria: b.getAttribute('aria-label') || '',
                            cls: (b.className || '').slice(0, 40)
                        }))
                    })"""
                )
                print("[SetupNoteProfile] Avatar modal DOM:", json.dumps(modal_dom, ensure_ascii=False))

                modal_file = modal.locator('input[type="file"]').first
                if modal_file.count() > 0:
                    modal_file.set_input_files(avatar_path)
                    avatar_uploaded = True
                    time.sleep(2.5)
                    confirm_crop_modal()
                    wait_form_unlocked()
                else:
                    # モーダル内のカメラ＋アイコン（アップロードボタン）を探す
                    first_icon_btn = modal.locator('button').first
                    if first_icon_btn.count() > 0:
                        try:
                            with page.expect_file_chooser(timeout=6000) as fc_info:
                                first_icon_btn.click()
                            fc_info.value.set_files(avatar_path)
                            avatar_uploaded = True
                            time.sleep(2.5)
                            confirm_crop_modal()
                            wait_form_unlocked()
                        except Exception as e:
                            print(f"[SetupNoteProfile] Modal icon click warning: {e}")

            if page.locator('[data-name="modal"]').last.is_visible(timeout=1500):
                confirm_crop_modal()
            if page.locator('[data-name="modal"]').last.is_visible(timeout=1000):
                cancel_btn = page.locator('[data-name="modal"] button:has-text("キャンセル")').last
                if cancel_btn.is_visible(timeout=1000):
                    cancel_btn.click()
                    time.sleep(1.5)
            wait_form_unlocked()

        # 5. 自己紹介文が維持されているか再確認し、ページ右下の「保存」ボタンをクリック
        if bio_box.input_value(timeout=5000).strip() != PROFILE_BIO_140.strip():
            bio_box.click()
            bio_box.fill("")
            bio_box.press_sequentially(PROFILE_BIO_140, delay=10)
            time.sleep(1)

        if nick_input.input_value(timeout=5000) != "Toproad":
            nick_input.fill("Toproad")
            time.sleep(0.5)

        page.screenshot(path=os.path.join(DATA_DIR, "note_profile_before_save.png"))
        save_btn = page.locator('button:has-text("保存")').last
        save_btn.scroll_into_view_if_needed()
        if save_btn.is_enabled(timeout=10000):
            save_btn.click()
            time.sleep(8)
        else:
            print("[SetupNoteProfile] Save button not enabled; check screenshot.")
        page.screenshot(path=os.path.join(DATA_DIR, "note_profile_after_save.png"))

        context.close()
        return {
            "status": "updated",
            "avatar_uploaded": avatar_uploaded,
            "avatar_path": avatar_path,
            "header_path": header_path,
        }


if __name__ == "__main__":
    inspect_only = "--inspect" in sys.argv
    res = inspect_and_update_profile(inspect_only=inspect_only)
    print(json.dumps({"status": res.get("status"), "public_profile": fetch_public_profile()}, ensure_ascii=False, indent=2))
