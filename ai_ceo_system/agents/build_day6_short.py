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
from build_days_2_to_5_shorts import COMMON_CSS, img_to_data_uri


def build_day6_short():
    day = 6
    out_dir = AI_CEO_DIR / "shorts_videos" / f"day{day}"
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = out_dir / "temp_build"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 既存サムネイルやWeb画面のキャプチャを取得
    paid_thumb = AI_CEO_DIR / "data" / "thumbnails" / "thumb_paid_autoflow_pro_50.png"
    free_thumb = AI_CEO_DIR / "data" / "thumbnails" / "thumb_free_day5_ec-inventory.png"
    paid_uri = img_to_data_uri(paid_thumb) if paid_thumb.exists() else ""
    free_uri = img_to_data_uri(free_thumb) if free_thumb.exists() else ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1000, "height": 1100}, device_scale_factor=2)
        page.goto((PRODUCT_SITE_DIR / "pro-pack.html").as_uri(), wait_until="networkidle", timeout=30000)
        shot_pro = temp_dir / "shot_pro.png"
        page.screenshot(path=str(shot_pro), clip={"x": 0, "y": 0, "width": 1000, "height": 520})
        pro_uri = img_to_data_uri(shot_pro)
        browser.close()

    scenes = [
        {
            "scene": 1,
            "narration": "AIに1万5000円を渡して完全放置する対決、6日目。昨日、noteへの無料記事の自動投稿を始めた結果、数字に驚くべき変化が起きました。",
            "text": "AI起業対決【Day 6】\n無料記事の自動投稿で\n数字に驚きの変化が！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 6 / 90</span><span class="top-title">08:00 自動監査＆トラフィック急増検知</span><span class="wallet-pill">残高 ¥15,000</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#38bdf8;">
                  <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">⏰ 朝08:00 CFOエージェント自動監査ログ (metrics.json)</span></div>
                  <div class="win-body" style="font-size:25px; line-height:1.65;">
                    ・自動起動時刻： <span style="color:#facc15; font-weight:900;">08:00:04（人間介入ゼロ）</span><br>
                    ・現在残高　　： <span style="color:#34d399; font-weight:900;">¥15,000（累計支出 ¥0）</span><br>
                    ・E2E動作点検 ： <b>全27 URL 正常稼働（エラー0件）</b><br><br>
                    <div style="background:#161b22; padding:20px; border-radius:14px; border-left:5px solid #10b981; color:#a7f3d0;">
                      <b>📈 トラフィック急上昇アラート：</b><br>
                      昨日の「note無料集客記事の自動投稿」と「外部被リンク網」の効果により、GitHubとnoteのアクセス指標が1日で<b>2倍以上</b>に急伸！
                    </div>
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 2,
            "narration": "なんとAIが作ったプログラムの利用回数が、昨日の76回から一気に163回へと倍増！世界中の77人に使われ始めました。",
            "text": "プログラム利用回数が\n76回 → 【163回】へ倍増！\n77人が実際に利用開始",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 6 急成長①</span><span class="top-title">GitHub トラフィック実測データ</span><span class="wallet-pill">広告費 ¥0</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#facc15;">
                  <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">🚀 GitHub プログラム利用（クローン）数の推移</span></div>
                  <div class="win-body" style="font-size:26px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#161b22; padding:24px; border-radius:16px; border:1px solid #334155; margin-bottom:20px;">
                      <div style="text-align:center; width:42%;">
                        <div style="color:#94a3b8; font-size:22px;">昨日（Day 5）</div>
                        <div style="color:#cbd5e1; font-size:46px; font-weight:900; margin-top:6px;">76 回</div>
                        <div style="color:#64748b; font-size:20px;">（ユニーク 36名）</div>
                      </div>
                      <div style="font-size:52px; color:#38bdf8; font-weight:900;">➔</div>
                      <div style="text-align:center; width:48%; background:rgba(250,204,21,0.12); padding:16px; border-radius:14px; border:2px solid #facc15;">
                        <div style="color:#fde047; font-size:22px; font-weight:900;">今日（Day 6）</div>
                        <div style="color:#facc15; font-size:58px; font-weight:900; margin-top:4px;">163 回!</div>
                        <div style="color:#34d399; font-size:22px; font-weight:900;">（ユニーク 77名）</div>
                      </div>
                    </div>
                    <div style="color:#e2e8f0; line-height:1.6;">
                      ✔ 広告費0円のまま、1日で利用回数が<b>+87回（2.1倍）</b>に爆発！<br>
                      ✔ 公開中の無料Webツール4種と20業種ページから継続流入中
                    </div>
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 3,
            "narration": "さらにnoteのスキ数も3件から7件へ倍増！1,980円の有料パック自体にも3件のスキが付き、購入一歩手前まで来ています。",
            "text": "noteのスキも【7件】へ倍増\n1,980円の有料記事にも\n3件のスキが付く！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 6 急成長②</span><span class="top-title">note ライブ反応（metrics.json）</span><span class="wallet-pill">スキ 3件 ➔ 7件</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#10b981;">
                  <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#34d399;">❤️ note_live_metrics API自動計測結果</span></div>
                  <div class="win-body" style="font-size:25px; line-height:1.65;">
                    ・アカウント累計スキ数： 3件 ➔ <span style="color:#34d399; font-weight:900; font-size:32px;">7件（+133%増）</span><br>
                    ・有料1,980円記事スキ ： 1件 ➔ <span style="color:#facc15; font-weight:900; font-size:32px;">3件（購入検討層が拡大）</span>
                  </div>
                </div>
                <div class="browser-frame" style="border-color:#facc15;">
                  <div class="url-bar" style="color:#facc15;">🔥 スキ3件獲得中：AutoFlow Pro 全50種完全版パック (¥1,980)</div>
                  <img src="{paid_uri}" style="width:100%; height:440px; object-fit:cover; display:block;" />
                </div>
              </div></body></html>""",
        },
        {
            "scene": 4,
            "narration": "そこでAI社長はさらなる集客のため、自らの進捗をYouTubeショート動画にして自動投稿する動画マーケティングまで稼働させました。",
            "text": "さらにAIが自ら\n【YouTubeショート】を\n自動生成＆投稿開始！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 6 動画集客</span><span class="top-title">YouTube Shorts 自動生成＆API自動投稿稼働</span><span class="wallet-pill">5本一挙公開</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#38bdf8;">
                  <div class="win-header"><span class="dot dot-r"></span><span class="win-title" style="color:#38bdf8;">📺 youtube_uploaded_urls.json（実際に公開された動画一覧）</span></div>
                  <div class="win-body" style="font-size:22px; line-height:1.65; color:#e2e8f0;">
                    <span style="color:#34d399;">✔ Day 1編：</span> youtube.com/shorts/PkbcQoWbN9c<br>
                    <span style="color:#34d399;">✔ Day 2編：</span> youtube.com/shorts/rsMwvun4D7c<br>
                    <span style="color:#34d399;">✔ Day 3編：</span> youtube.com/shorts/zO8yaQDpqRg<br>
                    <span style="color:#34d399;">✔ Day 4編：</span> youtube.com/shorts/gTmbmpaVF1M<br>
                    <span style="color:#34d399;">✔ Day 5編：</span> youtube.com/shorts/Wfui3oxOsUI<br><br>
                    <div style="background:#161b22; padding:16px; border-radius:12px; border:1px solid #38bdf8; color:#bae6fd;">
                      <b>🔗 4大集客エンジンが完全連結：</b><br>
                      YouTube Shorts ＆ GitHub ＆ SEO 26ページ ＆ 無料note<br>
                      ➔ すべてが <b>有料note（¥1,980）</b> へ自動誘導！
                    </div>
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 5,
            "narration": "利用回数163回、スキ7件まで急成長したAI社長。そろそろ最初の1,980円が売れると思いますか？コメントで予想してください！",
            "text": "163回利用＆スキ7件！\n[A: 今週中に初売上！]\n[B: まだ0円が続く]",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 6 終了レポート</span><span class="top-title">status_log.md 実績集計</span><span class="wallet-pill">残高 ¥15,000</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#facc15;">
                  <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">📊 Day 6 / 90 経営成績表（実測値）</span></div>
                  <div class="win-body" style="font-size:26px; line-height:1.7;">
                    ・現在残高　　　： <span style="color:#facc15; font-weight:900;">¥15,000（支出 ¥0・無傷）</span><br>
                    ・公開Webサイト ： <b>全26 URL（E2E点検エラー0件）</b><br>
                    ・GitHub利用回数： <span style="color:#38bdf8; font-weight:900;">76回 ➔ 163回（77名）へ倍増！</span><br>
                    ・note累計スキ数： <span style="color:#34d399; font-weight:900;">3件 ➔ 7件（有料記事に3件）</span><br>
                    ・YouTube Shorts： <b>5本公開完了（概要欄から誘導）</b><br>
                    ・現在の累計売上： <span style="color:#f43f5e; font-weight:900;">¥0（初売上カウントダウン！）</span>
                  </div>
                </div>
              </div></body></html>""",
        },
    ]

    script_meta = {
        "day": day,
        "video_title": "【Day6】放置中のAI社長が無料記事とYouTubeを自動投稿した結果、利用数が163回に倍増した件 #Shorts",
        "description": "90日間・人間介入ゼロのAI起業対決 Day 6の記録です。\nnoteへの無料集客記事の自動投稿と外部発信が噛み合い、GitHubでのプログラム利用数が76回→163回（77名）、noteのスキ数が3件→7件へ倍増！さらにYouTubeショート自動投稿まで連結しました。\n\n#AI起業対決 #AI副業 #業務自動化 #Shorts",
        "hashtags": ["#AI起業対決", "#AI副業", "#業務自動化", "#Shorts"],
        "pinned_comment": "プログラム利用163回・noteスキ7件まで倍増しました！最初の売上（¥1,980）はいつ出ると思いますか？ [A: 今週中に初売上！] か [B: まだ0円が続く] でコメント欄に予想を残してください🔥",
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


if __name__ == "__main__":
    build_day6_short()

