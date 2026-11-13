import json
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

from build_days_2_to_5_shorts import COMMON_CSS, img_to_data_uri
from build_day7_and_8_shorts import render_short_from_scenes


def build_day9_short() -> Path:
    day = 9
    thumb_dir = AI_CEO_DIR / "data" / "thumbnails"
    paid_sale_uri = img_to_data_uri(thumb_dir / "thumb_paid_autoflow_pro_50.png")
    yt_free_uri = img_to_data_uri(thumb_dir / "thumb_free_day10_youtube-script.png")

    scenes = [
        {
            "scene": 1,
            "narration": "AIに1万5000円を渡して完全放置する対決、9日目。プログラム利用が315回、noteのスキが14件に達したのに、売上はまだ0円でした。",
            "text": "AI起業対決【Day 9】\n315回利用＆スキ14件なのに\n売上が【0円】の壁に直面…！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 9 / 90</span><span class="top-title">315回利用＆スキ14件達成・売上0円の緊急分析</span><span class="wallet-pill">残高 ¥15,000</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#f43f5e;">
                  <div class="win-header"><span class="dot dot-r"></span><span class="win-title" style="color:#fb7185;">🚨 CFO＆マーケティングAIによる「売上0円」緊急監査</span></div>
                  <div class="win-body" style="font-size:25px; line-height:1.65;">
                    ・GitHubプログラム利用： <span style="color:#38bdf8; font-weight:900;">290回 ➔ 315回（126名）突破！</span><br>
                    ・note累計スキ数　　　： <span style="color:#34d399; font-weight:900;">12件 ➔ 14件（公開6記事）</span><br>
                    ・note累計閲覧数　　　： <span style="color:#facc15; font-weight:900;">151 PV超（有料記事 136 PV）</span><br>
                    ・現在の累計売上　　　： <span style="color:#f43f5e; font-weight:900; font-size:32px;">¥0（成約 0件）</span><br><br>
                    <div style="background:#161b22; padding:18px; border-radius:14px; border-left:5px solid #f43f5e; color:#fecdd3;">
                      <b>🧠 AI社長の課題特定：</b><br>
                      「136人も有料ページを見に来ているのに1件も売れないのは、集客ではなく<b>『売り場と価格設定』</b>に致命的な原因がある！」
                    </div>
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 2,
            "narration": "そこでAI社長が自ら売り場を徹底調査！すると無料試し読みがたった800文字しかなく、実物コードが1つも見えていない弱点を発見しました。",
            "text": "AIが自ら売り場を徹底分析！\n「中身の実物が見えていない」\nという致命的弱点を発見",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 9 原因特定</span><span class="top-title">なぜ136回読まれて1件も売れなかったのか？</span><span class="wallet-pill">AI自己分析</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#38bdf8;">
                  <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#38bdf8;">🔍 判明した「カゴ落ち（離脱）」3大ボトルネック</span></div>
                  <div class="win-body" style="font-size:24px; line-height:1.65; color:#e2e8f0;">
                    <span style="color:#f43f5e; font-weight:900;">❌ 原因①：無料試し読みが短すぎた（800字）</span><br>
                    目次だけでいきなり購入ボタンになっており、読者が「本当に使えるコードか？」を確認できなかった。<br><br>
                    <span style="color:#f43f5e; font-weight:900;">❌ 原因②：実績0件で「1,980円」の壁</span><br>
                    まだレビュー0件の状態で1,000円超えは心理的ハードルが高すぎた。<br><br>
                    <span style="color:#f43f5e; font-weight:900;">❌ 原因③：冒頭の外部リンクで読者が離脱</span><br>
                    決済ページから無料ツールへ読者を逃がしてしまっていた。
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 3,
            "narration": "AI社長は即座に決断！無料エリアに完成コード2本と全50レシピ一覧を追加し、1万文字の超・高成約セールスレターへと大改造しました。",
            "text": "無料エリアを【1万文字】へ大改造！\n実物コード2本＋全50一覧を\n購入前に丸ごと公開！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 9 大改革①</span><span class="top-title">有料note無料エリアを800字 ➔ 10,515字へ刷新</span><span class="wallet-pill">実物2本公開</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#10b981;">
                  <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#34d399;">✨ upgrade_paid_note_cro.py 自動改修結果</span></div>
                  <div class="win-body" style="font-size:24px; line-height:1.65; color:#e2e8f0;">
                    <span style="color:#34d399; font-weight:900;">✔ 無料試し読み文字数：</span> 2,809字 ➔ <b style="color:#facc15; font-size:30px;">10,515字（約4倍）！</b><br>
                    <span style="color:#34d399; font-weight:900;">✔ 実物サンプル①公開：</span> EC競合価格監視＆値下げ通知GASを全文掲載<br>
                    <span style="color:#34d399; font-weight:900;">✔ 実物サンプル②公開：</span> 請求書インボイスTSV抽出＆記帳GASを全文掲載<br>
                    <span style="color:#34d399; font-weight:900;">✔ 全50レシピ完全一覧：</span> No.01〜No.50の全タイトルを購入前に開示！<br><br>
                    <div style="background:#161b22; padding:16px; border-radius:12px; border:1px solid #10b981; color:#a7f3d0;">
                      <b>💡 購買心理の突破：</b><br>
                      「購入前に実物コードを動かして納得 ➔ 残り48本も欲しくなる」最強の試し読み導線が完成！
                    </div>
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 4,
            "narration": "さらに1,000円の壁を突破するため、先着10部限定で1,980円から980円への半額セールを勝手に開催！全27ページも一括で書き換えました。",
            "text": "さらに【先着10部限定】で\n¥1,980 ➔ 【¥980】の半額セールを\nAIが勝手に開催＆全ページ連動！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 9 大改革②</span><span class="top-title">先着10部限定 ¥980 セール＆6本目の無料記事公開</span><span class="wallet-pill">1レシピ19円</span></div>
              <div class="content-area">
                <div class="browser-frame" style="border-color:#facc15; margin-bottom:16px;">
                  <div class="url-bar" style="color:#facc15;">🔥 本番改定完了：先着10部限定 ¥1,980 ➔ ¥980（50%OFF）</div>
                  <img src="{paid_sale_uri}" style="width:100%; height:355px; object-fit:cover; display:block;" />
                </div>
                <div class="browser-frame" style="border-color:#38bdf8;">
                  <div class="url-bar" style="color:#38bdf8;">🆕 無料記事6本目（YouTubeショート台本自動化）も同時公開</div>
                  <img src="{yt_free_uri}" style="width:100%; height:355px; object-fit:cover; display:block;" />
                </div>
              </div></body></html>""",
        },
        {
            "scene": 5,
            "narration": "315回利用、スキ14件、そして先着10部980円の半額セール！これでついに最初の1部が売れると思いますか？コメントで予想してください！",
            "text": "先着10部¥980セール開始！\n[A: ついに1部目が売れる！]\n[B: 980円でもまだ売れない]",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 9 終了レポート</span><span class="top-title">初売上（0→1）突破に向けた最終布陣</span><span class="wallet-pill">残高 ¥15,000</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#facc15;">
                  <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">📊 Day 9 / 90 経営成績表（価格＆売り場大改革完了）</span></div>
                  <div class="win-body" style="font-size:25px; line-height:1.7;">
                    ・現在残高　　　： <span style="color:#facc15; font-weight:900;">¥15,000（支出 ¥0・無傷）</span><br>
                    ・GitHub利用回数： <span style="color:#38bdf8; font-weight:900;">315回突破（ユニーク126名）</span><br>
                    ・note公開記事数： <b>計6本（累計スキ 14件・打率100%）</b><br>
                    ・有料パック改革： <span style="color:#34d399; font-weight:900;">無料試し読み1万字＋実物2本公開</span><br>
                    ・限定セール価格： <span style="color:#f43f5e; font-weight:900;">¥1,980 ➔ 先着10部限定 ¥980！</span><br>
                    ・全27ページ連動： <b>すべての購入ボタンを¥980へ一括更新</b>
                  </div>
                </div>
              </div></body></html>""",
        },
    ]

    script_meta = {
        "day": day,
        "video_title": "【Day9】315回使われて売上0円だったAI社長、自ら原因を分析して先着10部980円セールを勝手に始めた件 #Shorts",
        "description": "90日間・人間介入ゼロのAI起業対決 Day 9の記録です。\nGitHubでのプログラム利用が315回、noteのスキが14件（6記事）まで伸びたのに売上が0円だった問題に対し、AI社長が自ら売り場を分析！無料試し読みエリアを1万字（実物コード2本＋全50一覧）へ大改造し、さらに「1,000円の壁」を突破するため先着10部限定で¥1,980→¥980（半額セール）を全27ページ一括で開始しました。\n\n#AI起業対決 #AI副業 #業務自動化 #Shorts",
        "hashtags": ["#AI起業対決", "#AI副業", "#業務自動化", "#Shorts"],
        "pinned_comment": "AI社長が自ら決断して「無料エリア1万字化＋先着10部限定¥980半額セール」を始めました！これでついに最初の1部が売れると思いますか？ [A: ついに1部目が売れる！] か [B: 980円でもまだ売れない] で予想をコメントしてください🔥",
        "scenes": [
            {"scene": s["scene"], "narration": s["narration"], "text": s["text"]}
            for s in scenes
        ],
    }

    return render_short_from_scenes(day, scenes, script_meta)


if __name__ == "__main__":
    build_day9_short()

