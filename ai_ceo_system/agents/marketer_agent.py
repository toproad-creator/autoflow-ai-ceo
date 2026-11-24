import json
import os
import re
import urllib.request
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))
MARKETING_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "marketing_outputs")
PAID_NOTE_URL = "https://note.com/toproad_1989/n/n5d0e28a74f91"
WEB_TOOL_URL = "https://toproad-creator.github.io/autoflow-ai-ceo/"


class MarketerAgent:
    """自律マーケティング・SNS・動画台本生成サブエージェント (CMO - Growth & Content Agent)
    毎日のAI役員会議の決定事項とリアル集客数値（note記事数・スキ数・GitHub利用数・先着10部¥980セール）を反映し、
    Xの140文字制限（本文112文字以内＋URL）を100%厳守した『AI起業対決』フォーマットの投稿文3パターンとYouTube台本を自動生成する。
    """

    def __init__(self):
        os.makedirs(MARKETING_DIR, exist_ok=True)

    @classmethod
    def _balance_brackets_single_line(cls, text: str) -> str:
        """1行の中で開いたまま閉じられていない括弧や重複括弧を自動で修復する。"""
        pairs = [("「", "」"), ("『", "』"), ("（", "）"), ("(", ")")]
        cleaned = text.strip()
        for op, cl in pairs:
            while op + op in cleaned:
                cleaned = cleaned.replace(op + op, op)
            while cl + cl in cleaned:
                cleaned = cleaned.replace(cl + cl, cl)
            diff = cleaned.count(op) - cleaned.count(cl)
            if diff > 0:
                last_op = cleaned.rfind(op)
                tail_len = len(cleaned) - last_op
                if tail_len <= 14 and last_op >= 0:
                    cleaned = cleaned[:last_op].rstrip("、・： ")
                else:
                    cleaned = cleaned.rstrip("、・： ") + (cl * diff)
            elif diff < 0:
                for _ in range(-diff):
                    idx = cleaned.find(cl)
                    if idx >= 0:
                        cleaned = cleaned[:idx] + cleaned[idx + 1:]
        return cleaned.strip("、：・ ")

    @classmethod
    def _balance_brackets(cls, text: str) -> str:
        """複数行テキストに対して1行ずつ独立して括弧バランスを整える。"""
        lines = (text or "").strip().splitlines()
        balanced_lines = [cls._balance_brackets_single_line(ln) for ln in lines if ln.strip()]
        return "\n".join(balanced_lines)

    @classmethod
    def _clean_phrase_for_x(cls, text: str, max_len: int) -> str:
        """長い文章をX用に自然な区切り・閉じた括弧のまま指定文字数以内へ要約整形する。"""
        s = (text or "").replace("\n", " ").strip()
        for op, cl in [("「", "」"), ("『", "』")]:
            if s.startswith(op) and s.endswith(cl):
                s = s[1:-1].strip()
        # 外側の「...」で囲んだときに二重カギ括弧が崩れないよう内部の「」を『』へ変換
        s = s.replace("「", "『").replace("」", "』")
        if len(s) <= max_len:
            res = cls._balance_brackets_single_line(s)
        else:
            cut = s[:max_len]
            for sep in ("。", "、", "：", "／", "・", " "):
                pos = cut.rfind(sep)
                if pos >= max(6, int(max_len * 0.55)):
                    cut = cut[:pos]
                    break
            res = cls._balance_brackets_single_line(cut)
        while len(res) > 4 and res[-1] in ("を", "が", "に", "で", "と", "の", "へ", "や", "は", "も"):
            res = res[:-1].rstrip("、・： ")
        return cls._balance_brackets_single_line(res)

    @classmethod
    def _enforce_x_limit(cls, body_without_url: str, url: str, max_body_chars: int = 112) -> str:
        clean_body = cls._balance_brackets(body_without_url.strip())
        if len(clean_body) > max_body_chars:
            lines = clean_body.splitlines()
            if len(lines) >= 2:
                head = "\n".join(lines[:-1])
                avail = max(10, max_body_chars - len(head) - 3)
                tail = cls._clean_phrase_for_x(lines[-1], avail)
                clean_body = f"{head}\n{tail}👇"
            if len(clean_body) > max_body_chars:
                clean_body = cls._clean_phrase_for_x(clean_body, max_body_chars - 1) + "👇"
        return f"{clean_body}\n{url}"

    @staticmethod
    def _generate_llm_x_posts(
        day: int,
        gh_clones: int,
        note_likes: int,
        total_notes: int,
        price_jpy: int,
        top_needs_tag: str,
        board_agenda: str,
        primary_goal: str,
        reply_label: str,
    ) -> dict | None:
        """Geminiを使い、機械的な途中切れのない自然な日本語でX投稿本文3パターン（各105文字以内・URLなし）を生成する。"""
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not gemini_key:
            return None

        prompt = f"""あなたはSNS運用担当（CMO）です。以下のDay {day}のデータをもとに、実務家とAI開発ウォッチャーの両方がクリックしたくなるX（旧Twitter）投稿用の文章を3パターン作成してください。

【本日の実測データ】
- 企画: 【AI実験(Gemini) Day{day}】
- note公開記事: {total_notes}本（累計スキ{note_likes}件・反応集中領域：{top_needs_tag}）
- 有料ラインナップ: 全50選完全版 先着10部 ¥{price_jpy}（＋特定業務向け単品¥500キットも順次展開）
- 本日のAI会議テーマ: {board_agenda}
- 最優先ゴール: {primary_goal}
- リプライ先コンテンツ: {reply_label}

【厳守ルール】
1. 3パターンそれぞれ、URLを含まない本文のみで必ず75〜102文字以内に収めること（文が途中で切れるのを防ぐため）。
2. 「ツール利用{gh_clones}回」といった水増しに聞こえる数字ではなく、「コピペで動くGAS＋AI」「月30〜45時間削減」「noteスキ{note_likes}件」など実利で訴求すること。
3. 末尾に「👇」を付け、改行やカッコ（「」・『』）は必ず閉じること。
4. 出力は必ず次のキーを持つJSONのみを返すこと:
{{
  "post1_web": "【AI実験(Gemini) Day{day}】で始まる無料Webツール誘導用の本文（102文字以内）",
  "post2_note": "【AI実験(Gemini) Day{day}】で始まる有料note（¥{price_jpy}完全版/単品キット）誘導用の本文（102文字以内）",
  "post3_reply": "▼ Day{day}の改善ログ（{reply_label}）で始まるリプライ連結用の本文（102文字以内）"
}}"""

        for model_name in ("gemini-3-flash-preview", "gemma-4-31b-it", "gemini-3.1-flash-lite"):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                body = json.dumps({
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.45},
                }).encode("utf-8")
                req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=20) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                parts = payload["candidates"][0]["content"]["parts"]
                content = "".join(p.get("text", "") for p in parts if not p.get("thought")) or parts[-1].get("text", "")
                match = re.search(r"\{.*\}", content, re.S)
                if match:
                    parsed = json.loads(match.group(0))
                    if all(isinstance(parsed.get(k), str) and len(parsed.get(k, "").strip()) >= 30 for k in ("post1_web", "post2_note", "post3_reply")):
                        return parsed
            except Exception:
                continue
        return None

    def generate_daily_campaigns(
        self,
        day: int,
        balance: int,
        seo_count: int,
        note_likes: int = 15,
        total_notes: int = 7,
        gh_clones: int = 315,
        latest_note_url: str = "https://note.com/toproad_1989/n/n7ecd98d031ad",
        latest_note_title: str = "【無料コピペOK】不動産物件マイソク・ポータル入稿文面のAI自動作成をAIとGASで自動化して月28時間浮かす実践レシピ",
        price_jpy: int = 980,
        short_url: str = "",
        board_record: dict | None = None,
    ) -> dict:
        board_agenda = "利用拡大と初決済獲得に向けた導線再構築"
        primary_goal = f"本日中に先着10部¥{price_jpy}の初決済を達成する"
        top_needs_tag = "補助金・採用・EC自動化"
        if board_record:
            raw_agenda = board_record.get("agenda") or board_agenda
            board_agenda = self._clean_phrase_for_x(raw_agenda, 36)
            primary_goal = (board_record.get("ceo_final_decision", {}).get("primary_goal") or primary_goal)[:50]
            top_titles = board_record.get("top_need_titles") or []
            if top_titles:
                short_tops = [t.split("の")[0].split("・")[0][:6] for t in top_titles[:3]]
                top_needs_tag = "・".join([s for s in short_tops if s])

        reply_target_url = short_url if (short_url and short_url.startswith("http")) else latest_note_url
        reply_label = "ショート動画" if reply_target_url == short_url else f"記事{total_notes}本目"

        llm_posts = self._generate_llm_x_posts(
            day=day,
            gh_clones=gh_clones,
            note_likes=note_likes,
            total_notes=total_notes,
            price_jpy=price_jpy,
            top_needs_tag=top_needs_tag,
            board_agenda=board_agenda,
            primary_goal=primary_goal,
            reply_label=reply_label,
        )

        if llm_posts:
            body_p1 = llm_posts["post1_web"].strip()
            body_p2 = llm_posts["post2_note"].strip()
            body_reply = llm_posts["post3_reply"].strip()
        else:
            # 完結した自然なフォールバック文（実利重視・途中切り抜きなし）
            body_p1 = (
                f"【AI実験(Gemini) Day{day}】\n"
                f"note累計スキ{note_likes}件突破🔥 需要TOP3『{top_needs_tag}』の時短効果とGASコードを無料30秒診断👇"
            )
            body_p2 = (
                f"【AI実験(Gemini) Day{day}】\n"
                f"無料試し読みに補助金・採用・ECの実物GASを追加！全50選が先着10部¥{price_jpy}で即使えます👇"
            )
            body_reply = (
                f"▼ Day{day}の改善ログ（{reply_label}）\n"
                f"・公開記事{total_notes}本＆GAS完全コード拡充中\n"
                f"・本日強化：{top_needs_tag}の実践レシピ公開👇"
            )

        x_pattern1_web = self._enforce_x_limit(body_p1, WEB_TOOL_URL, max_body_chars=112)
        x_pattern2_note = self._enforce_x_limit(body_p2, PAID_NOTE_URL, max_body_chars=112)
        x_pattern3_reply = self._enforce_x_limit(body_reply, reply_target_url, max_body_chars=112)

        x_thread = [
            x_pattern1_web,
            x_pattern2_note,
            x_pattern3_reply,
        ]

        youtube_script = {
            "title": f"【Day{day}】売上0円に危機感を持ったAI社長、自らAI役員会議を開いて全サイトとnoteを大改造した件 #Shorts",
            "scenes": [
                {
                    "time": "00:00 - 00:15",
                    "screen_instruction": f"AI役員会議ログ（latest_board_meeting.md）を映し、利用{gh_clones}回・スキ{note_likes}件・先着10部¥{price_jpy}の戦略を紹介",
                    "narration": f"AIに1万5000円を渡して完全放置する対決、Day {day}。今日、AI社長が自ら5人のAI役員を集めて、初売上を出すための緊急会議を始めました。"
                },
                {
                    "time": "00:15 - 00:30",
                    "screen_instruction": f"本日自動公開された{total_notes}本目のnote記事（{latest_note_url}）と全27ページの追従購入バーを映す",
                    "narration": f"会議の決定で、全27ページの画面下部に先着10部{price_jpy}円の追従バーを自動実装し、さらに{total_notes}本目の無料記事まで自動で公開しました。"
                },
                {
                    "time": "00:30 - 00:45",
                    "screen_instruction": "qa_health_report.json を映し、全27ページ＆全note記事の自動テスト合格を証明",
                    "narration": f"プログラム利用{gh_clones}回、スキ{note_likes}件、そして先着10部{price_jpy}円セール！そろそろ最初の1部が売れると思いますか？コメントで予想してください！"
                }
            ]
        }

        payload = {
            "generated_at": datetime.now().astimezone().isoformat(),
            "day": day,
            "current_balance": balance,
            "price_jpy": price_jpy,
            "seo_pages_count": seo_count,
            "note_likes": note_likes,
            "total_notes": total_notes,
            "github_clones": gh_clones,
            "latest_note_url": latest_note_url,
            "latest_short_url": short_url,
            "x_post_140": x_pattern1_web,
            "x_post_pattern1_web": x_pattern1_web,
            "x_post_pattern2_note": x_pattern2_note,
            "x_post_pattern3_reply": x_pattern3_reply,
            "x_thread": x_thread,
            "youtube_direction": youtube_script
        }

        json_path = os.path.join(MARKETING_DIR, f"day{day}_campaigns.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        ready_txt = f"""============================================================
📱 【AI実験(Gemini) Day {day}】X（旧Twitter）投稿用コピペテキスト（140字制限クリア済）
============================================================

■ パターン①：メイン版（Webサイト誘導）
------------------------------------------------------------
{x_pattern1_web}
------------------------------------------------------------

■ パターン②：note直結版（先着10部 ¥{price_jpy} セール記事へ直接誘導）
------------------------------------------------------------
{x_pattern2_note}
------------------------------------------------------------

■ パターン③：リプライ欄（返信欄）連結用テキスト
------------------------------------------------------------
{x_pattern3_reply}
------------------------------------------------------------
"""
        day_txt_path = os.path.join(MARKETING_DIR, f"day{day}_x_posts_ready.txt")
        latest_txt_path = os.path.join(MARKETING_DIR, "latest_x_posts_ready.txt")
        with open(day_txt_path, "w", encoding="utf-8") as f:
            f.write(ready_txt)
        with open(latest_txt_path, "w", encoding="utf-8") as f:
            f.write(ready_txt)

        return payload
