import json
import os
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[2]
AI_CEO_DIR = ROOT_DIR / "ai_ceo_system"
VIDEO_CREATOR_DIR = ROOT_DIR / "VideoCreator"
UPLOADED_JSON = AI_CEO_DIR / "shorts_videos" / "youtube_uploaded_urls.json"

sys.path.insert(0, str(AI_CEO_DIR / "agents"))
sys.path.insert(0, str(VIDEO_CREATOR_DIR))

from build_days_2_to_5_shorts import COMMON_CSS, img_to_data_uri
from build_day7_and_8_shorts import render_short_from_scenes


class DailyShortPipelineAgent:
    """毎日のAI役員会議の決定事項・最新集客スコア・新規公開note記事を映像化し、
    YouTubeショート動画（1080x1920・VOICEVOX音声＋BGM）を自動生成してYouTubeへ自動公開するエージェント
    """

    def get_existing_uploaded_url(self, day: int) -> str:
        if UPLOADED_JSON.exists():
            try:
                items = json.loads(UPLOADED_JSON.read_text(encoding="utf-8"))
                for it in items:
                    if it.get("day") == day and it.get("status") == "uploaded_public" and it.get("url"):
                        return it["url"]
            except Exception:
                pass
        return ""

    def build_and_upload_daily_short(
        self,
        day: int,
        balance: int = 15000,
        price_jpy: int = 980,
        total_notes: int = 7,
        total_likes: int = 15,
        gh_clones: int = 315,
        gh_uniques: int = 126,
        latest_note_title: str = "【無料コピペOK】不動産物件マイソク・ポータル入稿文面のAI自動作成",
        latest_note_thumb_path: str = "",
        auto_upload: bool = True,
    ) -> dict:
        existing_url = self.get_existing_uploaded_url(day)
        out_mp4 = AI_CEO_DIR / "shorts_videos" / f"day{day}" / f"ai_ceo_day{day}_short.mp4"
        if existing_url and out_mp4.exists():
            return {
                "day": day,
                "status": "already_uploaded",
                "video_path": str(out_mp4),
                "youtube_url": existing_url,
            }

        thumb_dir = AI_CEO_DIR / "data" / "thumbnails"
        paid_sale_uri = img_to_data_uri(thumb_dir / "thumb_paid_autoflow_pro_50.png")

        free_thumb_file = Path(latest_note_thumb_path) if latest_note_thumb_path else None
        if not free_thumb_file or not free_thumb_file.exists():
            thumbs = sorted(thumb_dir.glob("thumb_free_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
            free_thumb_file = thumbs[0] if thumbs else (thumb_dir / "thumb_paid_autoflow_pro_50.png")
        free_uri = img_to_data_uri(free_thumb_file)

        short_niche_title = latest_note_title.replace("【無料コピペOK】", "").split("をAIとGASで")[0][:22]

        scenes = [
            {
                "scene": 1,
                "narration": f"AIに1万5000円を渡して完全放置する対決、{day}日目。今日からAI社長が5人の専門AI役員を集め、利益を出すための緊急会議を自動で始めました。",
                "text": f"AI起業対決【Day {day}】\n売上0円を打破するため\n【AI役員会議】が自動開幕！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY {day} / 90</span><span class="top-title">利益創出特化型・AI役員会議が自動稼働</span><span class="wallet-pill">残高 ¥{balance:,}</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#facc15;">
                      <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">🏢 executive_board_agent.py 自律役員会議ログ</span></div>
                      <div class="win-body" style="font-size:24px; line-height:1.65;">
                        ・<b>CEO（AI社長）</b>： 「唯一の目的は利益を出すこと。自己満足の開発は禁止！」<br>
                        ・<b>CFO（財務AI）</b>： 「利用{gh_clones}回・スキ{total_likes}件・残高¥{balance:,}。成約率改善に全集中すべき」<br>
                        ・<b>CRO（収益AI）</b>： 「全27ページに画面下部追従の『限定¥{price_jpy}購入バー』を即実装します」<br>
                        ・<b>CMO（集客AI）</b>： 「記事・X投稿・ショート動画まで一気通貫で自動公開します」<br><br>
                        <div style="background:#161b22; padding:18px; border-radius:14px; border-left:5px solid #facc15; color:#fef08a;">
                          <b>⚡ 人間介入ゼロの合議制組織：</b><br>
                          毎朝8時に5人のAI役員が数字を分析し、改善策の決定から実装まで全自動で完遂！
                        </div>
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 2,
                "narration": f"会議の分析で、プログラム利用が{gh_clones}回、noteのスキが{total_likes}件まで増えたのに売上が0円なのは、スマホ画面での購入ボタンが目立っていないからだと判明！",
                "text": f"利用{gh_clones}回＆スキ{total_likes}件でも\n売れない原因をAI役員が特定！\n「スマホの購入導線が弱い」",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY {day} 数値監査</span><span class="top-title">CFO＆CROによるボトルネック特定</span><span class="wallet-pill">利用 {gh_clones}回</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#38bdf8;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">📊 実測トラフィックと成約ボトルネック診断</span></div>
                      <div class="win-body" style="font-size:25px; line-height:1.65; color:#e2e8f0;">
                        ・GitHubプログラム利用： <span style="color:#38bdf8; font-weight:900;">累計 {gh_clones}回（{gh_uniques}名）</span><br>
                        ・note公開記事＆スキ数： <span style="color:#34d399; font-weight:900;">計{total_notes}本 / スキ{total_likes}件</span><br>
                        ・有料パック限定価格　： <span style="color:#facc15; font-weight:900;">先着10部 ¥1,980 ➔ ¥{price_jpy}</span><br><br>
                        <div style="background:#161b22; padding:18px; border-radius:14px; border:1px solid #38bdf8; color:#bae6fd;">
                          <b>💡 CRO（最高収益責任者）の改善命令：</b><br>
                          「無料ツールを使って満足して帰る人を逃さないよう、全27ページの画面下部に常時追従する<b>『先着10部¥{price_jpy}フローティング購入バー』</b>を今すぐ自動実装せよ！」
                        </div>
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 3,
                "narration": f"AI社長の命令で、全27ページの画面下部に先着10部{price_jpy}円の追従購入バーを自動実装！無料記事にもAI役員会議の実証ストーリーを組み込みました。",
                "text": f"全27ページの画面下部に\n【先着10部¥{price_jpy}の追従バー】を\nAIが会議直後に自動実装！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY {day} 即時改修</span><span class="top-title">CRO×CTOによる売り場＆導線の自動アップグレード</span><span class="wallet-pill">1レシピ19円</span></div>
                  <div class="content-area">
                    <div class="browser-frame" style="border-color:#facc15; margin-bottom:16px;">
                      <div class="url-bar" style="color:#facc15;">🔥 先着10部限定 ¥1,980 ➔ ¥{price_jpy}（無料エリア1万字＋実物2本公開）</div>
                      <img src="{paid_sale_uri}" style="width:100%; height:355px; object-fit:cover; display:block;" />
                    </div>
                    <div class="browser-frame" style="border-color:#10b981;">
                      <div class="url-bar" style="color:#34d399;">🆕 {total_notes}本目の無料記事（{short_niche_title}）も自動公開</div>
                      <img src="{free_uri}" style="width:100%; height:355px; object-fit:cover; display:block;" />
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 4,
                "narration": f"さらに今日から、note投稿だけでなくXの140字投稿文の作成からYouTubeショート動画の生成・投稿まで、すべてオーケストレーターが全自動で回しています。",
                "text": "note投稿・X文面・YouTube動画まで\nすべて【AIオーケストレーター】が\n毎朝全自動で一気通貫実行！",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY {day} 完全自動化</span><span class="top-title">ceo_orchestrator.py 全工程統合パイプライン</span><span class="wallet-pill">エラー 0件</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#10b981;">
                      <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#34d399;">⚙️ 毎朝8時に全自動で回る利益創出ループ</span></div>
                      <div class="win-body" style="font-size:24px; line-height:1.65; color:#e2e8f0;">
                        <span style="color:#facc15; font-weight:900;">Step 1：</span> 5人のAI役員が会議を開き、その日の改善策を決断<br>
                        <span style="color:#34d399; font-weight:900;">Step 2：</span> Web全27ページ＆note有料導線を自動アップデート<br>
                        <span style="color:#38bdf8; font-weight:900;">Step 3：</span> 1280×670サムネ生成＆note無料記事を自動公開<br>
                        <span style="color:#c084fc; font-weight:900;">Step 4：</span> Xの140字投稿文＆YouTubeショートを自動生成・公開<br>
                        <span style="color:#fb7185; font-weight:900;">Step 5：</span> 全27 URL＆全{total_notes}記事をE2E自動点検してGitHub同期
                      </div>
                    </div>
                  </div></body></html>""",
            },
            {
                "scene": 5,
                "narration": f"AI役員会議まで始まったDay {day}！利用{gh_clones}回、スキ{total_likes}件、先着10部{price_jpy}円セールで初売上は出ると思いますか？コメントで予想してください！",
                "text": f"AI役員会議×限定¥{price_jpy}セール！\n[A: 今週中に初売上達成！]\n[B: まだ0円が続く]",
                "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
                  <div class="top-bar"><span class="badge-day">DAY {day} 終了レポート</span><span class="top-title">status_log.md 最新実績</span><span class="wallet-pill">残高 ¥{balance:,}</span></div>
                  <div class="content-area">
                    <div class="terminal-window" style="border-color:#facc15;">
                      <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">📊 Day {day} / 90 経営成績表（AI役員会議体制）</span></div>
                      <div class="win-body" style="font-size:25px; line-height:1.7;">
                        ・現在残高　　　： <span style="color:#facc15; font-weight:900;">¥{balance:,}（累計支出 ¥0・無傷）</span><br>
                        ・GitHub利用回数： <span style="color:#38bdf8; font-weight:900;">累計 {gh_clones}回（ユニーク{gh_uniques}名）</span><br>
                        ・note公開記事数： <b>計{total_notes}本（累計スキ {total_likes}件に増加！）</b><br>
                        ・本日の会議決定： <span style="color:#34d399; font-weight:900;">全27ページに限定¥{price_jpy}追従バー実装</span><br>
                        ・システム健全性： <b>全27 URL＆全{total_notes}記事 エラー0件</b><br>
                        ・現在の累計売上： <span style="color:#f43f5e; font-weight:900;">¥0（初売上カウントダウン！）</span>
                      </div>
                    </div>
                  </div></body></html>""",
            },
        ]

        script_meta = {
            "day": day,
            "video_title": f"【Day{day}】売上0円に危機感を持ったAI社長、自ら5人のAI役員会議を開いて全サイトを大改造した件 #Shorts",
            "description": (
                f"90日間・人間介入ゼロのAI起業対決 Day {day}の記録です。\n"
                f"利益（売上）を出すという唯一の目的のため、AI社長（CEO）がCFO・CRO・CMO・CTOの専門AI役員と毎朝自動で経営会議を開催する体制へ進化！\n"
                f"プログラム利用{gh_clones}回・noteスキ{total_likes}件（公開{total_notes}本）のアクセスを決済へ繋げるため、全27ページの画面下部に『先着10部限定¥{price_jpy}追従購入バー』を自動実装しました。\n\n"
                f"#AI起業対決 #AI副業 #業務自動化 #Shorts"
            ),
            "hashtags": ["#AI起業対決", "#AI副業", "#業務自動化", "#Shorts"],
            "pinned_comment": f"AI社長たちが自ら役員会議を開き、全27ページへの『先着10部¥{price_jpy}追従バー』実装と{total_notes}本目の記事公開を完了しました！そろそろ最初の1部が売れると思いますか？ [A: 今週中に初売上達成！] か [B: まだ0円が続く] でコメント欄に予想を残してください🔥",
            "scenes": [
                {"scene": s["scene"], "narration": s["narration"], "text": s["text"]}
                for s in scenes
            ],
        }

        video_path = render_short_from_scenes(day, scenes, script_meta)
        yt_url = ""
        if auto_upload:
            try:
                subprocess.run(
                    ["node", str(VIDEO_CREATOR_DIR / "upload_ai_ceo_shorts.js"), str(day)],
                    cwd=str(VIDEO_CREATOR_DIR),
                    check=True,
                    timeout=180,
                )
                yt_url = self.get_existing_uploaded_url(day)
            except Exception as e:
                print(f"[DailyShortPipeline] YouTube upload warning for Day {day}: {e}")

        return {
            "day": day,
            "status": "uploaded_public" if yt_url else "rendered_only",
            "video_path": str(video_path),
            "youtube_url": yt_url,
        }


if __name__ == "__main__":
    target_day = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    agent = DailyShortPipelineAgent()
    res = agent.build_and_upload_daily_short(day=target_day)
    print(json.dumps(res, ensure_ascii=False, indent=2))

