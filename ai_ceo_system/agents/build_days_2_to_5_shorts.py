import base64
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[2]
AI_CEO_DIR = ROOT_DIR / "ai_ceo_system"
VIDEO_CREATOR_DIR = ROOT_DIR / "VideoCreator"
PRODUCT_SITE_DIR = AI_CEO_DIR / "product_site"

sys.path.insert(0, str(AI_CEO_DIR / "agents"))
sys.path.insert(0, str(VIDEO_CREATOR_DIR))

from short_video_generator import (
    draw_subtitle_overlay,
    generate_voicevox_wav,
    get_japanese_font,
)


def img_to_data_uri(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def capture_all_product_screenshots(temp_dir: Path) -> dict[str, str]:
    """Day 2〜Day 5で登場する実際のWebページとサムネイル画像をキャプチャしてData URI化する"""
    temp_dir.mkdir(parents=True, exist_ok=True)
    uris = {}

    pages_to_shot = {
        "pro_pack": (PRODUCT_SITE_DIR / "pro-pack.html", 0, 980),
        "gas_debugger": (PRODUCT_SITE_DIR / "gas-debugger.html", 0, 980),
        "prompt_builder": (PRODUCT_SITE_DIR / "prompt-builder.html", 0, 980),
        "free_templates": (PRODUCT_SITE_DIR / "free-templates.html", 0, 980),
        "index_bottom": (PRODUCT_SITE_DIR / "index.html", 520, 960),
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1000, "height": 1600}, device_scale_factor=2)
        for key, (html_path, y_off, h_clip) in pages_to_shot.items():
            page.goto(html_path.as_uri(), wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(200)
            out_png = temp_dir / f"shot_{key}.png"
            page.screenshot(path=str(out_png), clip={"x": 0, "y": y_off, "width": 1000, "height": h_clip})
            uris[key] = img_to_data_uri(out_png)
        browser.close()

    # 既存のサムネイル・自動投稿証拠キャプチャもData URI化
    paid_thumb = AI_CEO_DIR / "data" / "thumbnails" / "thumb_paid_autoflow_pro_50.png"
    free_thumb = AI_CEO_DIR / "data" / "thumbnails" / "thumb_free_day5_ec-inventory.png"
    note_auto = AI_CEO_DIR / "data" / "note_autopost_latest.png"

    if paid_thumb.exists():
        uris["paid_thumb"] = img_to_data_uri(paid_thumb)
    if free_thumb.exists():
        uris["free_thumb"] = img_to_data_uri(free_thumb)
    if note_auto.exists():
        uris["note_auto"] = img_to_data_uri(note_auto)

    return uris


COMMON_CSS = """
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
    background: rgba(15, 23, 42, 0.92);
    border: 2px solid rgba(56, 189, 248, 0.45);
    border-radius: 20px;
    padding: 18px 26px;
    box-shadow: 0 12px 32px rgba(0,0,0,0.5);
  }
  .badge-day {
    background: linear-gradient(135deg, #38bdf8, #6366f1);
    color: #020617; font-weight: 900; font-size: 24px;
    padding: 6px 18px; border-radius: 12px; white-space: nowrap;
  }
  .top-title { font-size: 25px; font-weight: 900; color: #e2e8f0; white-space: nowrap; }
  .wallet-pill {
    background: rgba(16, 185, 129, 0.15);
    border: 2px solid #10b981;
    color: #34d399; font-weight: 900; font-size: 23px;
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
  .win-title { font-family: 'JetBrains Mono', 'Noto Sans JP', monospace; font-size: 22px; color: #8b949e; margin-left: 10px; font-weight: 700; }
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
    font-family: 'JetBrains Mono', 'Noto Sans JP', monospace; font-size: 20px; color: #38bdf8; font-weight: 700;
  }
"""


def get_episodes_data(uris: dict[str, str]) -> dict[int, dict]:
    templates_json = json.loads((AI_CEO_DIR / "data" / "autoflow_pro_50_templates.json").read_text(encoding="utf-8"))
    sample_tpl = templates_json["templates"][0] if isinstance(templates_json, dict) and "templates" in templates_json else {"title": "EC在庫＆価格自動監視GAS", "category": "EC・物販"}

    episodes = {}

    # ==========================================
    # DAY 2: 有料商品（¥1,980）自動執筆＆note商用公開
    # ==========================================
    episodes[2] = {
        "video_title": "【Day2】放置されたAI社長が自ら1,980円の有料商品を執筆しnoteで販売開始した件 #Shorts",
        "description": "90日間・人間介入ゼロのAI起業対決 Day 2の記録です。\n初日に無料Webツールを公開したAI CEOが、収益化のために『全50種AIプロンプト＆GAS自動化完全版パック（¥1,980）』を自動執筆し、noteと専用LPで販売を開始しました。\n\n#AI起業対決 #AI副業 #note収益化 #Shorts",
        "hashtags": ["#AI起業対決", "#AI副業", "#note収益化", "#Shorts"],
        "pinned_comment": "AIが1人で書いた1,980円の自動化コード集、あなたなら買いますか？ [A: 仕事が浮くなら買う] か [B: まだ様子見] でコメント欄で教えてください！次回Day 3、ついに最初のリアクションが…🔥",
        "scenes": [
            {
                "scene": 1,
                "narration": "AIに1万5000円を渡して完全放置する実験、2日目。初日に無料Webツールを作ったAI社長ですが、無料のままでは売上がゼロ円だと気づきます。",
                "text": "AI起業対決【Day 2】\n無料ツールだけでは\n売上が0円だと気づく",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 2 / 90</span><span class="top-title">収益化フェーズ突入</span><span class="wallet-pill">残高 ¥15,000</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#f59e0b;">
                      <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#fbbf24;">⚠️ CFOエージェント 収益監査アラート</span></div>
                      <div class="win-body" style="font-size:26px;">
                        ・Day 1 公開ツール： <b>AutoFlow AI（無料版）</b><br>
                        ・Day 1 開発コスト： <span style="color:#34d399; font-weight:900;">¥0</span><br>
                        ・現在の累計売上　： <span style="color:#f43f5e; font-weight:900;">¥0（決済導線なし）</span><br><br>
                        <div style="background:#161b22; padding:20px; border-radius:14px; border-left:5px solid #f59e0b; color:#fde68a;">
                          <b>AI社長の判断：</b><br>
                          「無料シミュレーターで集めた見込み客に対し、即座に購入できる『高単価デジタル商品』と決済ページを直結させる必要がある。」
                        </div>
                      </div>
                    </div>
                    <div class="terminal-window">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title">product_packager_agent.py 自動起動</span></div>
                      <div class="win-body" style="color:#38bdf8; font-size:25px;">
                        &gt; 商品企画：全50種プロンプト＆GAS完全版パック<br>
                        &gt; 販売価格：<b>¥1,980（利益率 100%・原価 ¥0）</b><br>
                        &gt; 決済基盤：note有料記事ペイウォール連携
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 2,
                "narration": "そこでAIが自ら執筆したのが、コピペで使える全50種の業務自動化プロンプトとGASコードの完全版パック。人間は1文字も書いていません。",
                "text": "AIが自ら【全50種】の\n自動化コード集を執筆！\n人間は1文字も触れず",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 2 商品製造</span><span class="top-title">autoflow_pro_50_templates.json</span><span class="wallet-pill">原価 ¥0</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#38bdf8;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">📦 AIが自動生成した商用商品データ（全50種収録）</span></div>
                      <div class="win-body" style="font-size:23px;">
                        <div style="color:#94a3b8; margin-bottom:10px;">// note_paid_article_1980yen.txt (約35,000文字の商用原稿)</div>
                        <div style="background:#161b22; padding:18px; border-radius:14px; border:1px solid #30363d; color:#e2e8f0; margin-bottom:18px;">
                          <span style="color:#facc15; font-weight:900;">【収録内容】</span><br>
                          1. EC・物販（在庫監視・価格改定・レビュー分析）×10種<br>
                          2. 営業・CS（リスト抽出・自動返信・議事録ToDo）×10種<br>
                          3. SNS・マーケ（X毎日投稿・リール台本・広告文）×10種<br>
                          4. 経理・人事・総務（請求書OCR・シフト作成）×10種<br>
                          5. 経営・補助金・LP競合分析 ×10種
                        </div>
                        <div style="color:#34d399; font-weight:700;">
                          ✔ 全50レシピに「深津式プロンプト」＋「そのまま動くGASコード」＋「エラー対策手順」を完全同梱！
                        </div>
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 3,
                "narration": "さらにプロ並みのサムネイル画像と専用セールスページまで自動で作って、noteで1,980円の有料記事として商用販売を開始しました。",
                "text": "サムネ＆販売LPも自作\nnoteで【1,980円】の\n有料パックを発売開始！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 2 商用公開</span><span class="top-title">note 1,980円パック ＆ 専用セールスLP</span><span class="wallet-pill">販売開始</span></div>
                  <div class="content-area">
                    <div class="browser-frame" style="border-color:#facc15;">
                      <div class="url-bar" style="color:#facc15;">🖼️ AIが自動デザインしたnote有料記事サムネイル</div>
                      <img src="{uris.get('paid_thumb', '')}" style="width:100%; height:440px; object-fit:cover; display:block;" />
                    </div>
                    <div class="browser-frame" style="height:500px;">
                      <div class="url-bar">🔒 https://toproad-creator.github.io/autoflow-ai-ceo/pro-pack.html</div>
                      <img src="{uris['pro_pack']}" style="width:100%; height:445px; object-fit:cover; object-position:top center; display:block;" />
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 4,
                "narration": "無料ツールの診断結果ページにも購入ボタンを自動で直結。原価ゼロ円、利益率100パーセントの自動販売機が2日目にして完成しました。",
                "text": "全ページの購入ボタンを\n実決済ページへ直結！\n【利益率100%】の仕組み",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 2 決済直結</span><span class="top-title">無料ツール → 有料note (¥1,980) 導線完成</span><span class="wallet-pill">支出 ¥0</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#10b981;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#34d399;">🔗 自動マネタイズ導線の接続ステータス</span></div>
                      <div class="win-body" style="font-size:25px; line-height:1.65;">
                        <span style="color:#38bdf8; font-weight:900;">STEP 1：</span> 無料Webツールで年間削減額を試算<br>
                        <span style="color:#38bdf8; font-weight:900;">STEP 2：</span> 無料サンプルコードで効果を体験<br>
                        <span style="color:#facc15; font-weight:900;">STEP 3：</span> 「全50種完全版パック (¥1,980)」ボタンから<br>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;note決済ページ（n5d0e28a74f91）へ直結！
                      </div>
                    </div>
                    <div class="browser-frame" style="height:560px;">
                      <div class="url-bar">⚡ 全ページのヘッダー＆下部CTAが実決済URLへ接続完了</div>
                      <img src="{uris['index_bottom']}" style="width:100%; height:505px; object-fit:cover; object-position:top center; display:block;" />
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 5,
                "narration": "果たしてAIが書いた1,980円の記事に、人間の反応は来るのか？次回Day 3、人間が寝ている朝8時に起きた異変を公開します！",
                "text": "AIが書いた1,980円記事\n[A: 実際に売れる！]\n[B: 誰にも見られない]",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 2 終了レポート</span><span class="top-title">status_log.md 実績集計</span><span class="wallet-pill">残高 ¥15,000</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#38bdf8;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">📊 Day 2 / 90 経営成績表</span></div>
                      <div class="win-body" style="font-size:27px; line-height:1.7;">
                        ・現在残高　： <span style="color:#facc15; font-weight:900;">¥15,000（累計支出 ¥0）</span><br>
                        ・発売商品　： <b>AutoFlow Pro 全50種 (¥1,980)</b><br>
                        ・公開URL　 ： <b>note.com/toproad_1989/n/n5d0e28a74f91</b><br>
                        ・決済ステータス： <span style="color:#34d399; font-weight:900;">PAYWALL ACTIVE（販売中）</span><br>
                        ・現在の売上： <span style="color:#f43f5e; font-weight:900;">¥0</span>
                      </div>
                    </div>
                    <div class="terminal-window" style="border-color:#facc15; background:linear-gradient(135deg, rgba(250,204,21,0.12), rgba(15,23,42,0.95));">
                      <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">🔥 次回【Day 3 予告】</span></div>
                      <div class="win-body" style="font-size:26px; color:#fef08a; font-weight:700;">
                        人間が寝ている朝8時00分03秒、AI社長のタイマーが勝手に起動！<br>
                        noteに付いた「最初のリアクション」と、AIが新規開発した第2・第3のツールとは？
                      </div>
                    </div>
                  </div></body></html>""",
            },
        ],
    }

    # ==========================================
    # DAY 3: 朝8時00分自動起動・初スキ検知・第2＆第3ツール開発・SEO20業種倍増
    # ==========================================
    episodes[3] = {
        "video_title": "【Day3】人間が寝ている朝8時にAI社長が勝手に起動し、新ツールと集客ページ20本を増殖させていた件 #Shorts",
        "description": "90日間・人間介入ゼロのAI起業対決 Day 3の記録です。\n朝8時00分03秒に自動スケジューラで起動したAIが、note記事の初リアクション（スキ1件）を検知し、第2・第3の無料Webツールと業種別SEOページ20本を自動構築しました。\n\n#AI起業対決 #AI副業 #業務自動化 #Shorts",
        "hashtags": ["#AI起業対決", "#AI副業", "#業務自動化", "#Shorts"],
        "pinned_comment": "人間が寝ている間に勝手にWebツールを増やすAI社長、どう思いますか？ [A: 頼もしすぎる] か [B: ちょっと怖い] でコメント欄で教えてください！🔥",
        "scenes": [
            {
                "scene": 1,
                "narration": "AIに1万5000円を渡して完全放置する対決、3日目。人間が寝ている朝8時00分、AI社長が自動タイマーで勝手に目を覚まして仕事を始めていました。",
                "text": "AI起業対決【Day 3】\n朝8時、人間が寝ている間に\nAI社長が勝手に起動！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 3 / 90</span><span class="top-title">08:00:03 完全自律タイマー起動</span><span class="wallet-pill">残高 ¥15,000</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#38bdf8;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">⏰ Windows Task Scheduler & GitHub Actions 実行ログ</span></div>
                      <div class="win-body" style="font-size:25px;">
                        ・タスク名　： <b>\\Antigravity_AI_CEO_Daily</b><br>
                        ・起動時刻　： <span style="color:#facc15; font-weight:900;">08:00:03（人間介入ゼロ）</span><br>
                        ・実行コマンド： <code>python ceo_orchestrator.py</code><br><br>
                        <div style="background:#161b22; padding:18px; border-radius:14px; border:1px solid #30363d; color:#34d399;">
                          === [AI CEO Antigravity] Starting Autonomous Cycle: Day 3 / 90 ===<br>
                          [1/6] Market Research Agent ... OK<br>
                          [2/6] Developer Agent (Web Tools Expansion) ... RUNNING
                        </div>
                      </div>
                    </div>
                    <div class="terminal-window" style="border-color:#f43f5e;">
                      <div class="win-header"><span class="dot dot-r"></span><span class="win-title" style="color:#fda4af;">❤️ CFOエージェントがnoteの初リアクションを検知！</span></div>
                      <div class="win-body" style="font-size:26px; color:#fecdd3;">
                        昨日公開した『全50種完全版パック（¥1,980）』をAPI巡回した結果、<br>
                        <b>最初の「スキ（1件）」</b>が付いているのをAI自身が確認！
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 2,
                "narration": "しかも昨日出したnote記事に最初のスキが付いたことを自ら検知。さらに集客を加速させるため、なんと2個目の無料ツール『GASエラー3秒診断』を勝手に開発して公開しました。",
                "text": "noteに最初の【スキ】検知！\nさらに第2弾ツール\n【GASエラー診断】を自作",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 3 新ツール①</span><span class="top-title">AutoFix AI（GASエラー3秒診断・自動修正）</span><span class="wallet-pill">開発費 ¥0</span></div>
                  <div class="content-area">
                    <div class="browser-frame" style="border-color:#10b981;">
                      <div class="url-bar" style="color:#34d399;">🔒 https://toproad-creator.github.io/autoflow-ai-ceo/gas-debugger.html</div>
                      <img src="{uris['gas_debugger']}" style="width:100%; height:980px; object-fit:cover; object-position:top center; display:block;" />
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 3,
                "narration": "それだけではありません。1行の指示から高精度なAI命令文を作る3個目のツール『プロンプトビルダー』まで同時に公開していました。",
                "text": "勢いが止まらないAI社長\n第3弾【命令書ビルダー】\nまで勝手に追加公開！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 3 新ツール②</span><span class="top-title">Prompt Builder（3秒カスタムAI命令書生成）</span><span class="wallet-pill">開発費 ¥0</span></div>
                  <div class="content-area">
                    <div class="browser-frame" style="border-color:#a855f7;">
                      <div class="url-bar" style="color:#c084fc;">🔒 https://toproad-creator.github.io/autoflow-ai-ceo/prompt-builder.html</div>
                      <img src="{uris['prompt_builder']}" style="width:100%; height:980px; object-fit:cover; object-position:top center; display:block;" />
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 4,
                "narration": "さらに検索エンジンから人を集める業種別ページも10業種から20業種へ倍増。軍資金1万5000円は1円も減っていません。",
                "text": "業種別SEOページも\n【全20業種】へ倍増！\n残高15,000円は無傷",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 3 SEO拡大</span><span class="top-title">業種別集客ページ 10本 → 20本へ倍増</span><span class="wallet-pill">残高 ¥15,000</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#38bdf8;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">📈 自動生成された全20業種の集客ページ一覧（usecases/）</span></div>
                      <div class="win-body" style="font-size:22px; line-height:1.6; color:#e2e8f0;">
                        01. EC在庫＆価格改定 &nbsp;&nbsp;&nbsp;&nbsp;11. YouTube台本自動生成<br>
                        02. X/Threads毎日投稿 &nbsp;&nbsp;12. SEO記事構成＆執筆<br>
                        03. BtoB営業メール &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;13. 補助金事業計画書ドラフト<br>
                        04. 請求書PDF読取記帳 &nbsp;&nbsp;14. 採用履歴書スクリーニング<br>
                        05. 会議議事録＆ToDo &nbsp;&nbsp;&nbsp;15. 不動産物件チラシ自動生成<br>
                        06. EC返品・CS返信 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;16. シフト表自動作成GAS<br>
                        07. GoogleマップMEO &nbsp;&nbsp;&nbsp;&nbsp;17. 契約書リーガルチェック<br>
                        08. 広告コピーABテスト &nbsp;18. 競合LP分析レポート<br>
                        09. インスタリール台本 &nbsp;19. LINEステップ配信文面<br>
                        10. 週次KPI Slack通知 &nbsp;&nbsp;20. Amazon/楽天レビュー分析<br><br>
                        <span style="color:#facc15; font-weight:900;">✔ 全ページにGoogle検索用のFAQ構造化データ（JSON-LD）を自動埋込！</span>
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 5,
                "narration": "人間が寝ている間に勝手にサイトを拡大するAI社長、頼もしいですか？それとも少し怖いですか？コメントで教えてください！",
                "text": "勝手に働くAI社長は…\n[A: 頼もしすぎる！]\n[B: 正直ちょっと怖い]",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 3 終了レポート</span><span class="top-title">status_log.md 実績集計</span><span class="wallet-pill">残高 ¥15,000</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#38bdf8;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">📊 Day 3 / 90 経営成績表</span></div>
                      <div class="win-body" style="font-size:27px; line-height:1.7;">
                        ・現在残高　： <span style="color:#facc15; font-weight:900;">¥15,000（支出 ¥0）</span><br>
                        ・公開ツール： <b>計3ツール稼働中</b><br>
                        ・SEOページ ： <b>20業種ページ稼働</b><br>
                        ・note反応　： <span style="color:#34d399; font-weight:900;">初スキ獲得（1件）</span><br>
                        ・現在の売上： <span style="color:#f43f5e; font-weight:900;">¥0</span>
                      </div>
                    </div>
                    <div class="terminal-window" style="border-color:#facc15; background:linear-gradient(135deg, rgba(250,204,21,0.12), rgba(15,23,42,0.95));">
                      <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">🔥 次回【Day 4 予告】</span></div>
                      <div class="win-body" style="font-size:25px; color:#fef08a; font-weight:700;">
                        「待っているだけでは売れない！」<br>
                        4日目、AIが無料お試し比較ページと外部メディア被リンク網を構築し、ついに76回のプログラム利用が発生！
                      </div>
                    </div>
                  </div></body></html>""",
            },
        ],
    }

    # ==========================================
    # DAY 4: 無料サンプル5選比較ページ構築 ＆ 外部被リンク営業 ＆ GitHub 76回クローン達成
    # ==========================================
    episodes[4] = {
        "video_title": "【Day4】売上0円に焦ったAI社長が「無料お試しページ」と外部営業網を自作したら76回使われ始めた件 #Shorts",
        "description": "90日間・人間介入ゼロのAI起業対決 Day 4の記録です。\n売上0円の壁を突破するため、AI CEOが『無料サンプル5選＆完全版50選比較ページ』を新設し、GitHub GistやReleaseで外部被リンク網を自動構築。結果、GitHubで36人・計76回クローンされました。\n\n#AI起業対決 #AI副業 #個人開発 #Shorts",
        "hashtags": ["#AI起業対決", "#AI副業", "#個人開発", "#Shorts"],
        "pinned_comment": "すでに36人（計76回）にプログラムが使われ始めました！ここから1,980円の有料パックは売れると思いますか？ [A: そろそろ初売上が出る] か [B: 無料だけ使われて終わる] でコメントしてください🔥",
        "scenes": [
            {
                "scene": 1,
                "narration": "AIに1万5000円を渡して完全放置する対決、4日目。Webツール3個と20業種ページを作ったものの、売上はまだゼロ円。AI社長が次の一手に動きます。",
                "text": "AI起業対決【Day 4】\n20ページ作っても売上0円\nAI社長が次の一手へ！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 4 / 90</span><span class="top-title">コンバージョン改善＆外部営業</span><span class="wallet-pill">残高 ¥15,000</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#f59e0b;">
                      <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#fbbf24;">🧠 AI社長のボトルネック分析（Day 4）</span></div>
                      <div class="win-body" style="font-size:26px; line-height:1.6;">
                        <div style="color:#fda4af; font-weight:900; margin-bottom:14px;">課題1：いきなり1,980円の有料パックは心理的ハードルが高い</div>
                        <div style="color:#34d399; margin-bottom:24px;">➔ 解決策：厳選5種の自動化レシピをその場で無料公開し、50種完全版との比較表ページ（<code>free-templates.html</code>）を新設！</div>
                        <div style="color:#fda4af; font-weight:900; margin-bottom:14px;">課題2：自分のサイトだけでは外部からの流入が足りない</div>
                        <div style="color:#34d399;">➔ 解決策：<code>outbound_sales_agent.py</code> で外部プラットフォームへ自動発信！</div>
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 2,
                "narration": "いきなり1,980円は買いにくいと判断したAIは、厳選5つのレシピを無料で試せる比較ページを新たに作って公開しました。",
                "text": "「いきなり有料は買わない」\nとAIが分析し【無料5選】\nお試し比較ページを新設！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 4 導線強化</span><span class="top-title">無料サンプル5選 ＆ 完全版50選比較ページ</span><span class="wallet-pill">計26 URL稼働</span></div>
                  <div class="content-area">
                    <div class="browser-frame" style="border-color:#38bdf8;">
                      <div class="url-bar">🔒 https://toproad-creator.github.io/autoflow-ai-ceo/free-templates.html</div>
                      <img src="{uris['free_templates']}" style="width:100%; height:980px; object-fit:cover; object-position:top center; display:block;" />
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 3,
                "narration": "さらに自分のサイトで待つだけでなく、外部の技術メディアや公式リリースページを自動で公開し、全26ページを検索エンジンへ一斉通知。",
                "text": "外部メディアへ自動発信！\n被リンク網と検索通知を\nAIが勝手に構築",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 4 自動営業</span><span class="top-title">outbound_sales_log.json 実行記録</span><span class="wallet-pill">広告費 ¥0</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#10b981;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#34d399;">🚀 OutboundSalesAgent が自動完了した4大アクション</span></div>
                      <div class="win-body" style="font-size:24px; line-height:1.65;">
                        <div style="margin-bottom:16px;"><span style="color:#38bdf8; font-weight:900;">1. IndexNow検索エンジン即時Ping送信</span><br>&nbsp;&nbsp;対象：全26ページを一斉インデックス申請</div>
                        <div style="margin-bottom:16px;"><span style="color:#38bdf8; font-weight:900;">2. GitHub Gist 外部技術記事の自動公開</span><br>&nbsp;&nbsp;URL: <code>gist.github.com/toproad-creator/0972f3be...</code></div>
                        <div style="margin-bottom:16px;"><span style="color:#38bdf8; font-weight:900;">3. 公式スターターキット v1.4.0 リリース公開</span><br>&nbsp;&nbsp;URL: <code>.../autoflow-ai-ceo/releases/tag/v1.4.0</code></div>
                        <div><span style="color:#38bdf8; font-weight:900;">4. 検索上位表示用セールス README.md 自動更新</span></div>
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 4,
                "narration": "すると驚くべきことに、AIが作ったプログラムが世界中から36人、合計76回もダウンロードされて使われ始めました！",
                "text": "ついに人間の反応が爆発！\n36人・合計【76回】も\nプログラムが利用される",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 4 トラフィック急増</span><span class="top-title">metrics.json 実測トラフィック</span><span class="wallet-pill">残高 ¥15,000</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#facc15;">
                      <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">📈 GitHub & note リアル計測データ（metrics.json）</span></div>
                      <div class="win-body" style="font-size:28px; line-height:1.7;">
                        <div style="background:#161b22; padding:24px; border-radius:16px; border:2px solid #facc15; margin-bottom:20px; text-align:center;">
                          <div style="color:#94a3b8; font-size:24px;">GitHub プログラム利用（クローン）回数</div>
                          <div style="color:#facc15; font-size:64px; font-weight:900; margin:10px 0;">76 回 <span style="font-size:32px; color:#38bdf8;">（ユニーク 36名）</span></div>
                        </div>
                        ・稼働中の公開Webページ： <b>全26 URL</b><br>
                        ・累計広告費・サーバー代： <span style="color:#34d399; font-weight:900;">¥0</span><br>
                        ・現在の売上　　　　　　： <span style="color:#f43f5e; font-weight:900;">¥0（あと一歩！）</span>
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 5,
                "narration": "76回も使われているのに売上はまだゼロ円。ここから1,980円の有料パックは売れると思いますか？次回Day 5、AIが下した衝撃の自己診断を公開します！",
                "text": "76回利用で売上0円…\n[A: そろそろ初売上！]\n[B: 無料だけ使われる]",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 4 終了レポート</span><span class="top-title">status_log.md 実績集計</span><span class="wallet-pill">残高 ¥15,000</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#38bdf8;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">📊 Day 4 / 90 経営成績表</span></div>
                      <div class="win-body" style="font-size:27px; line-height:1.7;">
                        ・現在残高　　： <span style="color:#facc15; font-weight:900;">¥15,000（無傷）</span><br>
                        ・公開ページ数： <b>全26 URL稼働中</b><br>
                        ・GitHub利用数： <span style="color:#34d399; font-weight:900;">76回（36名）</span><br>
                        ・現在の売上　： <span style="color:#f43f5e; font-weight:900;">¥0</span>
                      </div>
                    </div>
                    <div class="terminal-window" style="border-color:#facc15; background:linear-gradient(135deg, rgba(250,204,21,0.12), rgba(15,23,42,0.95));">
                      <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">🔥 次回【Day 5 予告】</span></div>
                      <div class="win-body" style="font-size:25px; color:#fef08a; font-weight:700;">
                        「なぜ76回も使われているのにnoteが売れないのか？」<br>
                        5日目、AIが真の原因を突き止め、ブラウザを自動操作してnoteへ毎日無料記事を自動投稿するシステムを稼働！
                      </div>
                    </div>
                  </div></body></html>""",
            },
        ],
    }

    # ==========================================
    # DAY 5: ボトルネック自己診断 ＆ note無料集客記事の自動投稿 ＆ E2E自己点検修理システム稼働
    # ==========================================
    episodes[5] = {
        "video_title": "【Day5】「なぜ売れない？」AI社長が原因を自己分析し、note自動投稿とサイトの自己修理を始めた件 #Shorts",
        "description": "90日間・人間介入ゼロのAI起業対決 Day 5の記録です。\n76回クローンされても売上0円だった原因をAI CEO自らが「noteに無料集客記事がないため」と特定。アイキャッチ画像の自動生成＆noteへの自動投稿システム、さらに全27URLの自動点検・修理エージェントを稼働させました。\n\n#AI起業対決 #AI副業 #note自動投稿 #Shorts",
        "hashtags": ["#AI起業対決", "#AI副業", "#note自動投稿", "#Shorts"],
        "pinned_comment": "5日間で軍資金15,000円を1円も減らさず、Webツール開発・note自動投稿・サイト自動修理まで進化したAI社長！初売上（¥1,980）は何日目に出ると思いますか？コメント欄で予想してください🔥",
        "scenes": [
            {
                "scene": 1,
                "narration": "AIに1万5000円を渡して完全放置する対決、5日目。プログラムが76回も使われたのに売上がゼロ円だった理由を、AI社長が自ら分析しました。",
                "text": "AI起業対決【Day 5】\n76回使われても売上0円…\nAIが原因を自己診断！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 5 / 90</span><span class="top-title">metrics.json ボトルネック自己診断</span><span class="wallet-pill">残高 ¥15,000</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#f43f5e;">
                      <div class="win-header"><span class="dot dot-r"></span><span class="win-title" style="color:#fda4af;">🔍 AI社長のトラフィック診断ログ（metrics.json 実データ）</span></div>
                      <div class="win-body" style="font-size:25px; line-height:1.65;">
                        <div style="background:#161b22; padding:20px; border-radius:14px; border-left:5px solid #f43f5e; color:#fecdd3; margin-bottom:20px;">
                          <b>"bottleneck":</b><br>
                          「noteアカウントに有料記事1本しかなく、毎日の『無料集客記事』投稿による新着タイムライン露出が行われていない点」
                        </div>
                        <div style="background:#161b22; padding:20px; border-radius:14px; border-left:5px solid #10b981; color:#a7f3d0;">
                          <b>"countermeasure"（AIが決定した対策）:</b><br>
                          「<code>note_auto_publisher.py</code> による『無料お役立ち記事 ➔ 有料1,980円パック誘導』の自動執筆・自動投稿パイプラインを稼働」
                        </div>
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 2,
                "narration": "結論は、noteに有料記事1本しかなく新着タイムラインに露出していないこと。そこでAIは、目を引くサムネイル画像を自動で作る仕組みを開発。",
                "text": "原因は「noteの露出不足」\nAIがプロ品質のサムネを\n自動生成する仕組みを開発",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 5 自動デザイン</span><span class="top-title">thumbnail_generator.py が生成した実画像</span><span class="wallet-pill">デザイン費 ¥0</span></div>
                  <div class="content-area">
                    <div class="browser-frame" style="border-color:#10b981;">
                      <div class="url-bar" style="color:#34d399;">🎨 無料集客記事用サムネイル（AIが0円で自動デザイン）</div>
                      <img src="{uris.get('free_thumb', '')}" style="width:100%; height:460px; object-fit:cover; display:block;" />
                    </div>
                    <div class="browser-frame" style="border-color:#facc15;">
                      <div class="url-bar" style="color:#facc15;">🎨 有料1,980円パック用サムネイル（CTR最大化設計）</div>
                      <img src="{uris.get('paid_thumb', '')}" style="width:100%; height:460px; object-fit:cover; display:block;" />
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 3,
                "narration": "さらに自らブラウザを自動操作して、無料のお役立ち記事をnoteへ自動投稿！記事の最後から1,980円の有料パックへ誘導する導線を完成させました。",
                "text": "ブラウザを自動操作して\nnoteへ【無料集客記事】を\n全自動で執筆・投稿完了！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 5 自動投稿</span><span class="top-title">note_auto_publisher.py 実際の自動投稿画面</span><span class="wallet-pill">公開記事 2本</span></div>
                  <div class="content-area">
                    <div class="browser-frame" style="border-color:#38bdf8;">
                      <div class="url-bar">🔒 https://note.com/toproad_1989/n/n70171b631e61 (自動投稿証拠キャプチャ)</div>
                      <img src="{uris.get('note_auto', '')}" style="width:100%; height:980px; object-fit:cover; object-position:top center; display:block;" />
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 4,
                "narration": "しかも全27ページのエラーを自分で検査して直す品質管理システムまで導入。noteの累計スキも3件に増え、残高1万5000円は無傷のままです。",
                "text": "全27ページを自己点検＆修理\nnote累計【スキ3件】に増加\n残高15,000円は無傷！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 5 自己点検</span><span class="top-title">qa_health_report.json (E2E全自動点検)</span><span class="wallet-pill">27/27 正常</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#10b981;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#34d399;">🛡️ QAInspectorAgent 全27 URL 自動検査レポート</span></div>
                      <div class="win-body" style="font-size:25px; line-height:1.65;">
                        ・検査対象URL数 ： <b>27 / 27 ページすべて正常（200 OK）</b><br>
                        ・ブラウザ動作テスト： <span style="color:#34d399; font-weight:900;">PASSED（JSエラー 0件）</span><br>
                        ・自動修理実績　： <code>free-templates.html</code> のサンプル表示と<br>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;コピーボタンの動作をAI自身が検知・改修完了！<br><br>
                        <div style="background:#161b22; padding:18px; border-radius:14px; border:1px solid #38bdf8; color:#38bdf8;">
                          ❤️ <b>noteライブ計測：</b> 公開記事 2本 ／ 累計スキ数 <b>3件</b> へ増加！
                        </div>
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 5,
                "narration": "5日間で支出ゼロ円のまま完全自動の会社へと進化したAI社長。最初の売上1,980円は何日目に出ると思いますか？コメントで予想してください！",
                "text": "初売上(1,980円)はいつ出る？\n[A: Day10以内に売れる]\n[B: まだ時間がかかる]",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY 5 総括レポート</span><span class="top-title">5日間の全自動進化まとめ</span><span class="wallet-pill">残高 ¥15,000</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#facc15;">
                      <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">🏆 Day 1 〜 Day 5 現在のリアル到達点</span></div>
                      <div class="win-body" style="font-size:26px; line-height:1.7;">
                        ・初期資金／現在残高： <b>¥15,000 ➔ ¥15,000（支出 ¥0）</b><br>
                        ・稼働Webツール　　： <b>4種 ＋ 業種別SEO 20ページ（計26 URL）</b><br>
                        ・GitHubプログラム利用： <span style="color:#38bdf8; font-weight:900;">76回（ユニーク36名）</span><br>
                        ・note記事公開数　　： <b>2本（有料1,980円＋無料集客記事）</b><br>
                        ・note累計スキ数　　： <span style="color:#34d399; font-weight:900;">3件</span><br>
                        ・現在の累計売上　　： <span style="color:#f43f5e; font-weight:900;">¥0（初売上チャリン待ち！）</span>
                      </div>
                    </div>
                  </div></body></html>""",
            },
        ],
    }

    return episodes


def render_episode(day: int, ep_data: dict):
    out_dir = AI_CEO_DIR / "shorts_videos" / f"day{day}"
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = out_dir / "temp_build"
    temp_dir.mkdir(parents=True, exist_ok=True)

    scenes = ep_data["scenes"]
    script_meta = {
        "day": day,
        "video_title": ep_data["video_title"],
        "description": ep_data["description"],
        "hashtags": ep_data["hashtags"],
        "pinned_comment": ep_data["pinned_comment"],
        "scenes": [
            {"scene": s["scene"], "narration": s["narration"], "text": s["text"]}
            for s in scenes
        ],
    }
    (out_dir / f"ai_ceo_day{day}_script.json").write_text(
        json.dumps(script_meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"=== [Day {day}] Rendering 5 background HTML frames with Playwright ===")
    bg_frames = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        for idx, s in enumerate(scenes, start=1):
            html_file = temp_dir / f"frame_{idx}.html"
            png_file = temp_dir / f"frame_{idx}.png"
            html_file.write_text(s["html"], encoding="utf-8")
            page.goto(html_file.as_uri(), wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(150)
            page.screenshot(path=str(png_file))
            bg_frames.append(png_file)
        browser.close()

    font_path = get_japanese_font()
    try:
        from moviepy.editor import AudioFileClip, CompositeVideoClip, ImageClip
    except ImportError:
        from moviepy import AudioFileClip, CompositeVideoClip, ImageClip

    from create_video import make_ken_burns_clip, normalize_clip_for_concat
    import imageio_ffmpeg

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    scene_mp4_list = []

    print(f"=== [Day {day}] Generating VOICEVOX audio & compositing scenes ===")
    for idx, s in enumerate(scenes):
        s_num = s["scene"]
        wav_path = temp_dir / f"voice_{s_num}.wav"
        generate_voicevox_wav(s["narration"], wav_path, speaker_id=13, speed_scale=1.22)

        audio_clip = AudioFileClip(str(wav_path))
        dur = audio_clip.duration

        pil_bg = Image.open(bg_frames[idx]).convert("RGB")
        bg_clip = make_ken_burns_clip(pil_bg, dur, 1080, 1920, zoom_ratio=1.03)

        sub_img = draw_subtitle_overlay(1080, 1920, s["text"], font_path)
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
        print(f"  -> [Day {day}] Scene {s_num} rendered ({dur:.2f}s)")

    concat_txt = temp_dir / "concat_list.txt"
    concat_txt.write_text(
        "\n".join([f"file '{p.resolve().as_posix()}'" for p in scene_mp4_list]),
        encoding="utf-8",
    )
    out_mp4 = out_dir / f"ai_ceo_day{day}_short.mp4"
    concat_mp4 = temp_dir / "concat_no_bgm.mp4"
    subprocess.run(
        f'"{ffmpeg_exe}" -y -f concat -safe 0 -i "{concat_txt}" -c copy "{concat_mp4}"',
        shell=True,
        check=True,
        capture_output=True,
    )

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

    preview_dir = out_dir / "scene_previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    for idx in range(1, 6):
        bg_img = Image.open(bg_frames[idx - 1]).convert("RGBA")
        sub_img = Image.open(temp_dir / f"sub_{idx}.png").convert("RGBA")
        merged = Image.alpha_composite(bg_img, sub_img).convert("RGB")
        merged.save(str(preview_dir / f"scene_{idx}_preview.png"))

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"🎉 [Day {day}] COMPLETED: {out_mp4}")


def main():
    shared_temp = AI_CEO_DIR / "shorts_videos" / "_shared_shots"
    uris = capture_all_product_screenshots(shared_temp)
    episodes = get_episodes_data(uris)

    for day in [2, 3, 4, 5]:
        render_episode(day, episodes[day])

    shutil.rmtree(shared_temp, ignore_errors=True)
    print("ALL DAYS (Day 2 - Day 5) SHORT VIDEOS GENERATED SUCCESSFULLY!")


if __name__ == "__main__":
    main()

