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

    @staticmethod
    def _enforce_x_limit(body_without_url: str, url: str, max_body_chars: int = 112) -> str:
        clean_body = body_without_url.strip()
        if len(clean_body) > max_body_chars:
            clean_body = clean_body[: max_body_chars - 1] + "👇"
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
        board_action_short = f"全27ページに限定¥{price_jpy}追従バーを自動実装"
        if board_record:
            board_agenda = (board_record.get("agenda") or board_agenda)[:28]
            actions = board_record.get("ceo_final_decision", {}).get("approved_actions", [])
            if actions:
                first_act = actions[0].split("】")[-1].strip()
                if first_act:
                    board_action_short = first_act[:26]

        # パターン①：メイン版（Webサイト誘導・本文112文字以内厳守）
        body_p1 = (
            f"【AI起業対決 Day{day}】\n"
            f"人間が放置してる間にAI役員会議が自己診断し「{board_agenda}」を決議…😨\n"
            f"利用{gh_clones}回・スキ{note_likes}件から{board_action_short}👇"
        )
        x_pattern1_web = self._enforce_x_limit(body_p1, WEB_TOOL_URL, max_body_chars=112)

        # パターン②：note直結版（¥980セール記事へ直接誘導・本文112文字以内厳守）
        body_p2 = (
            f"【AI起業対決 Day{day}】\n"
            f"AI社長が自己点検で「無料満足での離脱」を検知し、記事{total_notes}本目＆改善策（{board_action_short[:18]}）を即時実行…😨\n"
            f"先着10部¥{price_jpy}セール稼働中👇"
        )
        x_pattern2_note = self._enforce_x_limit(body_p2, PAID_NOTE_URL, max_body_chars=112)

        # パターン③：リプライ欄用（最新無料note記事誘導・本文112文字以内厳守）
        body_reply = (
            f"▼ AI役員会議のDay{day}自己改善ログ\n"
            f"・プログラム利用：{gh_clones}回突破\n"
            f"・noteスキ：計{note_likes}件（{total_notes}本目公開）\n"
            f"・AI決議：{board_action_short}👇"
        )
        x_pattern3_reply = self._enforce_x_limit(body_reply, latest_note_url, max_body_chars=112)

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
📱 【AI起業対決 Day {day}】X（旧Twitter）投稿用コピペテキスト（140字制限クリア済）
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
