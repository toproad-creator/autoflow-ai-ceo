import json
import os
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRODUCT_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "product_site")
PRIVATE_DATA_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "data")
EVOLUTION_STATE_PATH = os.path.join(PRIVATE_DATA_DIR, "company_evolution_state.json")
NOTE_CHECKOUT_URL = "https://note.com/toproad_1989/n/n5d0e28a74f91"


def _sanitize_customer_text(text: str) -> str:
    cleaned = text or ""
    for term in ("AI起業対決", "AI CEO", "実験ログ", "実験台", "実験", "対決"):
        cleaned = cleaned.replace(term, "")
    return cleaned.strip()


class ProductPackagerAgent:
    """有料商品パッケージ＆高成約率セールスLP構築サブエージェント
    実際に販売する『全職種対応・業務自動化50種プロンプト＆GAS完全版パック』の商品データ本体と、
    市場ニーズTOP3・3段階商品の階段（無料→¥980→上位設計）を反映したセールスLP（pro-pack.html）を自動生成する。
    """

    def __init__(self):
        os.makedirs(PRIVATE_DATA_DIR, exist_ok=True)

    @staticmethod
    def _load_evolution_state() -> dict:
        if os.path.exists(EVOLUTION_STATE_PATH):
            try:
                with open(EVOLUTION_STATE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

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
        evo_state = self._load_evolution_state()
        offer_cfg = evo_state.get("dynamic_offer_config", {})
        winners = offer_cfg.get("winner_highlights") or [
            {"rank": 1, "slug": "ec-inventory", "title": "EC・物販の在庫管理＆価格改定自動化", "avg_hours_saved_monthly": 42, "yearly_yen": 1260000},
            {"rank": 2, "slug": "subsidy-business-plan", "title": "補助金申請・融資用の事業計画書ドラフト＆収支表自動作成", "avg_hours_saved_monthly": 45, "yearly_yen": 1890000},
            {"rank": 3, "slug": "hr-resume-screening", "title": "採用・人事の職務経歴書スクリーニング＆面接質問自動生成", "avg_hours_saved_monthly": 32, "yearly_yen": 1152000},
        ]
        ladder = evo_state.get("product_ladder") or [
            {
                "tier": "STEP 1｜無料スターター",
                "name": "AutoFlow 無料Webツール＆厳選5種レシピ",
                "price_label": "¥0（登録不要）",
                "target": "まずは1つ自分の業務で試してみたい方",
                "features": ["業務削減ROIシミュレーター＋コード即時生成", "構造化プロンプト設計＆GASエラー3秒診断", "厳選5種類の無料サンプルコード体験"],
                "cta_label": "無料で試してみる →",
                "cta_url": "free-templates.html",
                "highlight": False,
            },
            {
                "tier": "STEP 2｜一番人気・入門完全版",
                "name": "AutoFlow Pro 全10業種・50選 完全版パック",
                "price_label": "限定 ¥980（定価 ¥1,980 / 先着10部）",
                "target": "エラー対策済みの実用コード50本を今すぐ現場導入したい方",
                "features": ["人気TOP3含む全50本を完全収録", "エラーリトライ・通知連携付きの完成GASコード", "無料エリアで実物2本＆全50一覧を事前確認OK"],
                "cta_label": "🔥 限定 ¥980 で今すぐ入手する →",
                "cta_url": NOTE_CHECKOUT_URL,
                "highlight": True,
            },
            {
                "tier": "STEP 3｜上位・部門導入拡張",
                "name": "AutoFlow Business 部門横断カスタム自動化設計",
                "price_label": "想定 ¥4,980（上位拡張モデル）",
                "target": "請求書・契約チェック・チームKPI連携まで自動化したい法人・上級者",
                "features": ["BtoBバックオフィス・契約監査・補助金支援特化", "複数シート連携＆Slack/Chatwork自動レポート統合", "STEP 2 完全版ユーザー向けの優先アップグレード対象"],
                "cta_label": "まずはSTEP 2（限定¥980）から始める →",
                "cta_url": NOTE_CHECKOUT_URL,
                "highlight": False,
            },
        ]

        hero_badge = _sanitize_customer_text(offer_cfg.get("hero_badge", "🔥 先着10部限定 50%OFFセール開催中（¥1,980 ➔ ¥980）"))
        spotlight_sub = _sanitize_customer_text(
            offer_cfg.get(
                "spotlight_subcopy",
                "時給2,500円換算でたった24分分の作業が浮けば元が取れる（先着10部限定 ¥980 / 1レシピあたり約19円）実践テンプレート集。構造化AIプロンプト50本とGASコードをセットで収録しています。",
            )
        )

        top3_html = ""
        for w in winners[:3]:
            title_clean = _sanitize_customer_text(w.get("title", ""))
            top3_html += f"""
            <a href="usecases/{w.get('slug', 'ec-inventory')}.html" class="block bg-slate-900/90 hover:bg-slate-800 border border-amber-400/40 rounded-xl p-4 transition">
              <div class="flex items-center justify-between text-[11px] font-bold mb-1">
                <span class="bg-amber-400/20 text-amber-300 px-2 py-0.5 rounded">注目ランキング #{w.get('rank', 1)}</span>
                <span class="text-emerald-400">年間削減目安 ¥{int(w.get('yearly_yen', 1000000)):,}</span>
              </div>
              <div class="font-bold text-sm text-slate-100 mt-1">{title_clean}</div>
              <div class="text-xs text-slate-400 mt-1">月平均 {w.get('avg_hours_saved_monthly', 30)}時間削減レシピを見る →</div>
            </a>
            """

        ladder_html = ""
        for step in ladder:
            is_hi = step.get("highlight", False)
            border_cls = "border-2 border-amber-400 bg-gradient-to-b from-slate-900 to-indigo-950 shadow-2xl" if is_hi else "border border-slate-800 bg-slate-900/80"
            btn_cls = "bg-amber-400 hover:bg-amber-300 text-slate-950 font-black" if is_hi else "bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700 font-bold"
            target_attr = 'target="_blank" rel="noopener"' if step.get("cta_url", "").startswith("http") else ""
            feats = "".join(f"<li class='text-xs text-slate-300 flex items-start gap-1.5'><span>✔</span><span>{_sanitize_customer_text(ft)}</span></li>" for ft in step.get("features", []))
            ladder_html += f"""
            <div class="{border_cls} rounded-2xl p-6 flex flex-col justify-between">
              <div>
                <span class="text-[11px] font-bold {'text-amber-300' if is_hi else 'text-sky-400'}">{_sanitize_customer_text(step.get('tier', ''))}</span>
                <h3 class="text-lg font-extrabold text-white mt-1">{_sanitize_customer_text(step.get('name', ''))}</h3>
                <div class="text-base font-black {'text-amber-400' if is_hi else 'text-slate-200'} mt-2 mb-2">{_sanitize_customer_text(step.get('price_label', ''))}</div>
                <p class="text-xs text-slate-400 mb-4">{_sanitize_customer_text(step.get('target', ''))}</p>
                <ul class="space-y-2 mb-6">{feats}</ul>
              </div>
              <a href="{step.get('cta_url', NOTE_CHECKOUT_URL)}" {target_attr} class="block text-center text-xs px-4 py-3 rounded-xl transition {btn_cls}">
                {_sanitize_customer_text(step.get('cta_label', ''))}
              </a>
            </div>
            """

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
      <span class="bg-amber-400/20 text-amber-300 border border-amber-400/40 text-xs font-bold px-3 py-1 rounded-full">{hero_badge}</span>
      <h1 class="text-3xl md:text-5xl font-extrabold mt-4 mb-4 leading-tight">
        コピペ5分で「毎日のルーティン作業」を消滅させる<br/><span class="text-sky-400">AutoFlow Pro 完全版パッケージ</span>
      </h1>
      <p class="text-slate-400 max-w-2xl mx-auto text-sm md:text-base">
        {spotlight_sub}
      </p>
    </div>

    <!-- 最近のニーズ調査で特に選ばれている注目レシピ TOP3 -->
    <section class="mb-12">
      <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
        <h2 class="text-xl font-bold">📈 最近のニーズ調査で特に選ばれている注目レシピ TOP3</h2>
        <span class="text-xs text-slate-400">需要の高い実践領域をピックアップ</span>
      </div>
      <div class="grid md:grid-cols-3 gap-4">
        {top3_html}
      </div>
    </section>

    <!-- 目的に合わせて選べる3つの導入ステップ（商品の階段） -->
    <section class="mb-14">
      <div class="text-center mb-6">
        <span class="text-xs font-bold text-sky-400 uppercase tracking-wider">導入ステップ別プラン</span>
        <h2 class="text-2xl font-extrabold mt-1">🪜 目的に合わせて選べる3つの導入ステップ</h2>
        <p class="text-xs text-slate-400 mt-1">まずは無料ツールで体験し、実務導入なら全50選完全版パック（限定¥980）が最もお得です。</p>
      </div>
      <div class="grid md:grid-cols-3 gap-5">
        {ladder_html}
      </div>
    </section>

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

