import json
import os
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
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
        board_action_short = f"全27ページに限定¥{price_jpy}追従バーを実装"
        top_needs_tag = "補助金・採用・EC自動化"
        if board_record:
            raw_agenda = board_record.get("agenda") or board_agenda
            board_agenda = self._clean_phrase_for_x(raw_agenda, 24)
            actions = board_record.get("ceo_final_decision", {}).get("approved_actions", [])
            if actions:
                first_act = actions[0].split("】")[-1].strip()
                if first_act:
                    board_action_short = self._clean_phrase_for_x(first_act, 24)
            top_titles = board_record.get("top_need_titles") or []
            if top_titles:
                short_tops = [t.split("の")[0][:5] for t in top_titles[:3]]
                top_needs_tag = "・".join(short_tops)

        # パターン①：メイン版（Webサイト誘導・本文112文字以内厳守）
        body_p1 = (
            f"【AI起業対決 Day{day}】\n"
            f"利用{gh_clones}回・スキ{note_likes}件でも売上0円にAI役員会議が危機感🔥\n"
            f"需要TOP3（{top_needs_tag}）集中と「{self._clean_phrase_for_x(board_action_short, 18)}」を実行👇"
        )
        x_pattern1_web = self._enforce_x_limit(body_p1, WEB_TOOL_URL, max_body_chars=112)

        # パターン②：note直結版（¥980セール記事へ直接誘導・本文112文字以内厳守）
        body_p2 = (
            f"【AI起業対決 Day{day}】\n"
            f"AI会議で「{self._clean_phrase_for_x(board_agenda, 22)}」を決議！\n"
            f"{top_needs_tag}特化オファー＆先着10部¥{price_jpy}で公開中👇"
        )
        x_pattern2_note = self._enforce_x_limit(body_p2, PAID_NOTE_URL, max_body_chars=112)

        # パターン③：リプライ欄用（YouTubeショートまたは最新無料note誘導・本文112文字以内厳守）
        reply_target_url = short_url if (short_url and short_url.startswith("http")) else latest_note_url
        reply_label = "ショート動画" if reply_target_url == short_url else f"記事{total_notes}本目"
        body_reply = (
            f"▼ Day{day}のAI会議＆自己改善ログ（{reply_label}）\n"
            f"・ツール利用：{gh_clones}回 / スキ：{note_likes}件\n"
            f"・実施：{self._clean_phrase_for_x(board_action_short, 24)}👇"
        )
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
