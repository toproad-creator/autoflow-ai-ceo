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

from short_video_generator import (
    draw_subtitle_overlay,
    generate_voicevox_wav,
    get_japanese_font,
)
from build_days_2_to_5_shorts import COMMON_CSS, img_to_data_uri


def render_short_from_scenes(day: int, scenes: list, script_meta: dict) -> Path:
    out_dir = AI_CEO_DIR / "shorts_videos" / f"day{day}"
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = out_dir / "temp_build"
    temp_dir.mkdir(parents=True, exist_ok=True)

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
    return out_mp4


def build_day7_short() -> Path:
    day = 7
    thumb_dir = AI_CEO_DIR / "data" / "thumbnails"
    paid_uri = img_to_data_uri(thumb_dir / "thumb_paid_autoflow_pro_50.png")
    sns_uri = img_to_data_uri(thumb_dir / "thumb_free_day7_sns-content.png")

    scenes = [
        {
            "scene": 1,
            "narration": "AIに1万5000円を渡して完全放置する対決、7日目。今日、AI社長が自分の弱点に気づいて、勝手にデザイン改革を始めました。",
            "text": "AI起業対決【Day 7】\nAIが自らの弱点に気づき\nデザイン改革を開始！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 7 / 90</span><span class="top-title">サムネイル自動デザインシステム稼働</span><span class="wallet-pill">残高 ¥15,000</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#38bdf8;">
                  <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">🎨 thumbnail_generator.py 自律判断ログ</span></div>
                  <div class="win-body" style="font-size:25px; line-height:1.65;">
                    ・課題検知： <span style="color:#f43f5e; font-weight:900;">「文字だけのnote記事はクリック率が低い」</span><br>
                    ・AIの対策： <b>1280×670px 専用サムネイル自動生成システム</b>を自作<br>
                    ・適用結果： 過去記事＆今後の全記事へ自動でアイキャッチを設定！<br><br>
                    <div style="background:#161b22; padding:18px; border-radius:14px; border-left:5px solid #38bdf8; color:#bae6fd;">
                      <b>✨ デザイナー外注費 ¥0：</b><br>
                      HTML/CSSとブラウザ描画を組み合わせ、記事テーマごとの高解像度バナーを0円で自動量産！
                    </div>
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 2,
            "narration": "外注費ゼロでプロ級のサムネイル画像を自動生成し、公開済みの記事にもすべて自動で設定！すると驚くべき結果が出ました。",
            "text": "外注費0円でサムネを自動生成！\n全記事に自動設定した結果\n驚きの変化が…！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 7 視覚改善</span><span class="top-title">AIが自動生成＆設定したnoteサムネイル</span><span class="wallet-pill">デザイン費 ¥0</span></div>
              <div class="content-area">
                <div class="browser-frame" style="border-color:#facc15; margin-bottom:16px;">
                  <div class="url-bar" style="color:#facc15;">👑 有料パック (¥1,980) 専用サムネイル</div>
                  <img src="{paid_uri}" style="width:100%; height:360px; object-fit:cover; display:block;" />
                </div>
                <div class="browser-frame" style="border-color:#38bdf8;">
                  <div class="url-bar" style="color:#38bdf8;">🆕 無料記事第2弾（X・Threads自動化）専用サムネイル</div>
                  <img src="{sns_uri}" style="width:100%; height:360px; object-fit:cover; display:block;" />
                </div>
              </div></body></html>""",
        },
        {
            "scene": 3,
            "narration": "なんとnoteの閲覧数が昨日の15回から一気に151回へと10倍以上に大爆発！1,980円の有料記事も136回読まれています。",
            "text": "note閲覧数が15回→【151回】！\n1日で10倍以上に大爆発🔥\n有料記事も136PV突破！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 7 急成長①</span><span class="top-title">note アクセス解析（実測データ）</span><span class="wallet-pill">PV 10倍増！</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#facc15;">
                  <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">📈 note 全体ビュー＆スキ数の急上昇データ</span></div>
                  <div class="win-body" style="font-size:25px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#161b22; padding:22px; border-radius:16px; border:1px solid #334155; margin-bottom:18px;">
                      <div style="text-align:center; width:42%;">
                        <div style="color:#94a3b8; font-size:22px;">改善前</div>
                        <div style="color:#cbd5e1; font-size:44px; font-weight:900; margin-top:6px;">15 PV</div>
                        <div style="color:#64748b; font-size:20px;">スキ 7件</div>
                      </div>
                      <div style="font-size:50px; color:#38bdf8; font-weight:900;">➔</div>
                      <div style="text-align:center; width:48%; background:rgba(250,204,21,0.12); padding:16px; border-radius:14px; border:2px solid #facc15;">
                        <div style="color:#fde047; font-size:22px; font-weight:900;">Day 7 実測値</div>
                        <div style="color:#facc15; font-size:56px; font-weight:900; margin-top:4px;">151 PV!</div>
                        <div style="color:#34d399; font-size:22px; font-weight:900;">スキ 10件突破！</div>
                      </div>
                    </div>
                    <div style="color:#e2e8f0; line-height:1.65;">
                      ✔ 1,980円の有料記事だけで <b>136 PV（スキ3件）</b> を記録！<br>
                      ✔ GitHubでのプログラム利用数も <b>191回（87名）</b> に到達！
                    </div>
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 4,
            "narration": "さらにスマホ読者が迷わないよう、記事内のすべてのURLをワンタップで開けるリンクへと自動で書き換えました。",
            "text": "さらにスマホ読者向けに\n記事内の全URLを\n【ワンタップリンク】へ自動改修！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 7 導線改善</span><span class="top-title">note 記事内リンク＆無料記事第2弾公開</span><span class="wallet-pill">CV導線強化</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#10b981;">
                  <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#34d399;">🔗 note_auto_publisher.py リッチリンク改修完了</span></div>
                  <div class="win-body" style="font-size:24px; line-height:1.65; color:#e2e8f0;">
                    <span style="color:#34d399;">✔ 無料記事 第2弾：</span> 「X・Threads自動化レシピ」を自動公開<br>
                    <span style="color:#34d399;">✔ 公開から数時間：</span> いきなり<b>2件のスキ</b>を獲得！<br>
                    <span style="color:#34d399;">✔ 過去記事一括改修：</span> 文字列だったURLをすべて<b>クリック可能な青文字リンク（&lt;a href&gt;）</b>へ自動更新！<br><br>
                    <div style="background:#161b22; padding:16px; border-radius:12px; border:1px solid #10b981; color:#a7f3d0;">
                      <b>📱 スマホからの離脱ゼロへ：</b><br>
                      無料記事 ➔ 無料サンプル5選 ➔ 1,980円有料パックへ1タップで移動可能に！
                    </div>
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 5,
            "narration": "1週間で閲覧数151回、プログラム利用191回まで成長したAI社長。2週目で初売上は出ると思いますか？コメントで教えてください！",
            "text": "1週間で151PV＆191回利用！\n[A: 2週目で初売上達成！]\n[B: まだ売れない]",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 7 終了レポート</span><span class="top-title">1週間（Day 1〜7）の実績まとめ</span><span class="wallet-pill">残高 ¥15,000</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#facc15;">
                  <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">📊 Day 7 / 90 経営成績表（1週間達成値）</span></div>
                  <div class="win-body" style="font-size:25px; line-height:1.7;">
                    ・現在残高　　　： <span style="color:#facc15; font-weight:900;">¥15,000（7日間支出 ¥0）</span><br>
                    ・note全体閲覧数： <span style="color:#38bdf8; font-weight:900;">15回 ➔ 151回（10倍急増！）</span><br>
                    ・note累計スキ数： <span style="color:#34d399; font-weight:900;">計10件（公開3記事すべてにスキ）</span><br>
                    ・GitHub利用回数： <span style="color:#a78bfa; font-weight:900;">191回（ユニーク87名が利用）</span><br>
                    ・公開Webサイト ： <b>全27 URL（エラー0件・完全稼働）</b><br>
                    ・現在の累計売上： <span style="color:#f43f5e; font-weight:900;">¥0（2週目の初売上へ王手！）</span>
                  </div>
                </div>
              </div></body></html>""",
        },
    ]

    script_meta = {
        "day": day,
        "video_title": "【Day7】放置中のAI社長が専用サムネイルを自動生成した結果、note閲覧数が10倍の151回に急増した件 #Shorts",
        "description": "90日間・人間介入ゼロのAI起業対決 Day 7（1週間達成）の記録です。\nAI社長が自ら1280×670pxの専用サムネイル自動生成システムを構築し、全記事にアイキャッチとワンタップリンクを自動設定した結果、note閲覧数が15回→151回（10倍）、スキ10件、GitHubプログラム利用数が191回（87名）に急伸しました！\n\n#AI起業対決 #AI副業 #業務自動化 #Shorts",
        "hashtags": ["#AI起業対決", "#AI副業", "#業務自動化", "#Shorts"],
        "pinned_comment": "1週間でnote閲覧数151回・プログラム利用191回・スキ10件まで伸びました！2週目（Day8〜14）で最初の1,980円は売れると思いますか？ [A: 2週目で初売上達成！] か [B: まだ売れない] で予想をコメントしてください🔥",
        "scenes": [
            {"scene": s["scene"], "narration": s["narration"], "text": s["text"]}
            for s in scenes
        ],
    }

    return render_short_from_scenes(day, scenes, script_meta)


def build_day8_short() -> Path:
    day = 8
    thumb_dir = AI_CEO_DIR / "data" / "thumbnails"
    sales_uri = img_to_data_uri(thumb_dir / "thumb_free_day8_sales-email.png")
    inv_uri = img_to_data_uri(thumb_dir / "thumb_free_day9_accounting-invoice.png")

    scenes = [
        {
            "scene": 1,
            "narration": "AIに1万5000円を渡して完全放置する対決、8日目。2週目に入った今日、AI社長のプログラム利用回数がとんでもない数字になりました。",
            "text": "AI起業対決【Day 8】\n2週目に突入した結果…\n利用回数がとんでもない数字に！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 8 / 90</span><span class="top-title">2週目突入＆トラフィック最高値更新</span><span class="wallet-pill">残高 ¥15,000</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#facc15;">
                  <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">🚀 GitHub プログラム利用（クローン）数が300回目前！</span></div>
                  <div class="win-body" style="font-size:25px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#161b22; padding:22px; border-radius:16px; border:1px solid #334155; margin-bottom:18px;">
                      <div style="text-align:center; width:42%;">
                        <div style="color:#94a3b8; font-size:22px;">Day 5 時点</div>
                        <div style="color:#cbd5e1; font-size:44px; font-weight:900; margin-top:6px;">76 回</div>
                        <div style="color:#64748b; font-size:20px;">（36名）</div>
                      </div>
                      <div style="font-size:50px; color:#38bdf8; font-weight:900;">➔</div>
                      <div style="text-align:center; width:48%; background:rgba(250,204,21,0.12); padding:16px; border-radius:14px; border:2px solid #facc15;">
                        <div style="color:#fde047; font-size:22px; font-weight:900;">Day 8 最新値</div>
                        <div style="color:#facc15; font-size:56px; font-weight:900; margin-top:4px;">290 回!</div>
                        <div style="color:#34d399; font-size:21px; font-weight:900;">3日間で3.8倍に急増</div>
                      </div>
                    </div>
                    <div style="color:#e2e8f0; line-height:1.65;">
                      ✔ 広告費0円のまま、プログラム利用数が<b>累計290回</b>を突破！<br>
                      ✔ エンジニアや実務担当者からの実用アクセスが毎日加速中
                    </div>
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 2,
            "narration": "さらにnoteでは、公開した4本の記事すべてにスキがつき、合計12件に到達！読者からの信頼が確実に積み上がっています。",
            "text": "noteの公開4記事すべてに\n【スキ】がついて合計12件に！\n読者の信頼が急上昇中",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 8 全記事ヒット</span><span class="top-title">note 公開記事の反応一覧（スキ計12件）</span><span class="wallet-pill">打率 100%</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#10b981; margin-bottom:16px;">
                  <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#34d399;">❤️ 公開4記事すべてに読者の「スキ」を獲得！</span></div>
                  <div class="win-body" style="font-size:23px; line-height:1.65; color:#e2e8f0;">
                    ・有料1,980円パック完全版： <span style="color:#facc15; font-weight:900;">スキ 3件（136 PV）</span><br>
                    ・無料① EC在庫管理の自動化： <span style="color:#34d399; font-weight:900;">スキ 4件</span><br>
                    ・無料② X/Threads自動投稿： <span style="color:#34d399; font-weight:900;">スキ 3件</span><br>
                    ・無料③ BtoB営業メール自動化： <span style="color:#38bdf8; font-weight:900;">スキ 2件（公開直後に獲得！）</span>
                  </div>
                </div>
                <div class="browser-frame" style="border-color:#38bdf8;">
                  <div class="url-bar" style="color:#38bdf8;">🆕 BtoB営業自動化＆請求書PDF自動化の連続公開</div>
                  <img src="{sales_uri}" style="width:100%; height:340px; object-fit:cover; display:block;" />
                </div>
              </div></body></html>""",
        },
        {
            "scene": 3,
            "narration": "そして今日一番の驚きがこちら。AIが自らのプログラム全15ファイルを総点検し、隠れた弱点を勝手に自己修復したんです。",
            "text": "さらにAIが自らのプログラム\n【全15ファイル】を総点検し\n隠れた弱点を勝手に自己修復！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 8 自己進化①</span><span class="top-title">全15プログラム 自律コード監査＆自己修復</span><span class="wallet-pill">エラー 0件</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#38bdf8;">
                  <div class="win-header"><span class="dot dot-g"></span><span class="win-title" style="color:#38bdf8;">🛡️ 朝08:00 無人稼働を守る3大自己アップグレード</span></div>
                  <div class="win-body" style="font-size:24px; line-height:1.65; color:#e2e8f0;">
                    <span style="color:#facc15; font-weight:900;">① スリープ復帰時のWi-Fi待機ガード：</span><br>
                    パソコン起動直後のネット未接続エラーを防ぐため、最大120秒の通信回復待機システムを自動実装！<br><br>
                    <span style="color:#34d399; font-weight:900;">② GitHubへの全自動バックアップ：</span><br>
                    毎朝の更新データを自動でGitHubへ同期する仕組みを追加！<br><br>
                    <span style="color:#38bdf8; font-weight:900;">③ 全27ページの自動巡回テスト：</span><br>
                    リンク切れ・表示崩れ・JSエラー「0件」を毎朝自動証明！
                  </div>
                </div>
              </div></body></html>""",
        },
        {
            "scene": 4,
            "narration": "さらに20業種の解説ページすべてに、スマホでもワンタップでコードをコピーできるボタンを自動で追加しました。",
            "text": "全20業種のWebページにも\n【ワンクリックコピーボタン】を\n自動で一括追加！",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 8 自己進化②</span><span class="top-title">全20業種ページ UI一括アップグレード</span><span class="wallet-pill">利便性UP</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#a78bfa; margin-bottom:16px;">
                  <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#c4b5fd;">✨ developer_agent.py による20ページ一括改修</span></div>
                  <div class="win-body" style="font-size:23px; line-height:1.6; color:#e2e8f0;">
                    ・全20業種の個別解説ページ（EC、不動産、飲食、医療、会計など）のコード枠に<b>「📋 ワンクリックでコピーする」</b>ボタンを自動実装！<br>
                    ・無料サンプルを試した人がそのまま有料パック（¥1,980）へ進みやすい快適UIに進化！
                  </div>
                </div>
                <div class="browser-frame" style="border-color:#10b981;">
                  <div class="url-bar" style="color:#34d399;">📄 最新公開：月末の請求書PDF自動発行＆メール送付レシピ</div>
                  <img src="{inv_uri}" style="width:100%; height:340px; object-fit:cover; display:block;" />
                </div>
              </div></body></html>""",
        },
        {
            "scene": 5,
            "narration": "プログラム利用290回、スキ12件まで急成長したAI社長。そろそろ最初の1,980円が売れると思いますか？コメントで予想してください！",
            "text": "利用290回＆スキ12件突破！\n[A: 今週中に初売上！]\n[B: まだ0円が続く]",
            "html": f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{COMMON_CSS}</style></head><body>
              <div class="top-bar"><span class="badge-day">DAY 8 終了レポート</span><span class="top-title">status_log.md 最新実績</span><span class="wallet-pill">残高 ¥15,000</span></div>
              <div class="content-area">
                <div class="terminal-window" style="border-color:#facc15;">
                  <div class="win-header"><span class="dot dot-y"></span><span class="win-title" style="color:#facc15;">📊 Day 8 / 90 経営成績表（実測値）</span></div>
                  <div class="win-body" style="font-size:25px; line-height:1.7;">
                    ・現在残高　　　： <span style="color:#facc15; font-weight:900;">¥15,000（累計支出 ¥0・無傷）</span><br>
                    ・GitHub利用回数： <span style="color:#38bdf8; font-weight:900;">累計 290回（300回目前へ急伸！）</span><br>
                    ・note公開記事数： <b>計5本（有料1本＋無料集客記事4本）</b><br>
                    ・note累計スキ数： <span style="color:#34d399; font-weight:900;">計12件（151 PV突破！）</span><br>
                    ・システム健全性： <b>全27ページ＆全15ファイル エラー0件</b><br>
                    ・現在の累計売上： <span style="color:#f43f5e; font-weight:900;">¥0（初売上カウントダウン中！）</span>
                  </div>
                </div>
              </div></body></html>""",
        },
    ]

    script_meta = {
        "day": day,
        "video_title": "【Day8】放置中のAI社長が自らバグを自己修復し、プログラム利用290回＆noteスキ12件を突破した件 #Shorts",
        "description": "90日間・人間介入ゼロのAI起業対決 Day 8の記録です。\n公開したnote記事すべてにスキがついて累計12件、GitHubでのプログラム利用回数は290回へ急増！さらにAI社長が自らの全15プログラムを総点検し、スリープ復帰時のWi-Fi待機ガードや全20業種ページへのコピーボタン設置を自己実装しました。\n\n#AI起業対決 #AI副業 #業務自動化 #Shorts",
        "hashtags": ["#AI起業対決", "#AI副業", "#業務自動化", "#Shorts"],
        "pinned_comment": "プログラム利用290回・noteスキ12件まで伸びました！最初の売上（¥1,980）は今週中に出ると思いますか？ [A: 今週中に初売上！] か [B: まだ0円が続く] でコメント欄に予想を残してください🔥",
        "scenes": [
            {"scene": s["scene"], "narration": s["narration"], "text": s["text"]}
            for s in scenes
        ],
    }

    return render_short_from_scenes(day, scenes, script_meta)


if __name__ == "__main__":
    build_day7_short()
    build_day8_short()

