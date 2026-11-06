import os
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
THUMB_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "thumbnails")


class NoteThumbnailGenerator:
    """note記事のクリック率（CTR）を最大化する 1280x670px アイキャッチ画像の自動生成エンジン
    Playwright の HTML/CSS レンダリングを用いることで、文字化けゼロ・デザイナー品質の日本語サムネイルを¥0で自動生成する。
    """

    def __init__(self):
        os.makedirs(THUMB_DIR, exist_ok=True)

    def build_free_article_html(self, niche: dict, day: int) -> str:
        yearly_yen = niche["avg_hours_saved_monthly"] * 12 * niche["hourly_wage"]
        yearly_man = int(yearly_yen / 10000)
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@700;900&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1280px;
    height: 670px;
    font-family: 'Noto Sans JP', 'Yu Gothic', 'Meiryo', sans-serif;
    background: radial-gradient(circle at 85% 15%, #1e3a8a 0%, #0f172a 55%, #020617 100%);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 56px 68px;
    position: relative;
    overflow: hidden;
  }}
  .bg-grid {{
    position: absolute;
    inset: 0;
    background-image: linear-gradient(rgba(56, 189, 248, 0.07) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(56, 189, 248, 0.07) 1px, transparent 1px);
    background-size: 40px 40px;
    z-index: 0;
  }}
  .glow-orb {{
    position: absolute;
    width: 520px;
    height: 520px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.25) 0%, transparent 70%);
    top: -120px;
    right: -80px;
    z-index: 0;
  }}
  .left-col {{
    position: relative;
    z-index: 2;
    width: 740px;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }}
  .badge-row {{
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .badge-free {{
    background: linear-gradient(135deg, #10b981, #059669);
    color: #ffffff;
    font-size: 26px;
    font-weight: 900;
    padding: 8px 24px;
    border-radius: 999px;
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
    letter-spacing: 1px;
  }}
  .badge-sub {{
    background: rgba(56, 189, 248, 0.15);
    border: 2px solid #38bdf8;
    color: #38bdf8;
    font-size: 22px;
    font-weight: 700;
    padding: 8px 20px;
    border-radius: 999px;
  }}
  .main-title {{
    font-size: 56px;
    font-weight: 900;
    line-height: 1.25;
    letter-spacing: -0.5px;
    color: #ffffff;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  }}
  .highlight-yellow {{
    color: #fde047;
    background: linear-gradient(transparent 65%, rgba(234, 179, 8, 0.35) 65%);
  }}
  .metrics-bar {{
    display: flex;
    gap: 20px;
    margin-top: 8px;
  }}
  .metric-card {{
    background: rgba(15, 23, 42, 0.85);
    border: 2px solid rgba(148, 163, 184, 0.25);
    border-radius: 18px;
    padding: 16px 26px;
    display: flex;
    flex-direction: column;
  }}
  .metric-label {{
    font-size: 18px;
    color: #94a3b8;
    font-weight: 700;
  }}
  .metric-val {{
    font-size: 40px;
    font-weight: 900;
    color: #38bdf8;
  }}
  .metric-val.green {{
    color: #34d399;
  }}
  .right-col {{
    position: relative;
    z-index: 2;
    width: 360px;
    background: rgba(15, 23, 42, 0.9);
    border: 2px solid rgba(56, 189, 248, 0.4);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
  }}
  .window-dots {{
    display: flex;
    gap: 8px;
    margin-bottom: 18px;
  }}
  .dot {{ width: 14px; height: 14px; border-radius: 50%; }}
  .dot.r {{ background: #ef4444; }}
  .dot.y {{ background: #f59e0b; }}
  .dot.g {{ background: #10b981; }}
  .code-line {{
    font-family: Consolas, monospace;
    font-size: 17px;
    line-height: 1.65;
    color: #e2e8f0;
    margin-bottom: 8px;
  }}
  .c-kw {{ color: #38bdf8; font-weight: bold; }}
  .c-fn {{ color: #fde047; }}
  .c-cm {{ color: #64748b; }}
  .cta-pill {{
    margin-top: 20px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    text-align: center;
    padding: 12px;
    border-radius: 12px;
    font-size: 20px;
    font-weight: 900;
    color: #fff;
  }}
</style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="glow-orb"></div>
  <div class="left-col">
    <div class="badge-row">
      <span class="badge-free">無料コピペOK</span>
      <span class="badge-sub">ChatGPT × Googleスプレッドシート自動化</span>
    </div>
    <div class="main-title">
      <span class="highlight-yellow">{niche['title']}</span>を<br>
      AIとGASで完全自動化する<br>
      実践プロンプト＆コード
    </div>
    <div class="metrics-bar">
      <div class="metric-card">
        <span class="metric-label">月間削減時間</span>
        <span class="metric-val">月 {niche['avg_hours_saved_monthly']} 時間</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">年間コスト削減換算</span>
        <span class="metric-val green">約 {yearly_man} 万円/年</span>
      </div>
    </div>
  </div>
  <div class="right-col">
    <div class="window-dots">
      <div class="dot r"></div><div class="dot y"></div><div class="dot g"></div>
    </div>
    <div class="code-line"><span class="c-cm">// AutoFlow AI 自動実行レシピ</span></div>
    <div class="code-line"><span class="c-kw">function</span> <span class="c-fn">runAutoFlow</span>() {{</div>
    <div class="code-line">&nbsp;&nbsp;<span class="c-kw">const</span> sheet = SpreadsheetApp</div>
    <div class="code-line">&nbsp;&nbsp;&nbsp;&nbsp;.getActiveSheet();</div>
    <div class="code-line">&nbsp;&nbsp;<span class="c-fn">callStructuredAI</span>(sheet);</div>
    <div class="code-line">&nbsp;&nbsp;<span class="c-fn">sendReport</span>(<span style="color:#34d399;">"完了！"</span>);</div>
    <div class="code-line">}}</div>
    <div class="cta-pill">5分で導入できる実践手順 ➔</div>
  </div>
</body>
</html>"""

    def build_paid_pack_html(self) -> str:
        return """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@700;900&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1280px;
    height: 670px;
    font-family: 'Noto Sans JP', 'Yu Gothic', 'Meiryo', sans-serif;
    background: radial-gradient(circle at 80% 20%, #3b0764 0%, #0f172a 55%, #020617 100%);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 56px 68px;
    position: relative;
    overflow: hidden;
  }
  .bg-grid {
    position: absolute;
    inset: 0;
    background-image: linear-gradient(rgba(250, 204, 21, 0.06) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(250, 204, 21, 0.06) 1px, transparent 1px);
    background-size: 40px 40px;
    z-index: 0;
  }
  .left-col {
    position: relative;
    z-index: 2;
    width: 780px;
    display: flex;
    flex-direction: column;
    gap: 22px;
  }
  .badge-row {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .badge-gold {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: #ffffff;
    font-size: 26px;
    font-weight: 900;
    padding: 8px 26px;
    border-radius: 999px;
    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.45);
  }
  .badge-sub {
    background: rgba(250, 204, 21, 0.12);
    border: 2px solid #facc15;
    color: #fde047;
    font-size: 22px;
    font-weight: 700;
    padding: 8px 20px;
    border-radius: 999px;
  }
  .main-title {
    font-size: 54px;
    font-weight: 900;
    line-height: 1.25;
    color: #ffffff;
  }
  .gold-text {
    color: #fde047;
  }
  .metrics-bar {
    display: flex;
    gap: 20px;
    margin-top: 8px;
  }
  .metric-card {
    background: rgba(15, 23, 42, 0.88);
    border: 2px solid rgba(250, 204, 21, 0.35);
    border-radius: 18px;
    padding: 16px 26px;
    display: flex;
    flex-direction: column;
  }
  .metric-label { font-size: 18px; color: #cbd5e1; font-weight: 700; }
  .metric-val { font-size: 38px; font-weight: 900; color: #fde047; }
  .right-col {
    position: relative;
    z-index: 2;
    width: 330px;
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
    border: 3px solid #facc15;
    border-radius: 24px;
    padding: 30px 24px;
    text-align: center;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.7);
  }
  .pack-title { font-size: 24px; font-weight: 900; color: #fde047; margin-bottom: 12px; }
  .pack-num { font-size: 64px; font-weight: 900; color: #ffffff; line-height: 1.1; }
  .pack-unit { font-size: 24px; color: #94a3b8; font-weight: 700; margin-bottom: 18px; }
  .pack-list { text-align: left; font-size: 18px; color: #e2e8f0; line-height: 1.8; margin-bottom: 20px; }
  .price-tag {
    background: linear-gradient(90deg, #f59e0b, #ea580c);
    color: #fff;
    font-size: 26px;
    font-weight: 900;
    padding: 12px;
    border-radius: 14px;
  }
</style>
</head>
<body>
  <div class="bg-grid"></div>
  <div class="left-col">
    <div class="badge-row">
      <span class="badge-gold">AutoFlow Pro 完全版</span>
      <span class="badge-sub">コピペ5分でルーティン業務を消滅</span>
    </div>
    <div class="main-title">
      <span class="gold-text">全10業種・50選</span><br>
      AIプロンプト＆GAS自動実行<br>
      コード完全版パッケージ
    </div>
    <div class="metrics-bar">
      <div class="metric-card">
        <span class="metric-label">収録テンプレート数</span>
        <span class="metric-val">全 50 種類</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">エラー対策・自動通知</span>
        <span class="metric-val">完全実装済</span>
      </div>
    </div>
  </div>
  <div class="right-col">
    <div class="pack-title">COMPLETE PACK</div>
    <div class="pack-num">50</div>
    <div class="pack-unit">AI Prompts + GAS</div>
    <div class="pack-list">
      ✅ EC・物販 / 不動産 / 採用<br>
      ✅ 経理・請求 / SNS運用<br>
      ✅ 営業リスト / 広告レポート
    </div>
    <div class="price-tag">買い切り ¥1,980</div>
  </div>
</body>
</html>"""

    def render_html_to_png(self, html: str, out_path: str) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 670, "device_scale_factor": 1})
            page.set_content(html, wait_until="networkidle", timeout=30000)
            page.screenshot(path=out_path)
            browser.close()
        return out_path

    def generate_free_article_thumbnail(self, niche: dict, day: int) -> str:
        slug = niche.get("slug", niche.get("id", f"niche{day}"))
        out_path = os.path.join(THUMB_DIR, f"thumb_free_day{day}_{slug}.png")
        html = self.build_free_article_html(niche, day)
        return self.render_html_to_png(html, out_path)

    def generate_paid_pack_thumbnail(self) -> str:
        out_path = os.path.join(THUMB_DIR, "thumb_paid_autoflow_pro_50.png")
        html = self.build_paid_pack_html()
        return self.render_html_to_png(html, out_path)


if __name__ == "__main__":
    from researcher_agent import ResearcherAgent
    niches = ResearcherAgent().run_market_analysis()["high_demand_niches"]
    gen = NoteThumbnailGenerator()
    p1 = gen.generate_free_article_thumbnail(niches[0], day=5)
    p2 = gen.generate_paid_pack_thumbnail()
    print("Generated thumbnails:", p1, p2)
