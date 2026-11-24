import base64
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[2]
AI_CEO_DIR = ROOT_DIR / "ai_ceo_system"
VIDEO_CREATOR_DIR = ROOT_DIR / "VideoCreator"
UPLOADED_JSON = AI_CEO_DIR / "shorts_videos" / "youtube_uploaded_urls.json"

load_dotenv(ROOT_DIR / ".env")

sys.path.insert(0, str(AI_CEO_DIR / "agents"))
sys.path.insert(0, str(VIDEO_CREATOR_DIR))

PAID_NOTE_FRAGMENT = "【先着10部"
LEGACY_SHORT_CLICHES = (
    "スマホ画面での購入ボタンが目立っていない",
    "スマホの購入導線が弱い",
    "全27ページの画面下部に追従バー",
    "オーケストレーターが全自動で回しています",
    "自ら5人のAI役員会議を開いて全サイトを大改造した件",
    "全27ページの画面下部に\n【先着10部",
    "コメント欄のリンク",
    "概要欄のリンク",
    "リンクから詳細をチェック",
    "リンクの先にあります",
)

CONCEPT_ROTATION = (
    {
        "id": "timesaving_demo",
        "name": "時短ノウハウ実演回",
        "hook_angle": "視聴者の実務時短ベネフィット最優先：『毎月何十時間消えていた作業がコピペ30秒で終わる最新レシピ』の実演型フック",
    },
    {
        "id": "zero_revenue_drama",
        "name": "リアル経営ドキュメンタリー回",
        "hook_angle": "AI社長の泥臭い挑戦ドラマ：『ツール利用やnoteスキは伸びているのに売上¥0の壁』を突破するため本日のAI役員会議が決断した逆転の一手",
    },
    {
        "id": "manual_loss_comparison",
        "name": "手作業損失ビフォーアフター比較回",
        "hook_angle": "損得インパクト重視：『今のまま手作業を続けると年間どれほど損をするか vs 本日公開の無料AIレシピ導入後』の比較フック",
    },
)

SHORT_COMMON_CSS = """
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
  .top-title { font-size: 24px; font-weight: 900; color: #e2e8f0; white-space: nowrap; }
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
  .win-body { padding: 28px; font-size: 27px; line-height: 1.6; }
  .headline-big { font-size: 38px; font-weight: 900; line-height: 1.38; margin-bottom: 20px; }
  .bullet-item { background: rgba(30, 41, 59, 0.72); border-left: 5px solid #38bdf8; padding: 14px 18px; border-radius: 10px; margin-bottom: 14px; font-size: 26px; font-weight: 700; color: #f1f5f9; }
  .callout-box { background: #161b22; border: 2px solid #38bdf8; border-radius: 14px; padding: 18px 22px; margin-top: 12px; font-size: 25px; line-height: 1.55; color: #bae6fd; }
  .thumb-frame { width: 100%; max-height: 360px; object-fit: cover; border-radius: 14px; border: 2px solid #334155; margin-bottom: 16px; }
"""


def _img_to_data_uri(path: Path) -> str:
    if not path or not path.exists():
        return ""
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _has_unbalanced_brackets(text: str) -> bool:
    for op, cl in [("「", "」"), ("『", "』"), ("（", "）"), ("【", "】"), ("(", ")")]:
        if (text or "").count(op) != (text or "").count(cl):
            return True
    return False


class DailyShortPipelineAgent:
    """毎日のAI役員会議・最新集客スコア・新規公開無料note記事を題材に、
    視聴者維持率＆クリック率を最大化する完全ユニーク台本（Gemini生成＋非重複検査＋検証済みフォールバック）と
    YouTubeショート動画（1080x1920・VOICEVOX音声＋BGM）を生成・公開するエージェント。
    """

    @staticmethod
    def _pick_concept(day: int) -> dict:
        return CONCEPT_ROTATION[day % len(CONCEPT_ROTATION)]

    @staticmethod
    def _clean_free_niche_title(title: str, top1_short: str = "業務自動化") -> str:
        raw = (title or "").strip()
        if not raw or PAID_NOTE_FRAGMENT in raw or raw == "AutoFlow Pro":
            return top1_short
        cleaned = re.sub(r"【[^】]*】", "", raw).strip()
        for sep in ("をAIとGASで", "をChatGPTやClaudeで", "をAIで", "の作り方", "完全ガイド"):
            if sep in cleaned:
                cleaned = cleaned.split(sep)[0].strip()
        cleaned = cleaned.strip("「」『』（）【】・：: ")
        if len(cleaned) > 22:
            cut = cleaned[:22]
            for delim in ("＆", "・", "、", " "):
                pos = cut.rfind(delim)
                if pos >= 8:
                    cut = cut[:pos]
                    break
            cleaned = cut.strip("＆・、： ")
        while len(cleaned) > 4 and cleaned[-1] in ("を", "が", "に", "で", "と", "の", "へ", "や", "は"):
            cleaned = cleaned[:-1].rstrip("＆・、： ")
        return cleaned or top1_short

    @staticmethod
    def _load_recent_short_lines(day: int) -> tuple[set[str], list[str]]:
        prev_narrations: set[str] = set()
        recent_titles: list[str] = []
        for d in range(max(1, day - 3), day):
            sp = AI_CEO_DIR / "shorts_videos" / f"day{d}" / f"ai_ceo_day{d}_script.json"
            if not sp.exists():
                continue
            try:
                data = json.loads(sp.read_text(encoding="utf-8"))
                vt = (data.get("video_title") or "").strip()
                if vt:
                    recent_titles.append(vt)
                for sc in data.get("scenes", []):
                    nr = (sc.get("narration") or "").strip()
                    if nr:
                        prev_narrations.add(nr)
            except Exception:
                continue
        if UPLOADED_JSON.exists():
            try:
                for it in json.loads(UPLOADED_JSON.read_text(encoding="utf-8")):
                    if it.get("day", 0) != day and it.get("title"):
                        if it["title"] not in recent_titles:
                            recent_titles.append(it["title"])
            except Exception:
                pass
        return prev_narrations, recent_titles

    def _load_day_context(self, day: int) -> dict:
        data_dir = AI_CEO_DIR / "data"
        meeting = {}
        m_path = data_dir / "board_meetings" / f"day{day}_meeting.json"
        if m_path.exists():
            try:
                meeting = json.loads(m_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        evo = {}
        e_path = data_dir / "company_evolution_state.json"
        if e_path.exists():
            try:
                evo = json.loads(e_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        prev_narrations, recent_titles = self._load_recent_short_lines(day)
        top_winners = evo.get("selection_and_focus", {}).get("winners_top3") or []
        top1_title = top_winners[0].get("title", "補助金申請・事業計画") if top_winners else "補助金申請・事業計画"
        top1_short = top1_title.split("・")[0].split("の")[0][:14]
        hours_saved = top_winners[0].get("avg_hours_saved_monthly", 42) if top_winners else 42
        staff_count = evo.get("ai_team_roster", {}).get("total_headcount", 9)
        agenda = (meeting.get("agenda") or f"需要1位「{top1_short}」強化と初売上達成").strip()
        goal = (meeting.get("ceo_final_decision", {}).get("primary_goal") or "先着10部¥980の初決済突破").strip()
        return {
            "top1_short": top1_short,
            "top1_title": top1_title,
            "hours_saved": hours_saved,
            "staff_count": staff_count,
            "agenda": agenda,
            "goal": goal,
            "prev_narrations": prev_narrations,
            "recent_titles": recent_titles,
        }

    @classmethod
    def validate_script_payload(
        cls,
        payload: dict,
        prev_narrations: set[str] | None = None,
        prev_titles: set[str] | None = None,
        require_cards: bool = False,
    ) -> tuple[bool, list[str]]:
        """実際の script.json データを検査し、有料タイトル混入・途切れ・旧固定文・前日使い回しを0件に保証する。"""
        reasons: list[str] = []
        if not isinstance(payload, dict):
            return False, ["payload_not_dict"]

        vt = (payload.get("video_title") or "").strip()
        if not vt:
            reasons.append("empty_video_title")
        if "#Shorts" not in vt:
            reasons.append("missing_shorts_hashtag")
        if PAID_NOTE_FRAGMENT in vt or "補」" in vt:
            reasons.append("paid_note_fragment_leak")
        if _has_unbalanced_brackets(vt):
            reasons.append("unbalanced_brackets_in_title")
        if prev_titles and vt in prev_titles:
            reasons.append("duplicate_video_title_with_previous_day")

        scenes = payload.get("scenes") or []
        if len(scenes) != 5:
            reasons.append(f"invalid_scene_count:{len(scenes)}")

        seen_day_narr: set[str] = set()
        for idx, sc in enumerate(scenes, start=1):
            nr = (sc.get("narration") or "").strip()
            tx = (sc.get("text") or "").strip()
            if len(nr) < 18:
                reasons.append(f"scene_{idx}_narration_too_short")
            if len(tx) < 8:
                reasons.append(f"scene_{idx}_text_too_short")
            if nr in seen_day_narr:
                reasons.append(f"scene_{idx}_duplicate_within_day")
            seen_day_narr.add(nr)
            if prev_narrations and nr in prev_narrations:
                reasons.append(f"scene_{idx}_reused_from_previous_day")

            combined = f"{vt}\n{nr}\n{tx}"
            card = sc.get("card")
            if require_cards and not (isinstance(card, dict) and card.get("headline") and card.get("bullets")):
                reasons.append(f"scene_{idx}_missing_card")
            if isinstance(card, dict):
                combined += f"\n{card.get('headline', '')}\n{card.get('highlight_body', '')}"
            for bad in LEGACY_SHORT_CLICHES:
                if bad in combined:
                    reasons.append(f"scene_{idx}_legacy_cliche:{bad[:14]}")

        return len(reasons) == 0, reasons

    def _generate_llm_short_script(
        self,
        day: int,
        concept: dict,
        clean_niche_title: str,
        day_ctx: dict,
        metrics_ctx: dict,
    ) -> dict | None:
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not gemini_key:
            return None

        prev_titles_sample = " / ".join(day_ctx["recent_titles"][:3]) or "なし"
        prev_narr_sample = "\n".join(f"- {ln}" for ln in sorted(day_ctx["prev_narrations"])[:6]) or "- なし"

        prompt = f"""あなたは再生数とチャンネル登録率を最大化するYouTubeショート専門の放送作家兼CMOです。
以下の実測データをもとに、視聴者が最初の2秒でスクロールを止め、最後まで見てコメント・リンククリックしたくなる Day {day} 専用の完全オリジナルショート台本（5シーン構成）を作成してください。

【本日の企画コンセプト（必ずこの切り口で全体を構成すること）】
- コンセプト名: {concept['name']}
- 演出方針: {concept['hook_angle']}

【本日の実測データ】
- Day番号: Day {day} / 残高: ¥{metrics_ctx['balance']:,} / 売上: ¥0
- 本日の最新無料公開レシピ: 『{clean_niche_title}』（AI+GASで月{day_ctx['hours_saved']}時間削減見込み）
- 今いちばん需要が高いテーマ1位: 『{day_ctx['top1_short']}』
- 本日のAI役員会議（{day_ctx['staff_count']}名体制）議題: {day_ctx['agenda'][:60]}
- 最優先目標: {day_ctx['goal'][:50]}
- note公開記事: {metrics_ctx['total_notes']}本（累計スキ{metrics_ctx['total_likes']}件）
- 限定有料パック価格: 単品¥500特化キット / 全50選パック 先着10部 ¥{metrics_ctx['price_jpy']:,}

【絶対厳守ルール】
1. `video_title` は82文字以内・括弧バランス完璧・末尾に必ず ` #Shorts` を付け、視聴者の好奇心を引くこと。先着10部などの途切れ表記や、過去動画と同じテンプレは厳禁。
2. YouTubeショートの仕様上、概要欄やコメント欄のURLは押せないため、「コメント欄のリンク」「概要欄のリンク」「リンクから詳細をチェック」という表現は絶対に使わないこと。代わりに誘導先を示すときは必ず「チャンネル画面のリンク」または「noteで『AutoFlow』と検索」と案内すること。
3. 5シーンすべての `narration`・`text`・画面表示カード（`card`）を本日固有の内容として新しく書き下ろすこと。定型文の使い回しは厳禁。
4. 以下の過去回タイトルおよびセリフと一字一句同じ文は絶対に使わないこと：
過去タイトル: {prev_titles_sample}
過去セリフ抜粋:
{prev_narr_sample}
5. 各シーンの `narration` は話し言葉で40〜68文字（約5〜7秒で読み切れるテンポ）。Scene 1は衝撃のフック、Scene 2は具体データ/損失、Scene 3は無料記事『{clean_niche_title}』実演（チャンネルプロフィールのnoteへ誘導）、Scene 4は裏側のAI改善打ち手、Scene 5は2択コメント誘導CTA（[A: ...] [B: ...]）＋プロフィール検索誘導。
5. 出力は次のスキーマの純粋なJSONのみ（説明文不要）を返すこと：
{{
  "video_title": "【Day{day}】... #Shorts",
  "pinned_comment": "視聴者がAかBで思わず投票したくなる固定コメント（120文字以内）",
  "scenes": [
    {{
      "scene": 1,
      "narration": "...",
      "text": "字幕1行目\\n字幕2行目\\n字幕3行目",
      "card": {{
        "card_title": "ウィンドウ見出し（22文字以内）",
        "headline": "画面内の太字ヘッドライン（28文字以内）",
        "bullets": ["データ箇条書き1", "データ箇条書き2"],
        "highlight_label": "注目ポイント見出し",
        "highlight_body": "注目ポイント本文（45文字以内）"
      }}
    }}
  ]
}}"""

        prev_titles_set = set(day_ctx["recent_titles"])
        for model_name in ("gemini-3-flash-preview", "gemma-4-31b-it", "gemini-3.1-flash-lite"):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                body = json.dumps({
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.65},
                }).encode("utf-8")
                req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=28) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                parts = payload["candidates"][0]["content"]["parts"]
                content = "".join(p.get("text", "") for p in parts if not p.get("thought")) or parts[-1].get("text", "")
                match = re.search(r"\{.*\}", content, re.S)
                if not match:
                    continue
                parsed = json.loads(match.group(0))
                vt = (parsed.get("video_title") or "").strip()
                if vt and "#Shorts" not in vt:
                    parsed["video_title"] = f"{vt} #Shorts"
                for sc in parsed.get("scenes", []):
                    if isinstance(sc.get("text"), str):
                        sc["text"] = sc["text"].replace("\\n", "\n").strip()
                ok, _ = self.validate_script_payload(
                    parsed,
                    prev_narrations=day_ctx["prev_narrations"],
                    prev_titles=prev_titles_set,
                    require_cards=True,
                )
                if ok:
                    return parsed
            except Exception:
                continue
        return None

    def _build_fallback_script(
        self,
        day: int,
        concept: dict,
        clean_niche_title: str,
        day_ctx: dict,
        metrics_ctx: dict,
    ) -> dict:
        """Gemini不在時やAPI失敗時でも、企画コンセプト3パターン×Day番号連動で絶対に前日と被らない台本を生成する。"""
        top1 = day_ctx["top1_short"]
        hrs = day_ctx["hours_saved"]
        agenda_short = day_ctx["agenda"][:26]
        gh_clones = metrics_ctx["gh_clones"]
        gh_uniques = metrics_ctx["gh_uniques"]
        total_notes = metrics_ctx["total_notes"]
        total_likes = metrics_ctx["total_likes"]
        price_jpy = metrics_ctx["price_jpy"]
        cid = concept["id"]

        if cid == "timesaving_demo":
            vt = f"【Day{day}】{clean_niche_title}をAIとGASでコピペ自動化する最新時短レシピ公開 #Shorts"
            pinned = f"Day{day}の無料テンプレート『{clean_niche_title}』、あなたの職場でも使えそうですか？ [A: 今すぐ試したい] [B: 他業務も自動化したい] コメントで教えてください！"
            scenes = [
                {
                    "scene": 1,
                    "narration": f"Day{day}の今日は、毎回手作業だと月{hrs}時間も奪われる「{clean_niche_title}」をAIで30秒化する実演です！",
                    "text": f"【Day {day} 時短実演】\n月{hrs}時間消える作業を\nコピペAIで30秒化！",
                    "card": {
                        "card_title": f"DAY {day} 時短デモ：対象業務",
                        "headline": f"『{clean_niche_title}』を完全自動化",
                        "bullets": [f"手作業の負担：毎月約{hrs}時間を丸ごと圧縮", f"無料テンプレ公開：計{total_notes}本目を追加済み"],
                        "highlight_label": "本日のターゲット需要",
                        "highlight_body": f"現在人気1位『{top1}』と連動する即戦力GASコードを公開",
                    },
                },
                {
                    "scene": 2,
                    "narration": f"市場データ分析でも「{top1}」と並ぶ需要トップ領域で、すでにWebツール利用は累計{gh_clones}回を突破しました。",
                    "text": f"利用{gh_clones}回を突破！\n需要TOP『{top1}』と\n直結する現場ニーズ",
                    "card": {
                        "card_title": "LIVE DEMAND ANALYTICS",
                        "headline": f"利用者{gh_uniques}名が選んだ注目課題",
                        "bullets": [f"GitHubツール利用：累計{gh_clones}回達成", f"note累計スキ数：{total_likes}件まで拡大中"],
                        "highlight_label": "実務インパクト",
                        "highlight_body": f"入力バラつき・返信遅延をGeminiプロンプトとGASが同時に解消",
                    },
                },
                {
                    "scene": 3,
                    "narration": f"本日公開した{total_notes}本目の無料note記事では、すぐコピペできる実行手順と設計プロンプトをそのまま開放中です！",
                    "text": f"note{total_notes}本目で無料公開！\n「{clean_niche_title[:16]}」\nコピペ用GAS付き",
                    "card": {
                        "card_title": f"FREE NOTE #{total_notes} RELEASED",
                        "headline": f"{clean_niche_title} 実践ガイド",
                        "bullets": ["そのまま貼り付けて動くプロンプト全文", "現場で迷わないエラー回避のチェック表"],
                        "highlight_label": "無料レシピ入手方法",
                        "highlight_body": f"チャンネルトップのURLか、noteで「AutoFlow」と検索（{total_notes}本目）",
                    },
                },
                {
                    "scene": 4,
                    "narration": f"さらにDay{day}の会議議題「{agenda_short}」を受け、無料ツール利用直後のおすすめ導線も最新化済みです。",
                    "text": f"Day {day} 会議アップデート\n無料ツール終了後に\n最適レシピを即提案！",
                    "card": {
                        "card_title": f"DAY {day} SITE ENGINE UPDATE",
                        "headline": "体験後レコメンドを本日版へ同期",
                        "bullets": [f"会議テーマ：{agenda_short}", f"対応状況：需要1位『{top1}』中心へ自動切替"],
                        "highlight_label": "仕組みの裏側",
                        "highlight_body": "読者が欲しいテンプレートへ迷わず辿り着ける専用導線を毎日最適化",
                    },
                },
                {
                    "scene": 5,
                    "narration": f"50本まとめた限定{price_jpy}円パックも含め、Day{day}の自動化ツールは試したくなりましたか？AかBで投票してください！",
                    "text": f"時短レシピ50選（限定¥{price_jpy}）\n[A: 無料記事から試す！]\n[B: 業務別の要望を送る]",
                    "card": {
                        "card_title": f"AUTOFLOW PRO / DAY {day} POLL",
                        "headline": f"厳選レシピ50本パック 先着10部 ¥{price_jpy}",
                        "bullets": [f"無料記事{total_notes}本公開 / スキ{total_likes}件達成", f"現在の実験残高：¥{metrics_ctx['balance']:,}"],
                        "highlight_label": "コメント欄で2択投票！",
                        "highlight_body": "[A: 今すぐ無料で試す] / [B: この業務も自動化してほしい]",
                    },
                },
            ]
        elif cid == "zero_revenue_drama":
            vt = f"【Day{day}】利用{gh_clones}回でも売上0円…AI役員が「{clean_niche_title[:14]}」で逆転を狙う会議の裏側 #Shorts"
            pinned = f"Day{day}現在、利用{gh_clones}回・記事{total_notes}本でも売上¥0。今回の『{clean_niche_title}』投入で初決済は出ると思いますか？ [A: そろそろ1部売れる] [B: まだ壁が厚い]"
            scenes = [
                {
                    "scene": 1,
                    "narration": f"Day{day}、利用{gh_clones}回・スキ{total_likes}件まで増えたのに売上はまだ0円。今日AI社長は「{agenda_short}」へ舵を切りました！",
                    "text": f"AI社長のリアル記録 Day {day}\n利用{gh_clones}回でも売上¥0\n逆転の新施策を発動！",
                    "card": {
                        "card_title": f"CRISIS LOG // DAY {day}",
                        "headline": f"累計売上¥0を破るDay{day}の決断",
                        "bullets": [f"プログラム利用：{gh_clones}回（{gh_uniques}名）", f"本日の重要議題：{agenda_short}"],
                        "highlight_label": "危機感ポイント",
                        "highlight_body": f"アクセスは着実に増加中。あとは『{top1}』から有料版への納得感",
                    },
                },
                {
                    "scene": 2,
                    "narration": f"AI役員{day_ctx['staff_count']}名が市場を分析した結果、今もっとも切実な需要1位は「{top1}」だと確定しました。",
                    "text": f"AI役員{day_ctx['staff_count']}名が分析！\nいま本当に求められている\n需要1位『{top1}』",
                    "card": {
                        "card_title": "EXECUTIVE BOARD ANALYSIS",
                        "headline": f"読者反応が集中した『{top1}』",
                        "bullets": [f"noteスキ獲得数：累計{total_likes}件到達", f"期待時短効果：月{hrs}時間クラスの課題"],
                        "highlight_label": "本日の路線修正",
                        "highlight_body": "抽象的な機能紹介をやめ、現場で今日すぐ使える具体コードへ集中投資",
                    },
                },
                {
                    "scene": 3,
                    "narration": f"その突破口として本日公開されたのが、{total_notes}本目の無料note「{clean_niche_title}」です！",
                    "text": f"突破口の無料記事{total_notes}本目\n「{clean_niche_title[:16]}」\n本日公開完了！",
                    "card": {
                        "card_title": f"DAY {day} NEW FREE ARTICLE",
                        "headline": f"『{clean_niche_title}』コピペ実践記事",
                        "bullets": ["ゼロから設定できる導入手順を全掲載", "実際の現場データで即テスト可能"],
                        "highlight_label": "無料価値で信頼獲得",
                        "highlight_body": "まず無料で成果を実感してもらい、50本完全パックへ繋ぐ正攻法",
                    },
                },
                {
                    "scene": 4,
                    "narration": f"同時にX投稿文から有料記事の冒頭文面まで自動検証し、誤字や不自然な表現をすべて自動で取り除きました。",
                    "text": f"品質ゲート全自動監査\nX投稿も有料ページ冒頭も\nAIが違和感ゼロへ修正！",
                    "card": {
                        "card_title": "AUTO REMEDIATION GATE",
                        "headline": "公開前の自動品質テストを通過",
                        "bullets": [f"対象記事：計{total_notes}本の最新データを同期", f"価格訴求：先着10部¥{price_jpy}で統一検証済み"],
                        "highlight_label": "今日の改善ポイント",
                        "highlight_body": "無料から有料への説明文を『数値根拠つき・不自然な途切れゼロ』に刷新",
                    },
                },
                {
                    "scene": 5,
                    "narration": f"Day{day}の本気アップデートで、先着10部{price_jpy}円の記念すべき初売上は届くでしょうか？コメントで予想してください！",
                    "text": f"Day {day} 初売上チャレンジ！\n[A: 今週こそ初売上達成！]\n[B: まだ改善が必要かも]",
                    "card": {
                        "card_title": f"DAY {day} CHALLENGE STATUS",
                        "headline": f"限定先着10部 ¥{price_jpy} 初決済待ち",
                        "bullets": [f"利用{gh_clones}回・スキ{total_likes}件・公開{total_notes}本", f"運用残高：¥{metrics_ctx['balance']:,}"],
                        "highlight_label": "あなたの予想を募集中🔥",
                        "highlight_body": "[A: そろそろ売れる！] か [B: ここを直すべき] をコメントへ！",
                    },
                },
            ]
        else:
            vt = f"【Day{day}】手作業で月{hrs}時間損してる人へ！『{clean_niche_title[:15]}』をAI化する時短比較 #Shorts"
            pinned = f"手作業で消耗している業務、1つ減らすならどれを選びますか？ [A: {clean_niche_title[:14]}] [B: {top1[:14]}] チャンネル欄のURLから無料レシピも見れます！"
            scenes = [
                {
                    "scene": 1,
                    "narration": f"Day{day}の警告です。その「{clean_niche_title}」、まだ手作業のままだと毎月{hrs}時間以上をムダにしているかもしれません！",
                    "text": f"【Day {day} 損失比較】\n手作業のまま放置すると\n毎月{hrs}時間のロス！？",
                    "card": {
                        "card_title": f"TIME LOSS AUDIT // DAY {day}",
                        "headline": f"『{clean_niche_title}』の手作業コスト",
                        "bullets": [f"Before：毎月{hrs}時間の手入力・確認地獄", "After：AI+GASテンプレ導入でほぼ自動完了"],
                        "highlight_label": "気づきにくい機会損失",
                        "highlight_body": "1回15分の作業でも月間・年間で見ると人件費数万円分の差に拡大",
                    },
                },
                {
                    "scene": 2,
                    "narration": f"実際、同じ悩みを解決する自動化ツールの利用は{gh_clones}回に達し、需要1位は「{top1}」となっています。",
                    "text": f"悩む人が急増中！\nツール利用{gh_clones}回\n注目1位『{top1}』",
                    "card": {
                        "card_title": "REAL USER TREND DATA",
                        "headline": f"現場ユーザー{gh_uniques}名の利用傾向",
                        "bullets": [f"累計アクセス利用：{gh_clones}回を記録", f"公開レシピ記事：全{total_notes}本 / スキ{total_likes}件"],
                        "highlight_label": "なぜ今自動化されるのか",
                        "highlight_body": f"専門知識ゼロでもGASコピペだけで『{top1}』周りが即省力化できるため",
                    },
                },
                {
                    "scene": 3,
                    "narration": f"本日新しく公開した「{clean_niche_title}」の記事なら、ビフォーを覆すコピペ用プロンプトと手順がすぐ使えます。",
                    "text": f"本日公開の無料レシピ\n「{clean_niche_title[:16]}」\n今すぐ使える実践手順",
                    "card": {
                        "card_title": f"DAY {day} SOLUTION TEMPLATE",
                        "headline": f"{clean_niche_title} 自動化セット",
                        "bullets": ["コピーして即動くプロンプト設計", "初心者でも詰まらない設定ガイド付き"],
                        "highlight_label": "無料公開の理由",
                        "highlight_body": "まずは1つ手作業を消す気持ちよさを無料で体験してもらうための特別公開",
                    },
                },
                {
                    "scene": 4,
                    "narration": f"AI役員会議でも「{agenda_short}」を掲げ、無料ツールを使うだけで次の最適自動化が見つかる構造へ整えました。",
                    "text": f"AI会議 Day {day} 決定事項\n「{agenda_short[:18]}」\n導入ステップを極限まで短縮！",
                    "card": {
                        "card_title": f"WORKFLOW IMPROVEMENT // DAY {day}",
                        "headline": "迷わず実践できる3ステップ導線",
                        "bullets": ["① Webシミュレーターで効果を試算", "② 無料note記事からコピペ導入"],
                        "highlight_label": "今後の拡張方針",
                        "highlight_body": f"要望の多い『{top1}』領域を軸に50本パック（先着¥{price_jpy}）も強化継続",
                    },
                },
                {
                    "scene": 5,
                    "narration": f"あなたの職場で一番先に手放したい手作業はどちらですか？AかBをコメント欄で教えてくださいね！",
                    "text": f"どれから手放したい？\n[A: {clean_niche_title[:14]}]\n[B: {top1[:14]}]",
                    "card": {
                        "card_title": f"DAY {day} BEFORE / AFTER POLL",
                        "headline": f"本格50本パックも限定¥{price_jpy}で公開中",
                        "bullets": [f"無料記事{total_notes}本公開済み / スキ{total_likes}件", f"チャンネル名横のリンクから即利用OK"],
                        "highlight_label": "チャンネル画面のリンク／note検索で取得👇",
                        "highlight_body": f"[A: {clean_niche_title[:16]}] or [B: {top1[:16]}]",
                    },
                },
            ]

        return {
            "video_title": vt,
            "pinned_comment": pinned,
            "scenes": scenes,
        }

    def _render_scene_html(
        self,
        day: int,
        scene_num: int,
        concept: dict,
        card: dict,
        metrics_ctx: dict,
        free_uri: str,
        paid_sale_uri: str,
    ) -> str:
        top_title = html.escape(f"{concept['name']} // DAY {day}")
        card_title = html.escape(str(card.get("card_title", f"DAY {day} SCENE {scene_num}")))
        headline = html.escape(str(card.get("headline", "")))
        bullets = [html.escape(str(b)) for b in (card.get("bullets") or [])[:3]]
        bullets_html = "".join(f'<div class="bullet-item">▶ {b}</div>' for b in bullets)
        h_label = html.escape(str(card.get("highlight_label", "ポイント")))
        h_body = html.escape(str(card.get("highlight_body", "")))

        img_html = ""
        if scene_num == 3 and free_uri:
            img_html = f'<img class="thumb-frame" src="{free_uri}" alt="free-note-thumb"/>'
        elif scene_num == 5 and paid_sale_uri:
            img_html = f'<img class="thumb-frame" src="{paid_sale_uri}" alt="paid-pack-thumb"/>'

        accent = ("#f43f5e", "#38bdf8", "#10b981", "#a78bfa", "#facc15")[scene_num - 1]
        return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{SHORT_COMMON_CSS}</style></head><body>
          <div class="top-bar"><span class="badge-day">DAY {day} / 90</span><span class="top-title">{top_title}</span><span class="wallet-pill">残高 ¥{metrics_ctx['balance']:,}</span></div>
          <div class="content-area">
            <div class="terminal-window" style="border-color:{accent};">
              <div class="win-header"><span class="dot dot-r"></span><span class="dot dot-y"></span><span class="dot dot-g"></span><span class="win-title">{card_title}</span></div>
              <div class="win-body">
                {img_html}
                <div class="headline-big" style="color:{accent};">{headline}</div>
                {bullets_html}
                <div class="callout-box" style="border-color:{accent};">
                  <b>💡 {h_label}：</b><br>{h_body}
                </div>
              </div>
            </div>
          </div></body></html>"""

    def get_existing_uploaded_url(self, day: int) -> str:
        if UPLOADED_JSON.exists():
            try:
                items = json.loads(UPLOADED_JSON.read_text(encoding="utf-8"))
                for it in items:
                    if it.get("day") == day and it.get("status") in ("uploaded_public", "uploaded_private") and it.get("url"):
                        return it["url"]
            except Exception:
                pass
        return ""

    def generate_script_and_scenes(
        self,
        day: int,
        balance: int = 15000,
        price_jpy: int = 980,
        total_notes: int = 15,
        total_likes: int = 44,
        gh_clones: int = 407,
        gh_uniques: int = 134,
        latest_note_title: str = "",
        latest_note_thumb_path: str = "",
        force: bool = False,
    ) -> dict:
        """Day固有のコンセプトで5シーン台本＆映像用HTMLを生成し、実物JSON（ai_ceo_day{day}_script.json）を検証保存する。"""
        out_dir = AI_CEO_DIR / "shorts_videos" / f"day{day}"
        out_dir.mkdir(parents=True, exist_ok=True)
        script_path = out_dir / f"ai_ceo_day{day}_script.json"

        day_ctx = self._load_day_context(day)
        concept = self._pick_concept(day)
        clean_niche_title = self._clean_free_niche_title(latest_note_title, day_ctx["top1_short"])
        metrics_ctx = {
            "balance": balance,
            "price_jpy": price_jpy,
            "total_notes": total_notes,
            "total_likes": total_likes,
            "gh_clones": gh_clones,
            "gh_uniques": gh_uniques,
        }

        thumb_dir = AI_CEO_DIR / "data" / "thumbnails"
        paid_sale_uri = _img_to_data_uri(thumb_dir / "thumb_paid_autoflow_pro_50.png")
        free_thumb_file = Path(latest_note_thumb_path) if latest_note_thumb_path else None
        if not free_thumb_file or not free_thumb_file.exists():
            day_thumbs = sorted(thumb_dir.glob(f"thumb_free_day{day}_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
            all_thumbs = day_thumbs or sorted(thumb_dir.glob("thumb_free_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
            free_thumb_file = all_thumbs[0] if all_thumbs else (thumb_dir / "thumb_paid_autoflow_pro_50.png")
        free_uri = _img_to_data_uri(free_thumb_file)

        prev_titles_set = set(day_ctx["recent_titles"])
        chosen_payload = None
        used_llm = False

        if not force and script_path.exists():
            try:
                existing = json.loads(script_path.read_text(encoding="utf-8"))
                ok, _ = self.validate_script_payload(
                    existing,
                    prev_narrations=day_ctx["prev_narrations"],
                    prev_titles=prev_titles_set,
                    require_cards=True,
                )
                if ok:
                    chosen_payload = existing
            except Exception:
                chosen_payload = None

        if chosen_payload is None:
            llm_payload = self._generate_llm_short_script(day, concept, clean_niche_title, day_ctx, metrics_ctx)
            if llm_payload:
                chosen_payload = llm_payload
                used_llm = True
            else:
                chosen_payload = self._build_fallback_script(day, concept, clean_niche_title, day_ctx, metrics_ctx)

        scenes_with_html = []
        clean_scenes_meta = []
        for idx, sc in enumerate(chosen_payload["scenes"], start=1):
            card = sc.get("card") or {}
            html_doc = self._render_scene_html(day, idx, concept, card, metrics_ctx, free_uri, paid_sale_uri)
            scenes_with_html.append({
                "scene": idx,
                "narration": sc["narration"].strip(),
                "text": sc["text"].strip(),
                "html": html_doc,
            })
            clean_scenes_meta.append({
                "scene": idx,
                "narration": sc["narration"].strip(),
                "text": sc["text"].strip(),
                "card": card,
            })

        script_meta = {
            "day": day,
            "concept": concept["name"],
            "free_recipe_focus": clean_niche_title,
            "video_title": chosen_payload["video_title"].strip(),
            "description": (
                f"90日間AI事業構築ドキュメント Day {day}（{concept['name']}）\n"
                f"本日の注目無料レシピ：『{clean_niche_title}』 / 需要1位：『{day_ctx['top1_short']}』\n"
                f"本日の会議テーマ：{day_ctx['agenda']}\n"
                f"▼ 無料レシピ・単品¥500キット・50選¥{price_jpy}パックはチャンネルプロフィール欄のURLからご覧ください\n"
                f"（公開note計{total_notes}本・累計スキ{total_likes}件）\n\n"
                f"#AI副業 #業務自動化 #GAS自動化 #AI起業対決 #Shorts"
            ),
            "hashtags": ["#AI副業", "#業務自動化", "#GAS自動化", "#Shorts"],
            "pinned_comment": chosen_payload["pinned_comment"].strip(),
            "scenes": clean_scenes_meta,
        }

        script_path.write_text(json.dumps(script_meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "day": day,
            "concept": concept["name"],
            "script_path": str(script_path),
            "script_meta": script_meta,
            "scenes": scenes_with_html,
            "used_llm": used_llm,
        }

    def build_and_upload_daily_short(
        self,
        day: int,
        balance: int = 15000,
        price_jpy: int = 980,
        total_notes: int = 15,
        total_likes: int = 44,
        gh_clones: int = 407,
        gh_uniques: int = 134,
        latest_note_title: str = "",
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

        gen = self.generate_script_and_scenes(
            day=day,
            balance=balance,
            price_jpy=price_jpy,
            total_notes=total_notes,
            total_likes=total_likes,
            gh_clones=gh_clones,
            gh_uniques=gh_uniques,
            latest_note_title=latest_note_title,
            latest_note_thumb_path=latest_note_thumb_path,
        )

        # ローカル動画レンダリング専用モジュールのみ遅延import（GitHub Actions非依存維持のため）
        from build_day7_and_8_shorts import render_short_from_scenes
        video_path = render_short_from_scenes(day, gen["scenes"], gen["script_meta"])

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
            "concept": gen["concept"],
            "video_path": str(video_path),
            "youtube_url": yt_url,
        }


if __name__ == "__main__":
    target_day = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    agent = DailyShortPipelineAgent()
    res = agent.build_and_upload_daily_short(day=target_day, auto_upload=("--upload" in sys.argv))
    print(json.dumps(res, ensure_ascii=False, indent=2))
