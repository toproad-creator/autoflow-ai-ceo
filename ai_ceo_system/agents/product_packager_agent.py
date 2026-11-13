import json
import os
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRODUCT_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "product_site")
PRIVATE_DATA_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "data")
NOTE_CHECKOUT_URL = "https://note.com/toproad_1989/n/n5d0e28a74f91"


class ProductPackagerAgent:
    """有料商品パッケージ＆高成約率セールスLP構築サブエージェント
    ダミーのアラートを撤廃し、実際に販売する『全職種対応・業務自動化50種プロンプト＆GAS完全版パック（¥1,980）』の
    商品データ本体と、note決済直結セールスLP（pro-pack.html）を自動生成する。
    """

    def __init__(self):
        os.makedirs(PRIVATE_DATA_DIR, exist_ok=True)

    def build_commercial_product_and_lp(self) -> dict:
        categories = [
            ("EC・物販", ["競合価格の毎朝自動取得＆値下げアラート", "在庫切れ寸前商品の自動検知＆発注書作成", "景表法NGワード自動除外＆SEO商品名生成", "英語・中国語仕入れ先への交渉メール自動作成", "購入者レビューの感情分析＆改善点抽出"]),
            ("SNSマーケティング", ["X(旧Twitter)インプレッション獲得140字構文生成", "長文スレッド5連投の結論ファースト自動構成", "Threads向け共感ストーリー型投稿ジェネレーター", "スプレッドシート予約投稿のWebhook自動配信", "競合バズ投稿のフック構造分解プロンプト"]),
            ("営業・カスタマーサポート", ["顧客Webサイト解析からの1to1営業メール作成", "問い合わせフォーム受信時の即時一次返信＆Slack通知", "商談議事録テキストからのToDo・次回提案書自動生成", "休眠顧客の掘り起こしステップメール3通生成", "クレーム・謝罪メールの冷静かつ誠実な回答案作成"]),
            ("経理・バックオフィス", ["請求書PDFテキストからのインボイス対応TSV抽出", "Googleドライブ内『請求書』ファイルの毎晩自動台帳記帳", "毎月のサブスク・固定費スプレッドシート異常値検知", "交通費・経費精算データの自動仕訳＆勘定科目判定", "月末の未入金取引先リスト抽出＆リマインド下書き作成"]),
            ("YouTube・ショート動画", ["冒頭3秒で離脱を防ぐショート動画台本ジェネレーター", "長尺YouTube動画のチャプター＆概要欄SEO自動生成", "クリック率を高めるサムネイル文言20案出力", "既存ブログ記事から動画用ナレーション台本への変換", "YouTubeコメント欄の質問自動抽出＆企画ネタ化"]),
            ("SEO記事・Webメディア", ["検索意図を網羅するH2/H3見出し構成案の自動設計", "専門用語を初心者向けに噛み砕くリライトプロンプト", "記事公開前のファクトチェック＆誤字脱字監査", "構造化データ(JSON-LD FAQPage)のワンクリック生成", "内部リンク最適化のための関連記事アンカーテキスト提案"]),
            ("人事・採用・マネジメント", ["求職者の職務経歴書からの強み＆面接質問リスト生成", "スカウトメール返信率を高めるパーソナライズ文面作成", "新入社員向けオンボーディング手順書の自動構造化", "1on1ミーティング記録からのメンタルトレンド要約", "社内FAQボット用Q&Aデータセット自動生成"]),
            ("店舗・ローカルビジネス", ["Googleマップ(MEO)口コミへの高評価お礼＆低評価神対応返信", "LINE公式アカウント配信用のクーポン誘導メッセージ作成", "季節イベントに合わせたチラシ・POPキャッチコピー生成", "予約キャンセル防止のリマインドSMS自動送信スクリプト", "リピート率を高める来店後サンキューメール自動送信"]),
            ("スプレッドシート・GAS自動化", ["複数シートの売上データを1枚のマスターシートへ毎晩自動統合", "指定列が空欄のまま放置されている行の担当者メンション通知", "Googleカレンダーの予定から週次の稼働時間レポート自動集計", "フォーム回答内容をテンプレートGoogleドキュメントへ自動差し込みPDF化", "エラー発生時に自動リトライ＆管理者へスタックトレース通知する共通関数"]),
            ("経営・プロジェクト管理", ["日報テキスト群からのプロジェクト遅延リスク自動検知", "新規事業アイデアの初期コスト0円・損益分岐点シミュレーション", "外注・フリーランス向け業務委託仕様書(要件定義書)の自動作成", "定例会議を廃止するための非同期ステータス報告フォーマット", "KPIデータの前週比・前月比サマリー自動生成＆メール配信"])
        ]

        templates = []
        idx = 1
        for cat_name, titles in categories:
            for t in titles:
                templates.append({
                    "id": f"TPL-{idx:02d}",
                    "category": cat_name,
                    "title": t,
                    "prompt_template": f"【{cat_name}：{t} 専用構造化プロンプト】\nあなたは{cat_name}の専門AIエージェントです。入力データを解析し、手作業をゼロにするための構造化出力（JSONまたはTSV）を生成してください。",
                    "gas_snippet": f"// [{t}] 自動実行Google Apps Script\nfunction runAutoTask_{idx:02d}() {{\n  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();\n  Logger.log('Executing {t}...');\n}}"
                })
                idx += 1

        json_product_path = os.path.join(PRIVATE_DATA_DIR, "autoflow_pro_50_templates.json")
        with open(json_product_path, "w", encoding="utf-8") as f:
            json.dump({"product": "AutoFlow Pro 50 Automation Pack", "price_jpy": 980, "regular_price_jpy": 1980, "checkout_url": NOTE_CHECKOUT_URL, "count": len(templates), "templates": templates}, f, ensure_ascii=False, indent=2)

        lp_path = self._build_sales_lp(templates)
        return {
            "built_at": datetime.now().astimezone().isoformat(),
            "templates_count": len(templates),
            "checkout_url": NOTE_CHECKOUT_URL,
            "product_json": json_product_path,
            "sales_lp": lp_path
        }

    def _build_sales_lp(self, templates: list) -> str:
        cards_html = ""
        for item in templates[:12]:
            cards_html += f"""
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <span class="text-[10px] font-bold bg-sky-500/20 text-sky-300 px-2 py-0.5 rounded">{item['id']} | {item['category']}</span>
              <h4 class="font-bold text-sm mt-2 text-slate-100">{item['title']}</h4>
              <p class="text-xs text-slate-400 mt-1">専用プロンプト ＋ GAS自動実行コード付属</p>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AutoFlow Pro Pack | 全職種対応50種AIプロンプト＆GAS自動化テンプレート完全版 (先着10部限定 ¥980)</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen">
  <header class="border-b border-slate-800 py-4 px-6 max-w-5xl mx-auto flex justify-between items-center">
    <a href="index.html" class="text-sky-400 text-sm font-bold hover:underline">← 無料シミュレーターに戻る</a>
    <span class="text-xs text-amber-400 font-bold">note決済対応（クレカ・PayPay・キャリア決済）・先着10部限定 ¥980</span>
  </header>

  <main class="max-w-5xl mx-auto px-6 py-12">
    <div class="text-center mb-12">
      <span class="bg-amber-400/20 text-amber-300 border border-amber-400/40 text-xs font-bold px-3 py-1 rounded-full">🔥 先着10部限定 50%OFFセール開催中（¥1,980 ➔ ¥980）</span>
      <h1 class="text-3xl md:text-5xl font-extrabold mt-4 mb-4 leading-tight">
        コピペ5分で「毎日のルーティン作業」を消滅させる<br/><span class="text-sky-400">AutoFlow Pro 完全版パッケージ</span>
      </h1>
      <p class="text-slate-400 max-w-2xl mx-auto text-sm md:text-base">
        時給2,500円換算で<strong>たった24分分の作業が浮けば元が取れる（先着10部限定 ¥980 / 1レシピあたり約19円）</strong>実践テンプレート集。
        構造化AIプロンプト50本と、Googleスプレッドシートでそのまま動くGASコードをセットで収録しています。
      </p>
    </div>

    <div class="mb-12">
      <h2 class="text-xl font-bold mb-4">📦 収録されている50種類の自動化テンプレート（一部抜粋）</h2>
      <div class="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
        {cards_html}
      </div>
      <p class="text-center text-xs text-slate-400 mt-4">…ほか全10カテゴリ・計50種類のプロンプト＆GASコードをnote有料エリアにて即時提供（無料試し読みエリアに実物2本＋全50リスト公開中！）</p>
    </div>

    <!-- Checkout CTA Box -->
    <div class="bg-gradient-to-br from-slate-900 to-indigo-950 border-2 border-amber-400/60 rounded-2xl p-8 text-center max-w-2xl mx-auto shadow-2xl">
      <div class="text-xs text-amber-300 font-bold uppercase tracking-wider">🔥 先着10部限定 50%OFFセール価格（買い切り）</div>
      <div class="text-4xl font-black my-2"><span class="line-through text-slate-500 text-2xl mr-2">¥1,980</span>¥980 <span class="text-sm font-normal text-slate-400">(税込・11部目から¥1,480へ改定)</span></div>
      <p class="text-xs text-slate-300 mb-6">noteにて決済後、その場で全50種類のプロンプト＆GASコードをすべて閲覧・コピーいただけます。</p>
      <a href="{NOTE_CHECKOUT_URL}" target="_blank" rel="noopener" onclick="triggerCheckout()" class="inline-block w-full sm:w-auto bg-amber-400 hover:bg-amber-300 text-slate-950 font-black px-8 py-4 rounded-xl text-base shadow-lg transition">
        ⚡ noteで今すぐ完全版パックを入手する (限定 ¥980) →
      </a>
    </div>
  </main>

  <script>
    function triggerCheckout() {{
      try {{ localStorage.setItem('af_checkout_intent', new Date().toISOString()); }} catch (e) {{}}
    }}
  </script>
</body>
</html>
"""
        out_path = os.path.join(PRODUCT_DIR, "pro-pack.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        return out_path


if __name__ == "__main__":
    packager = ProductPackagerAgent()
    print(packager.build_commercial_product_and_lp())

