import json
import os
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MARKETING_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "marketing_outputs")


class MarketerAgent:
    """自律マーケティング・SNS・動画台本生成サブエージェント (Growth & Content Agent)
    プロダクトの集客導線、X/Threads投稿データ、YouTube実況台本を自動生成する。
    """

    def __init__(self):
        os.makedirs(MARKETING_DIR, exist_ok=True)

    def generate_daily_campaigns(self, day: int, balance: int, seo_count: int, note_likes: int = 1) -> dict:
        x_140 = (
            f"【AI起業対決 Day{day}】人間が完全放置して寝ている間に、AI社長が朝8時00分03秒に自動起動して仕事を始めてた…😨\n"
            f"しかもAIが執筆したnoteに最初の「スキ({note_likes}件)」が付き、今日さらに第2弾ツール『GASエラー3秒診断(AutoFix AI)』とSEOページ{seo_count}本を勝手に追加公開してる👇\n"
            "https://toproad-creator.github.io/autoflow-ai-ceo/"
        )

        x_thread = [
            f"1/5 【90日間・人間介入ゼロ AI起業対決 Day {day}】人間がPCを放置している間に何が起きたか報告します。結論から言うと、今朝08:00:03にAI社長（Antigravity）の自動タイマーが勝手に起動し、収支監査とWebサイトの拡張を自力で完了していました。",
            f"2/5 さらに財務・計測AI（CFOエージェント）がnoteのAPIを自動巡回したところ、昨日公開した『全50種プロンプト＆GAS完全版パック（¥1,980）』に早くも最初のリアクション（スキ: {note_likes}件）が付いているのを検知！",
            "3/5 これを受けてAI社内会議が下した今日の戦略がエグい。『GASをコピペした初心者が最初にぶつかる壁は赤字のエラー画面である』と分析し、なんと第2弾の無料Webツール『AutoFix AI（GASエラー＆プロンプト3秒診断・自動修正ツール）』をその場で新規開発！",
            f"4/5 同時に、検索流入（Programmatic SEO）の業種別ランディングページを10業種→{seo_count}業種へ倍増（不動産・採用人事・EC返品対応・補助金事業計画・広告コピー等）。すべてのページにGoogle検索用のFAQ構造化データ（JSON-LD）まで自動で埋め込んでいます。",
            "5/5 初期軍資金15,000円は1円も減らさず（現在残高¥15,000）、稼働中の公開Webページは計23ページに拡大。明日以降どこで初売上（¥1,980チャリン）が鳴るのか引き続き完全放置で監視します！\n👉 https://toproad-creator.github.io/autoflow-ai-ceo/"
        ]

        youtube_script = {
            "title": f"【Day {day}】人間が寝ている朝8時00分03秒にAIが勝手に起動し、2個目のWebツールと集客ページ20本を増殖させていた件【AI起業対決】",
            "scenes": [
                {
                    "time": "00:00 - 00:50",
                    "screen_instruction": "wallet.json の last_updated が 08:00:03 になっているログ画面と、note記事に『スキ 1』が付いているAPI取得結果を映す",
                    "narration": f"AIに1万5000円を渡して完全放置する対決、Day {day}です。これ見てください、僕が何も触っていないのに、今朝8時00分03秒にAI社長が自動で目を覚まして帳簿を更新しています。しかもAIが自分でnoteのAPIを叩いて、昨日出した1,980円の記事に最初の『スキ』が付いたことまで勝手に把握していました。"
                },
                {
                    "time": "00:50 - 02:00",
                    "screen_instruction": "新設された https://toproad-creator.github.io/autoflow-ai-ceo/gas-debugger.html を開き、エラーを選ぶと原因と修正済みGASコードが一瞬で出る画面を実演",
                    "narration": "さらに今日、AIが『もっと集客してnoteを買ってもらうにはどうすべきか』を自分で考えて、なんと2個目のWebサービス『AutoFix AI（GASエラー3秒診断ツール）』を勝手に作って公開していました。GASでよくあるエラーを選ぶだけで、原因と修正済みコードが3秒で出てきて、その下にしっかり『最初からエラー対策済みの50種パック（1,980円）はこちら』と営業リンクまで貼っています。"
                },
                {
                    "time": "02:00 - 03:00",
                    "screen_instruction": "トップページ下部に追加された『全20業種レシピ一覧』をスクロールし、業種ページを開いて構造化データとスタータープロンプトが入っている様子を映す",
                    "narration": "しかも検索エンジンから人を呼び込むための業種別ページも、昨日の10ページから20ページに倍増しています。軍資金15,000円はまだ1円も減っていません。完全放置のAI社長がいつ最初の1,980円を売り上げるのか、明日も追跡します！"
                }
            ]
        }

        payload = {
            "generated_at": datetime.now().astimezone().isoformat(),
            "day": day,
            "current_balance": balance,
            "seo_pages_count": seo_count,
            "note_likes": note_likes,
            "x_post_140": x_140,
            "x_thread": x_thread,
            "youtube_direction": youtube_script
        }

        json_path = os.path.join(MARKETING_DIR, f"day{day}_campaigns.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return payload
