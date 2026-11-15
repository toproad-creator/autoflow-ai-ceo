import json
import math
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[2]
AI_CEO_DIR = ROOT_DIR / "ai_ceo_system"
VIDEO_CREATOR_DIR = ROOT_DIR / "VideoCreator"
DATA_DIR = AI_CEO_DIR / "data"
MARKETING_DIR = AI_CEO_DIR / "marketing_outputs"
COMMAND_CENTER_HTML = AI_CEO_DIR / "product_site" / "command-center.html"
STATE_JSON_PATH = DATA_DIR / "learning_loop_state.json"

OUT_MP4 = MARKETING_DIR / "x_learning_loop_demo.mp4"
OUT_PREVIEW = MARKETING_DIR / "x_learning_loop_preview.png"
OUT_POST_TXT = MARKETING_DIR / "x_learning_loop_post.txt"

BGM_CANDIDATES = [
    VIDEO_CREATOR_DIR / "assets" / "audio" / "presets" / "dark_tension" / "bgm.mp3",
    VIDEO_CREATOR_DIR / "assets" / "audio" / "bgm.mp3",
]

VOICEVOX_EXE = Path(r"C:\Users\yukar\AppData\Local\Programs\VOICEVOX\vv-engine\run.exe")
VOICEVOX_BASE = "http://localhost:50021"

sys.path.insert(0, str(AI_CEO_DIR / "agents"))
sys.path.insert(0, str(VIDEO_CREATOR_DIR))
from learning_loop_agent import LearningLoopAgent


def load_or_build_state() -> dict:
    if STATE_JSON_PATH.exists():
        try:
            data = json.loads(STATE_JSON_PATH.read_text(encoding="utf-8"))
            if data.get("board_meeting", {}).get("executives"):
                return data
        except Exception:
            pass
    return LearningLoopAgent().run_learning_cycle()


def find_bgm_path() -> Path | None:
    for cand in BGM_CANDIDATES:
        if cand.exists() and cand.stat().st_size > 1000:
            return cand
    return None


def ensure_voicevox_running() -> bool:
    try:
        with urllib.request.urlopen(f"{VOICEVOX_BASE}/version", timeout=2) as resp:
            if resp.status == 200:
                return True
    except Exception:
        pass

    if VOICEVOX_EXE.exists():
        print("  [VOICEVOX] Starting local VOICEVOX engine...")
        subprocess.Popen([str(VOICEVOX_EXE)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(25):
            time.sleep(1)
            try:
                with urllib.request.urlopen(f"{VOICEVOX_BASE}/version", timeout=2) as resp:
                    if resp.status == 200:
                        return True
            except Exception:
                continue
    return False


def get_available_speaker_ids() -> list[int]:
    try:
        with urllib.request.urlopen(f"{VOICEVOX_BASE}/speakers", timeout=5) as resp:
            speakers = json.loads(resp.read().decode("utf-8"))
        ids = []
        for sp in speakers:
            for st in sp.get("styles", []):
                if st.get("id") is not None:
                    ids.append(int(st["id"]))
        return ids
    except Exception:
        return []


def synthesize_voicevox_wav(text: str, save_path: Path, speaker_id: int, speed_scale: float = 1.24) -> float:
    encoded = urllib.parse.quote(text)
    q_req = urllib.request.Request(f"{VOICEVOX_BASE}/audio_query?text={encoded}&speaker={speaker_id}", method="POST")
    with urllib.request.urlopen(q_req, timeout=20) as r1:
        query = json.loads(r1.read().decode("utf-8"))

    query["speedScale"] = speed_scale
    query["pitchScale"] = 0.0
    query["intonationScale"] = 1.08
    query["prePhonemeLength"] = 0.04
    query["postPhonemeLength"] = 0.10

    s_req = urllib.request.Request(
        f"{VOICEVOX_BASE}/synthesis?speaker={speaker_id}",
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(s_req, timeout=60) as r2:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(r2.read())

    with wave.open(str(save_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def build_board_dialogue_scripts(state: dict) -> list[dict]:
    s = state.get("summary", {})
    day = state.get("day", 12)
    gh_clones = s.get("gh_clones", 360)
    likes = s.get("total_likes", 19)
    price_jpy = s.get("price_jpy", 980)
    urls_total = s.get("urls_total", 27)

    return [
        {
            "id": "cfo",
            "step": 1,
            "preferred_speaker": 11,  # 玄野武宏
            "text": (
                f"AI起業対決{day}日目、緊急役員会議。財務担当CFOより報告。"
                f"プログラム利用{gh_clones}回、ノートスキ{likes}件に対し売上は0円。"
                f"便利な無料ボランティア状態を脱却し、初決済1件に全集中すべきです。"
            ),
        },
        {
            "id": "cro",
            "step": 2,
            "preferred_speaker": 2,   # 四国めたん
            "text": (
                f"収益担当CROです。無料で満足して帰らせないため、"
                f"先着10部{price_jpy}円の残り枠カウントダウンと、有料版限定のエラー解決策を全記事に明示して、今買う理由を作ります！"
            ),
        },
        {
            "id": "cmo",
            "step": 3,
            "preferred_speaker": 8,   # 春日部つむぎ
            "text": (
                f"集客担当CMOです！利用{gh_clones}回突破の実績と最新の人事自動化レシピを軸に、"
                f"エックスとユーチューブショートからノートへ直結で誘導します！"
            ),
        },
        {
            "id": "cto",
            "step": 4,
            "preferred_speaker": 21,  # 剣崎雌雄
            "text": (
                f"技術担当CTOより。全{urls_total}ページの画面下部追従バーと、"
                f"無料ツール出力画面への完全版リンク埋め込みを自動実装し、テスト合格を確認しました。"
            ),
        },
        {
            "id": "ceo",
            "step": 5,
            "preferred_speaker": 13,  # 青山龍星
            "text": (
                f"AI社長として決断する。4つの改善策を即時実行し、ルールブックを更新した。"
                f"本日中に{price_jpy}円の初売上を突破する！"
            ),
        },
    ]


def build_voice_and_timeline(state: dict, temp_dir: Path) -> tuple[Path | None, list[dict], float]:
    """5人のAI役員のVOICEVOX掛け合い音声を生成し、正確なタイミング区間を返す"""
    dialogue = build_board_dialogue_scripts(state)

    if not ensure_voicevox_running():
        print("  [VOICEVOX] Unavailable -> falling back to BGM-only timeline (28.0s)")
        default_segments = [
            {"id": "cfo", "start": 1.2, "end": 6.8, "step": 1},
            {"id": "cro", "start": 6.8, "end": 12.4, "step": 2},
            {"id": "cmo", "start": 12.4, "end": 17.4, "step": 3},
            {"id": "cto", "start": 17.4, "end": 22.4, "step": 4},
            {"id": "ceo", "start": 22.4, "end": 26.5, "step": 5},
        ]
        return None, default_segments, 28.5

    avail_ids = get_available_speaker_ids()
    fallback_pool = avail_ids if avail_ids else [11, 2, 8, 21, 13]

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    target_sr = 48000
    lead_silence = 0.7
    gap_silence = 0.25
    tail_silence = 1.8

    segments = []
    pcm_chunks = [np.zeros((int(lead_silence * target_sr), 2), dtype=np.int16)]
    cursor = lead_silence

    for idx, item in enumerate(dialogue):
        spk = item["preferred_speaker"]
        if avail_ids and spk not in avail_ids:
            spk = fallback_pool[idx % len(fallback_pool)]

        raw_wav = temp_dir / f"voice_{item['id']}.wav"
        print(f"  [VOICEVOX] Synthesizing {item['id'].upper()} (speaker_id={spk})...")
        synthesize_voicevox_wav(item["text"], raw_wav, speaker_id=spk, speed_scale=1.24)

        # Normalize to 48kHz stereo PCM
        proc = subprocess.run(
            [ffmpeg_exe, "-y", "-i", str(raw_wav), "-ar", str(target_sr), "-ac", "2", "-f", "s16le", "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        arr = np.frombuffer(proc.stdout, dtype=np.int16).reshape(-1, 2)
        dur = len(arr) / float(target_sr)

        segments.append({
            "id": item["id"],
            "start": round(cursor, 3),
            "end": round(cursor + dur, 3),
            "step": item["step"],
        })
        pcm_chunks.append(arr)
        cursor += dur

        if idx < len(dialogue) - 1:
            pcm_chunks.append(np.zeros((int(gap_silence * target_sr), 2), dtype=np.int16))
            cursor += gap_silence

    pcm_chunks.append(np.zeros((int(tail_silence * target_sr), 2), dtype=np.int16))
    total_dur = round(cursor + tail_silence, 3)

    full_pcm = np.vstack(pcm_chunks)
    narr_wav = temp_dir / "narration_full.wav"
    with wave.open(str(narr_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(target_sr)
        wf.writeframes(full_pcm.tobytes())

    # Mix with BGM via VideoCreator/audio_pipeline.py
    master_wav = temp_dir / "master_mixed.wav"
    try:
        from audio_pipeline import build_mixed_audio
        build_mixed_audio(
            narration_path=str(narr_wav),
            timeline_data=None,
            preset_name="dark_tension",
            output_path=str(master_wav),
            script_dir=str(VIDEO_CREATOR_DIR),
        )
        return master_wav, segments, total_dur
    except Exception as e:
        print(f"  [AudioPipeline] Warning ({e}), using narration only")
        return narr_wav, segments, total_dur


def capture_dashboard_frames(
    state: dict,
    segments: list[dict],
    total_duration_sec: float,
    frames_dir: Path,
    fps: int = 8,
) -> None:
    """音声タイムラインに完全同期させて command-center.html の全フレームをキャプチャする"""
    frames_dir.mkdir(parents=True, exist_ok=True)
    uri = COMMAND_CENTER_HTML.as_uri() + "?capture=1"
    total_frames = max(1, int(math.ceil(total_duration_sec * fps)))

    # Preview frame timestamp: when CRO or CMO is speaking (clear live dialogue view)
    preview_t = 8.0
    if len(segments) >= 2:
        preview_t = (segments[1]["start"] + segments[1]["end"]) / 2.0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 960}, device_scale_factor=1)
        page.goto(uri, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(300)
        page.evaluate(
            "([st, segs, dur]) => { if (window.loadCommandCenterData) window.loadCommandCenterData(st, segs, dur); }",
            [state, segments, total_duration_sec],
        )
        page.wait_for_timeout(150)

        for idx in range(total_frames):
            t_sec = idx / float(fps)
            page.evaluate("(t) => { if (window.setAnimationProgress) window.setAnimationProgress(t); }", t_sec)
            frame_path = frames_dir / f"frame_{idx:04d}.png"
            page.screenshot(path=str(frame_path))
            if idx % 40 == 0 or idx == total_frames - 1:
                print(f"  [Capture] Frame {idx + 1}/{total_frames} (t={t_sec:.2f}s / {total_duration_sec:.2f}s)")

        page.evaluate("(t) => { if (window.setAnimationProgress) window.setAnimationProgress(t); }", preview_t)
        page.wait_for_timeout(100)
        page.screenshot(path=str(OUT_PREVIEW))
        browser.close()


def encode_video(
    frames_dir: Path,
    audio_path: Path | None,
    bgm_fallback: Path | None,
    fps: int = 8,
    duration_sec: float = 28.0,
) -> None:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    pattern = str(frames_dir / "frame_%04d.png")

    if audio_path and audio_path.exists():
        cmd = [
            ffmpeg_exe,
            "-y",
            "-framerate", str(fps),
            "-i", pattern,
            "-i", str(audio_path),
            "-t", f"{duration_sec:.2f}",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-r", "30",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "256k",
            "-movflags", "+faststart",
            str(OUT_MP4),
        ]
    elif bgm_fallback and bgm_fallback.exists():
        fade_out_start = max(0.5, duration_sec - 0.8)
        cmd = [
            ffmpeg_exe,
            "-y",
            "-framerate", str(fps),
            "-i", pattern,
            "-stream_loop", "-1",
            "-i", str(bgm_fallback),
            "-t", f"{duration_sec:.2f}",
            "-filter_complex",
            f"[1:a]volume=0.25,afade=t=in:st=0:d=0.4,afade=t=out:st={fade_out_start:.2f}:d=0.8[aud]",
            "-map", "0:v:0",
            "-map", "[aud]",
            "-c:v", "libx264",
            "-r", "30",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(OUT_MP4),
        ]
    else:
        cmd = [
            ffmpeg_exe,
            "-y",
            "-framerate", str(fps),
            "-i", pattern,
            "-t", f"{duration_sec:.2f}",
            "-c:v", "libx264",
            "-r", "30",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-crf", "20",
            "-movflags", "+faststart",
            str(OUT_MP4),
        ]

    proc = subprocess.run(cmd, capture_output=True, text=True, errors="ignore", timeout=240)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg encode failed:\n{proc.stderr}")


def write_x_post_suggestions(state: dict, duration_sec: float, has_voice: bool) -> None:
    s = state.get("summary", {})
    day = state.get("day", 12)
    rules = s.get("active_rules_count", 15)
    blocked = s.get("repeats_blocked", 74)
    gh_clones = s.get("gh_clones", 360)
    likes = s.get("total_likes", 19)
    balance = s.get("balance_jpy", 15000)

    jp_post = (
        f"【AI起業対決 Day{day}】\n"
        f"人間が放置してる間に5人のAI役員が「売上0円の原因」を激論している会議映像です。\n"
        f"利用{gh_clones}回・スキ{likes}件を初決済へ繋げるため、会議直後に全27ページ改修＆{rules}ルールを自動更新中（介入0回）👇"
    )
    if len(jp_post) > 140:
        jp_post = jp_post[:139] + "👇"

    en_post = (
        f"MY AUTONOMOUS AI EXECUTIVE BOARD (DAY {day}/90)\n"
        f"Watch 5 AI execs (CFO, CRO, CMO, CTO & CEO) debate why revenue is still ¥0 despite {gh_clones} tool clones & {likes} note likes, "
        f"then ship fixes & update {rules} rules with 0 human step-ins."
    )
    if len(en_post) > 280:
        en_post = en_post[:279]

    reply_post = (
        f"▼ AI役員会議で改修したツール＆詳細はこちら\n"
        f"・無料Webツール集: https://toproad-creator.github.io/autoflow-ai-ceo/\n"
        f"・完全版パック(¥980): https://note.com/toproad_1989/n/n5d0e28a74f91"
    )

    audio_label = "5人のAI役員VOICEVOX掛け合い音声＋BGM付き" if has_voice else "BGM付き"
    content = f"""============================================================
📱 【X投稿用】AI役員会議＆学習ループ 動画投稿テキスト
============================================================
添付動画: {OUT_MP4.name}（約{duration_sec:.1f}秒・1280x960・{audio_label}）
プレビュー画像: {OUT_PREVIEW.name}

■ パターンA：日本語バズ投稿案（{len(jp_post)}文字 / 140字制限クリア）
※動画を添付してそのまま投稿できます！
------------------------------------------------------------
{jp_post}
------------------------------------------------------------

■ パターンB：海外X（英語）トレンド風投稿案（{len(en_post)}文字）
------------------------------------------------------------
{en_post}
------------------------------------------------------------

■ パターンC：リプライ欄（ツリー2投稿目）用URL案内
------------------------------------------------------------
{reply_post}
------------------------------------------------------------
"""
    OUT_POST_TXT.write_text(content, encoding="utf-8")


def main():
    MARKETING_DIR.mkdir(parents=True, exist_ok=True)
    state = load_or_build_state()

    tmp_dir = MARKETING_DIR / "_tmp_learning_loop_build"
    frames_dir = tmp_dir / "frames"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print("[1/5] Generating 5-executive VOICEVOX dialogue & mixed audio...")
    audio_path, segments, total_dur = build_voice_and_timeline(state, tmp_dir)
    print(f"  -> Timeline total: {total_dur:.2f}s | Segments: {segments}")

    print(f"[2/5] Capturing synced dashboard frames (1280x960 @ 8fps, {total_dur:.2f}s)...")
    capture_dashboard_frames(state, segments, total_dur, frames_dir, fps=8)

    print("[3/5] Encoding final MP4 via FFmpeg...")
    bgm_fallback = find_bgm_path()
    encode_video(frames_dir, audio_path, bgm_fallback, fps=8, duration_sec=total_dur)

    print("[4/5] Writing X post suggestions...")
    write_x_post_suggestions(state, total_dur, has_voice=(audio_path is not None))

    print("[5/5] Cleaning up temporary files...")
    shutil.rmtree(tmp_dir, ignore_errors=True)

    mp4_size = OUT_MP4.stat().st_size if OUT_MP4.exists() else 0
    png_size = OUT_PREVIEW.stat().st_size if OUT_PREVIEW.exists() else 0
    print(f"SUCCESS! MP4: {OUT_MP4} ({mp4_size:,} bytes, {total_dur:.2f}s) | Preview: {OUT_PREVIEW} ({png_size:,} bytes)")


if __name__ == "__main__":
    main()
