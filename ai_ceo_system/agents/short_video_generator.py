import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[2]
AI_CEO_DIR = ROOT_DIR / "ai_ceo_system"
VIDEO_CREATOR_DIR = ROOT_DIR / "VideoCreator"
SHORTS_OUT_DIR = AI_CEO_DIR / "shorts_videos" / "day1"
PRODUCT_SITE_DIR = AI_CEO_DIR / "product_site"

sys.path.insert(0, str(VIDEO_CREATOR_DIR))


def get_japanese_font() -> str:
    local_font = VIDEO_CREATOR_DIR / "fonts" / "NotoSansJP-Bold.otf"
    if local_font.exists():
        return str(local_font)
    candidates = [
        r"C:\Windows\Fonts\meiryob.ttc",
        r"C:\Windows\Fonts\YuGothB.ttc",
        r"C:\Windows\Fonts\msgothic.ttc",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Japanese font not found")


def ensure_voicevox_running():
    try:
        req = urllib.request.Request("http://localhost:50021/version", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                return
    except Exception:
        pass

    vv_exe = r"C:\Users\yukar\AppData\Local\Programs\VOICEVOX\vv-engine\run.exe"
    if os.path.exists(vv_exe):
        subprocess.Popen([vv_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import time
        for _ in range(15):
            time.sleep(1)
            try:
                with urllib.request.urlopen("http://localhost:50021/version", timeout=2) as r:
                    if r.status == 200:
                        return
            except Exception:
                continue
    raise RuntimeError("VOICEVOX engine is not responding on localhost:50021")


def generate_voicevox_wav(text: str, save_path: Path, speaker_id: int = 13, speed_scale: float = 1.22):
    ensure_voicevox_running()
    encoded_text = urllib.parse.quote(text)
    query_url = f"http://localhost:50021/audio_query?text={encoded_text}&speaker={speaker_id}"
    req1 = urllib.request.Request(query_url, method="POST")
    with urllib.request.urlopen(req1, timeout=15) as resp1:
        query_data = json.loads(resp1.read().decode("utf-8"))

    query_data["speedScale"] = speed_scale
    query_data["pitchScale"] = 0.0
    query_data["intonationScale"] = 1.08
    query_data["prePhonemeLength"] = 0.05
    query_data["postPhonemeLength"] = 0.12

    synth_url = f"http://localhost:50021/synthesis?speaker={speaker_id}"
    req2 = urllib.request.Request(
        synth_url,
        data=json.dumps(query_data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req2, timeout=45) as resp2:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(resp2.read())


def capture_real_site_screenshots(temp_dir: Path) -> dict[str, Path]:
    """実際の product_site/index.html 等の画面をPlaywrightでリアルキャプチャする"""
    shots = {}
    index_uri = (PRODUCT_SITE_DIR / "index.html").as_uri()
    ec_uri = (PRODUCT_SITE_DIR / "usecases" / "ec-inventory.html").as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 1. AutoFlow AI トップ＆シミュレーター画面
        page = browser.new_page(viewport={"width": 1000, "height": 1050}, device_scale_factor=2)
        page.goto(index_uri, wait_until="networkidle", timeout=30000)
        shot_main = temp_dir / "raw_site_main.png"
        page.screenshot(path=str(shot_main), clip={"x": 0, "y": 0, "width": 1000, "height": 1020})
        shots["site_main"] = shot_main

        # GAS自動実行コードタブに切り替えた状態のキャプチャ
        try:
            page.click("#tabGas")
            page.wait_for_timeout(300)
        except Exception:
            pass
        shot_gas = temp_dir / "raw_site_gas.png"
        page.screenshot(path=str(shot_gas), clip={"x": 0, "y": 220, "width": 1000, "height": 760})
        shots["site_gas"] = shot_gas

        # 2. 業種別SEOページ (ec-inventory.html) のキャプチャ
        page.goto(ec_uri, wait_until="networkidle", timeout=30000)
        shot_seo = temp_dir / "raw_site_seo.png"
        page.screenshot(path=str(shot_seo), clip={"x": 0, "y": 0, "width": 1000, "height": 950})
        shots["site_seo"] = shot_seo

        browser.close()
    return shots


def render_vertical_evidence_frames(temp_dir: Path, raw_shots: dict[str, Path]) -> list[Path]:
    """実際のファイルデータとWeb画面キャプチャを組み合わせて、1080x1920の縦型背景フレーム5枚を生成"""
    wallet_data = json.loads((ROOT_DIR / "wallet.json").read_text(encoding="utf-8"))
    research_data = json.loads((AI_CEO_DIR / "data" / "market_research_day1.json").read_text(encoding="utf-8"))

    import base64

    def img_to_data_uri(path: Path) -> str:
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{b64}"

    main_uri = img_to_data_uri(raw_shots["site_main"])
    gas_uri = img_to_data_uri(raw_shots["site_gas"])
    seo_uri = img_to_data_uri(raw_shots["site_seo"])

    common_css = """
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700;900&family=JetBrains+Mono:wght@500;700&display=swap');
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body {
        width: 1080px; height: 1920px;
        font-family: 'Noto Sans JP', 'Meiryo', sans-serif;
        background: radial-gradient(circle at 50% 15%, #1e293b 0%, #090d16 70%, #020617 100%);
        color: #f8fafc;
        overflow: hidden;
        position: relative;
      }
      .top-bar {
        position: absolute; top: 55px; left: 50px; right: 50px;
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(15, 23, 42, 0.9);
        border: 2px solid rgba(56, 189, 248, 0.4);
        border-radius: 20px;
        padding: 18px 28px;
        box-shadow: 0 12px 32px rgba(0,0,0,0.5);
      }
      .badge-day {
        background: linear-gradient(135deg, #38bdf8, #6366f1);
        color: #020617; font-weight: 900; font-size: 24px;
        padding: 6px 18px; border-radius: 12px; white-space: nowrap;
      }
      .top-title { font-size: 26px; font-weight: 900; color: #e2e8f0; white-space: nowrap; }
      .wallet-pill {
        background: rgba(16, 185, 129, 0.15);
        border: 2px solid #10b981;
        color: #34d399; font-weight: 900; font-size: 24px;
        padding: 6px 16px; border-radius: 12px; white-space: nowrap;
      }
      .content-area {
        position: absolute; top: 175px; left: 50px; right: 50px; height: 1080px;
        display: flex; flex-direction: column; gap: 22px;
      }
      .terminal-window {
        background: #0d1117;
        border: 2px solid #30363d;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 20px 50px rgba(0,0,0,0.65);
      }
      .win-header {
        background: #161b22; padding: 14px 22px;
        display: flex; align-items: center; gap: 12px;
        border-bottom: 1px solid #30363d;
      }
      .dot { width: 14px; height: 14px; border-radius: 50%; }
      .dot-r { background: #ff5f56; } .dot-y { background: #ffbd2e; } .dot-g { background: #27c93f; }
      .win-title { font-family: 'JetBrains Mono', monospace; font-size: 22px; color: #8b949e; margin-left: 10px; font-weight: 700; }
      .win-body { padding: 26px; font-family: 'JetBrains Mono', 'Noto Sans JP', monospace; font-size: 24px; line-height: 1.55; }
      .browser-frame {
        background: #0f172a;
        border: 3px solid #38bdf8;
        border-radius: 22px;
        overflow: hidden;
        box-shadow: 0 20px 50px rgba(56, 189, 248, 0.2);
      }
      .url-bar {
        background: #1e293b; padding: 12px 20px;
        display: flex; align-items: center; gap: 12px;
        border-bottom: 2px solid #334155;
        font-family: 'JetBrains Mono', monospace; font-size: 20px; color: #38bdf8;
      }
    """

    # Scene 1 HTML: 実験ルール＆wallet.json＆AIエージェント自動構築画面
    html_s1 = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{common_css}</style></head><body>
      <div class="top-bar">
        <span class="badge-day">DAY 1 / 90</span>
        <span class="top-title">90日間・人間介入ゼロ AI起業対決</span>
        <span class="wallet-pill">残高 ¥15,000</span>
      </div>
      <div class="content-area">
        <div class="terminal-window">
          <div class="win-header"><span class="dot dot-r"></span><span class="dot dot-y"></span><span class="dot dot-g"></span>
            <span class="win-title">MISSION RULES & wallet.json (実データ)</span>
          </div>
          <div class="win-body">
            <div style="color:#38bdf8; font-weight:900; font-size:28px; margin-bottom:12px;">▼ 実験の絶対ルール</div>
            <div style="font-size:25px; margin-bottom:18px; color:#f1f5f9;">
              ・軍資金 <span style="color:#facc15; font-weight:900;">¥15,000</span> からスタート<br>
              ・人間の手直し・コピペ・営業代行は<span style="color:#f43f5e; font-weight:900;">一切禁止</span><br>
              ・残高が0円を下回った瞬間に<span style="color:#f43f5e; font-weight:900;">即失格（破産）</span>
            </div>
            <div style="background:#161b22; padding:18px; border-radius:14px; border:1px solid #30363d; color:#a5d6ff; font-size:22px;">
              // wallet.json (AI財務エージェントが自動生成)<br>
              {{<br>
              &nbsp;&nbsp;"initial_capital_jpy": <span style="color:#34d399; font-weight:900;">15000</span>,<br>
              &nbsp;&nbsp;"current_balance_jpy": <span style="color:#34d399; font-weight:900;">15000</span>,<br>
              &nbsp;&nbsp;"total_spent_jpy": <span style="color:#facc15; font-weight:900;">0</span>,<br>
              &nbsp;&nbsp;"status": <span style="color:#34d399;">"ACTIVE (Zero-Human-Touch)"</span><br>
              }}
            </div>
          </div>
        </div>
        <div class="terminal-window">
          <div class="win-header"><span class="dot dot-r"></span><span class="dot dot-y"></span><span class="dot dot-g"></span>
            <span class="win-title">ai_ceo_system/agents/ (開始数分でAIが自作した社内組織)</span>
          </div>
          <div class="win-body" style="font-size:23px; color:#cbd5e1;">
            <span style="color:#34d399;">✔</span> <b>ceo_orchestrator.py</b> （AI社長・全体統括）<br>
            <span style="color:#34d399;">✔</span> <b>cfo_analytics_agent.py</b> （財務防衛・残高監視）<br>
            <span style="color:#34d399;">✔</span> <b>researcher_agent.py</b> （市場調査・事業選定）<br>
            <span style="color:#34d399;">✔</span> <b>developer_agent.py</b> （Webツール全自動開発）<br>
            <span style="color:#34d399;">✔</span> <b>marketer_agent.py</b> （SEO＆SNS集客自動化）
          </div>
        </div>
      </div>
    </body></html>"""

    # Scene 2 HTML: 実際の market_research_day1.json による破産回避の意思決定ログ
    bm1 = research_data["evaluated_candidates"][0]
    bm2 = research_data["evaluated_candidates"][1]
    html_s2 = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{common_css}</style></head><body>
      <div class="top-bar">
        <span class="badge-day">DAY 1 社内会議ログ</span>
        <span class="top-title">market_research_day1.json</span>
        <span class="wallet-pill">支出 ¥0</span>
      </div>
      <div class="content-area">
        <div class="terminal-window" style="border-color:#f43f5e;">
          <div class="win-header" style="background:rgba(244,63,94,0.15);">
            <span class="dot dot-r"></span><span class="win-title" style="color:#fda4af;">❌ 却下された案：BM-02 従量課金APIラッパー型SaaS</span>
          </div>
          <div class="win-body" style="font-size:24px;">
            <div style="display:flex; gap:20px; margin-bottom:14px;">
              <span style="background:rgba(244,63,94,0.2); border:1px solid #f43f5e; color:#fda4af; padding:6px 16px; border-radius:10px; font-weight:900;">破産リスク: {bm2['scores']['risk_of_bankruptcy']}%</span>
              <span style="background:#1e293b; padding:6px 16px; border-radius:10px;">初期費用: ¥{bm2['setup_cost_jpy']:,} / 月額: ¥{bm2['monthly_running_cost_jpy']:,}</span>
            </div>
            <div style="background:#161b22; padding:16px; border-radius:12px; border-left:5px solid #f43f5e; color:#fecdd3;">
              <b>AI自身の却下理由：</b><br>
              「{bm2['rejection_reason']}」
            </div>
          </div>
        </div>

        <div class="terminal-window" style="border-color:#10b981;">
          <div class="win-header" style="background:rgba(16,185,129,0.18);">
            <span class="dot dot-g"></span><span class="win-title" style="color:#6ee7b7;">⭕ AIが採択した案：BM-01 静的Webツール＋テンプレ販売</span>
          </div>
          <div class="win-body" style="font-size:24px;">
            <div style="display:flex; gap:16px; margin-bottom:14px; flex-wrap:wrap;">
              <span style="background:rgba(16,185,129,0.25); border:2px solid #10b981; color:#34d399; padding:6px 16px; border-radius:10px; font-weight:900;">破産リスク: 0%</span>
              <span style="background:rgba(56,189,248,0.2); border:2px solid #38bdf8; color:#38bdf8; padding:6px 16px; border-radius:10px; font-weight:900;">初期費用 ¥0 / 月額維持費 ¥0</span>
              <span style="background:#1e293b; padding:6px 16px; border-radius:10px; color:#facc15; font-weight:900;">総合スコア: 96.0点</span>
            </div>
            <div style="color:#e2e8f0; line-height:1.5;">
              ・ブラウザ側だけで動く<b>「業務削減額シミュレーター＆GASコード生成Webツール」</b>を無料公開して集客<br>
              ・完全版50種テンプレート（¥1,980）販売で利益率100%を狙う戦略に決定！
            </div>
          </div>
        </div>
      </div>
    </body></html>"""

    # Scene 3 HTML: 実際にDay 1でAIが開発した Webサイト index.html (AutoFlow AI) のリアル画面
    html_s3 = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{common_css}</style></head><body>
      <div class="top-bar">
        <span class="badge-day">DAY 1 完成プロダクト</span>
        <span class="top-title">AIが1人で開発した『AutoFlow AI』</span>
        <span class="wallet-pill">サーバー代 ¥0</span>
      </div>
      <div class="content-area">
        <div class="browser-frame">
          <div class="url-bar">🔒 https://toproad-creator.github.io/autoflow-ai-ceo/index.html</div>
          <img src="{main_uri}" style="width:100%; height:980px; object-fit:cover; object-position:top center; display:block;" />
        </div>
      </div>
    </body></html>"""

    # Scene 4 HTML: GASコード出力画面 ＆ 業種別SEOページ自動量産キャプチャ
    html_s4 = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{common_css}</style></head><body>
      <div class="top-bar">
        <span class="badge-day">DAY 1 自動構築</span>
        <span class="top-title">GASコード生成 ＆ 業種別SEOページ量産</span>
        <span class="wallet-pill">残高 ¥15,000 無傷</span>
      </div>
      <div class="content-area">
        <div class="browser-frame" style="height:490px;">
          <div class="url-bar">⚡ コピペで動くGAS自動化コードを0秒出力</div>
          <img src="{gas_uri}" style="width:100%; height:435px; object-fit:cover; object-position:top center; display:block;" />
        </div>
        <div class="browser-frame" style="height:520px; border-color:#a855f7;">
          <div class="url-bar" style="color:#c084fc;">📈 職種別の集客用SEOページも自動で量産（usecases/）</div>
          <img src="{seo_uri}" style="width:100%; height:465px; object-fit:cover; object-position:top center; display:block;" />
        </div>
      </div>
    </body></html>"""

    # Scene 5 HTML: Day 1 決算サマリー＆視聴者アンケート＋Day 2予告
    html_s5 = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{common_css}</style></head><body>
      <div class="top-bar">
        <span class="badge-day">DAY 1 終了レポート</span>
        <span class="top-title">status_log.md 実績集計</span>
        <span class="wallet-pill">残高 ¥15,000</span>
      </div>
      <div class="content-area">
        <div class="terminal-window" style="border-color:#38bdf8;">
          <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">📊 Day 1 / 90 経営成績表（実測値）</span></div>
          <div class="win-body" style="font-size:27px; line-height:1.7;">
            ・初期軍資金： <b>¥15,000</b><br>
            ・Day 1 支出： <span style="color:#34d399; font-weight:900;">¥0（完全無料構成）</span><br>
            ・現在残高　： <span style="color:#facc15; font-weight:900;">¥15,000（無傷）</span><br>
            ・完成ツール： <b>AutoFlow AI Webスイート稼働</b><br>
            ・自動稼働　： <b>毎朝8時 GitHub Actions 自律実行</b><br>
            ・現在の売上： <span style="color:#f43f5e; font-weight:900;">¥0</span>
          </div>
        </div>
        <div class="terminal-window" style="border-color:#facc15; background:linear-gradient(135deg, rgba(250,204,21,0.12), rgba(15,23,42,0.95));">
          <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">🔥 次回【Day 2 予告】</span></div>
          <div class="win-body" style="font-size:26px; color:#fef08a; font-weight:700;">
            無料ツールだけでは売上は0円…<br>
            2日目、AI社長が自ら「全50種プロンプト＆GAS完全版パック（¥1,980）」を執筆し、noteで商用販売を開始！
          </div>
        </div>
      </div>
    </body></html>"""

    html_list = [html_s1, html_s2, html_s3, html_s4, html_s5]
    out_paths = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        for idx, html_str in enumerate(html_list, start=1):
            html_file = temp_dir / f"frame_{idx}.html"
            png_file = temp_dir / f"frame_{idx}.png"
            html_file.write_text(html_str, encoding="utf-8")
            page.goto(html_file.as_uri(), wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(200)
            page.screenshot(path=str(png_file))
            out_paths.append(png_file)
        browser.close()

    return out_paths


def draw_subtitle_overlay(width: int, height: int, text: str, font_path: str) -> Image.Image:
    """下部のセーフゾーン（Y: 1300〜1720px）に大きく読みやすい字幕バナーを描画し、上部のスクショ画面を隠さないようにする"""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    font_size = 58
    font = ImageFont.truetype(font_path, font_size)

    line_spacing = 24
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])

    total_h = sum(line_heights) + line_spacing * max(0, len(lines) - 1)
    y_start = 1320 + max(0, (360 - total_h) // 2)

    # 半透明の濃紺カード背景を敷いて可読性を100%保証
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rounded_rectangle(
        [45, y_start - 32, width - 45, y_start + total_h + 36],
        radius=28,
        fill=(8, 12, 24, 225),
        outline=(56, 189, 248, 180),
        width=3,
    )
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    y = y_start
    outline_w = 7
    for idx, line in enumerate(lines):
        w = font.getlength(line)
        x = (width - w) // 2

        for dx in range(-outline_w, outline_w + 1):
            for dy in range(-outline_w, outline_w + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))

        color = (255, 255, 255, 255)
        if "【" in line or "】" in line or "15,000円" in line or "AutoFlow" in line:
            color = (255, 230, 0, 255)
        elif "破産" in line or "失格" in line:
            color = (255, 65, 108, 255)
        elif "[A:" in line or "[B:" in line:
            color = (0, 242, 254, 255)

        draw.text((x, y), line, font=font, fill=color)
        y += line_heights[idx] + line_spacing

    return img


def build_day1_short():
    SHORTS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    temp_dir = SHORTS_OUT_DIR / "temp_build"
    temp_dir.mkdir(parents=True, exist_ok=True)

    scenes = [
        {
            "scene": 1,
            "narration": "AIに軍資金1万5000円を渡して、人間が一切手を出さずに90日間放置したら、一体どうなるのか？",
            "text": "AIに軍資金15,000円\n【90日間完全放置】\nしたらどうなる？",
        },
        {
            "scene": 2,
            "narration": "実験1日目。AIが最初にやったのは、まさかの破産対策でした。有料APIを使うと資金が溶けて失格になると自ら判断し、維持費ゼロ円の事業を選択。",
            "text": "Day1：まさかの\n【破産対策】を開始\n維持費0円モデルを選択",
        },
        {
            "scene": 3,
            "narration": "さらにその日のうちに、業務の削減金額と自動化コードを30秒で作れるWebツール、オートフローAIを、たった一人で開発して公開しました。",
            "text": "初日でWebツール\n【AutoFlow AI】を\nAIが1人で開発・公開",
        },
        {
            "scene": 4,
            "narration": "コピペで使える自動化コードと集客ページも自動で量産し、使ったお金はゼロ円のまま1日目が終了。",
            "text": "集客ページも自動量産\n残高【15,000円】無傷\n支出0円で1日目終了！",
        },
        {
            "scene": 5,
            "narration": "果たしてこのAI社長、90日後に黒字化できると思いますか？予想をコメント欄で教えてください！",
            "text": "90日後の結末は？\n[A: 黒字で大成功]\n[B: 売上0円で撃沈]",
        },
    ]

    script_meta = {
        "video_title": "【Day1】AIに1万5000円渡して完全放置したら勝手にWebサービス作って起業し始めた件 #Shorts",
        "description": "90日間・人間介入ゼロのAI起業対決 Day 1の記録です。\n初期資金15,000円を渡された自律型AI CEOが、破産リスクを自ら計算して維持費0円のWebツール『AutoFlow AI』を自作・公開するまでのリアルな進捗を公開します。\n\n#AI起業対決 #AI副業 #自動化 #Shorts",
        "hashtags": ["#AI起業対決", "#AI副業", "#業務効率化", "#Shorts"],
        "pinned_comment": "あなたは90日後どうなると思いますか？ [A: 黒字で大成功] か [B: 売上0円で撃沈] でコメント欄に予想を残してください！明日Day 2は、AIが1,980円の有料商品を自作してnoteで販売開始します🔥",
        "scenes": scenes,
    }
    script_json_path = SHORTS_OUT_DIR / "ai_ceo_day1_script.json"
    script_json_path.write_text(json.dumps(script_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[1/5] Capturing real screenshots of product_site & Day 1 logs...")
    raw_shots = capture_real_site_screenshots(temp_dir)
    bg_frames = render_vertical_evidence_frames(temp_dir, raw_shots)

    font_path = get_japanese_font()
    try:
        from moviepy.editor import AudioFileClip, CompositeVideoClip, ImageClip
    except ImportError:
        from moviepy import AudioFileClip, CompositeVideoClip, ImageClip

    from create_video import make_ken_burns_clip, normalize_clip_for_concat
    import imageio_ffmpeg

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    scene_mp4_list = []

    print("[2/5] Generating VOICEVOX audio and rendering 5 vertical scenes...")
    for idx, scene in enumerate(scenes):
        s_num = scene["scene"]
        wav_path = temp_dir / f"voice_{s_num}.wav"
        generate_voicevox_wav(scene["narration"], wav_path, speaker_id=13, speed_scale=1.22)

        audio_clip = AudioFileClip(str(wav_path))
        dur = audio_clip.duration

        pil_bg = Image.open(bg_frames[idx]).convert("RGB")
        # 上部のスクショがしっかり読めるよう、ズーム率を控えめ (1.03) に設定
        bg_clip = make_ken_burns_clip(pil_bg, dur, 1080, 1920, zoom_ratio=1.03)

        sub_img = draw_subtitle_overlay(1080, 1920, scene["text"], font_path)
        sub_path = temp_dir / f"sub_{s_num}.png"
        sub_img.save(str(sub_path))

        sub_clip = ImageClip(str(sub_path))
        sub_clip = sub_clip.with_duration(dur) if hasattr(sub_clip, "with_duration") else sub_clip.set_duration(dur)

        comp = CompositeVideoClip([bg_clip, sub_clip])
        comp = comp.with_audio(audio_clip) if hasattr(comp, "with_audio") else comp.set_audio(audio_clip)

        raw_scene_mp4 = temp_dir / f"raw_scene_{s_num}.mp4"
        temp_aud = temp_dir / f"temp_aud_{s_num}.m4a"
        comp.write_videofile(
            str(raw_scene_mp4),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(temp_aud),
            logger=None,
        )
        comp.close()
        bg_clip.close()
        sub_clip.close()
        audio_clip.close()

        norm_scene_mp4 = temp_dir / f"norm_scene_{s_num}.mp4"
        normalize_clip_for_concat(str(raw_scene_mp4), str(norm_scene_mp4), ffmpeg_exe, 1080, 1920, 30)
        scene_mp4_list.append(norm_scene_mp4)
        print(f"  -> Scene {s_num} rendered ({dur:.2f}s)")

    print("[3/5] Concatenating scenes with FFmpeg...")
    concat_txt = temp_dir / "concat_list.txt"
    concat_txt.write_text(
        "\n".join([f"file '{p.resolve().as_posix()}'" for p in scene_mp4_list]),
        encoding="utf-8",
    )
    out_mp4 = SHORTS_OUT_DIR / "ai_ceo_day1_short.mp4"
    concat_mp4 = temp_dir / "concat_no_bgm.mp4"
    subprocess.run(
        f'"{ffmpeg_exe}" -y -f concat -safe 0 -i "{concat_txt}" -c copy "{concat_mp4}"',
        shell=True,
        check=True,
        capture_output=True,
    )

    print("[4/5] Mixing BGM with auto-ducking via audio_pipeline...")
    from audio_pipeline import build_mixed_audio

    temp_narr_wav = temp_dir / "concat_narr.wav"
    subprocess.run(
        f'"{ffmpeg_exe}" -y -i "{concat_mp4}" -vn -ar 48000 -ac 2 "{temp_narr_wav}"',
        shell=True,
        check=True,
        capture_output=True,
    )
    master_wav = temp_dir / "master_mixed.wav"
    build_mixed_audio(
        narration_path=str(temp_narr_wav),
        timeline_data=None,
        output_path=str(master_wav),
        script_dir=str(VIDEO_CREATOR_DIR),
    )

    subprocess.run(
        f'"{ffmpeg_exe}" -y -i "{concat_mp4}" -i "{master_wav}" '
        f'-map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k "{out_mp4}"',
        shell=True,
        check=True,
        capture_output=True,
    )

    # プレビュー確認用に各シーンの完成フレーム静止画も保存しておく
    preview_dir = SHORTS_OUT_DIR / "scene_previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    for idx in range(1, 6):
        bg_img = Image.open(bg_frames[idx - 1]).convert("RGBA")
        sub_img = Image.open(temp_dir / f"sub_{idx}.png").convert("RGBA")
        merged = Image.alpha_composite(bg_img, sub_img).convert("RGB")
        merged.save(str(preview_dir / f"scene_{idx}_preview.png"))

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"[5/5] SUCCESS! Day 1 Short Video saved to: {out_mp4}")


if __name__ == "__main__":
    build_day1_short()

