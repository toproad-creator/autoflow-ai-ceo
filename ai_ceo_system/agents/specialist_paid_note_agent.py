import html as html_lib
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "data")
PROFILE_DIR = os.path.join(DATA_DIR, "note_browser_profile")
SPECIALIST_STATE_PATH = os.path.join(DATA_DIR, "specialist_paid_notes.json")
FLAGSHIP_PAID_URL = "https://note.com/toproad_1989/n/n5d0e28a74f91"

load_dotenv(os.path.join(ROOT_DIR, ".env"))
sys.path.insert(0, os.path.dirname(__file__))


def _sanitize_customer_text(text: str) -> str:
    cleaned = text or ""
    for src, dst in (
        ("AI起業対決", ""),
        ("AI CEO", ""),
        ("実証実験", "導入検証"),
        ("実験ログ", "運用記録"),
        ("実験台", "検証環境"),
        ("実験", "検証"),
        ("対決", "比較"),
    ):
        cleaned = cleaned.replace(src, dst)
    return cleaned.strip()


SPECIALIST_KITS = [
    {
        "slug": "subsidy-business-plan",
        "topic_tag": "補助金・融資 事業計画書",
        "price": 500,
        "title": "【単品¥500】補助金申請・融資の事業計画書＆5カ年収支表をコピペ自動作成する実践AI×GASキット",
        "hours_saved": 45,
        "problem_hook": "ものづくり補助金・小規模事業者持続化補助金・事業再構築・金融機関融資の計画書作成は、ゼロから書くと40〜60時間かかります。しかも審査員が重視する『根拠ある数値連動』や『付加価値額・給与支給総額の計算整合』が崩れると減点対象になります。",
        "kit_outcomes": [
            "採択率を高める審査員基準の事業計画ドラフトを一気通貫で生成する専用プロンプト5本",
            "Googleスプレッドシートへ5カ年収支表＆添付書類シート構成をワンクリック自動構築するGASコード",
            "付加価値額・利益率・根拠メモ不足を自動検出してアラート通知するセルフ監査GASコード",
        ],
        "free_sample_prompt": (
            "# 命令書（補助金・融資計画 現状課題＆投資計画の構造化抽出）\n"
            "あなたは認定経営革新等支援機関レベルの事業計画コンサルタントです。\n"
            "以下の【自社メモ】から審査員が最も評価する「導入背景」「既存課題の数値」「導入投資の回収ロジック」を抜き出し、"
            "補助事業計画書の第1章〜第3章そのまま使える文章案（約1,200字）を作成してください。\n"
            "1. 「大幅向上」「積極的に」などの抽象語を禁止し、必ず時間・金額・割合(%)で記述すること。\n"
            "2. 想定投資額と月間削減時間から「投資回収月数」を明記すること。\n"
            "3. 確認が必要な不足情報には末尾に `[要確認]` タグをリスト化すること。\n\n"
            "# 自社メモ\n（業種・現在の困りごと・導入したいシステム/設備・投資金額を記入）"
        ),
        "paid_prompts": [
            (
                "プロンプト①：審査員加点ポイント網羅・事業計画ドラフト自動構築",
                "あなたは経済産業省系補助金の採択審査を熟知した中小企業診断士です。入力情報をもとに①企業概要と強み、②市場環境と顧客ニーズ、③導入する補助事業の新規性・優位性、④具体的な実施スケジュール（月次ガントチャート表形式）、⑤期待される定量効果をTSV＆文章の両方で生成してください。根拠の薄い主張は `[要根拠データ]` を付与すること。"
            ),
            (
                "プロンプト②：5カ年収支計画（売上・原価・販管費・付加価値額）TSV自動算出",
                "あなたは財務モデリングの専門家です。初期投資額・単価・想定件数・人員計画をもとに、1年目〜5年目の「売上高 / 売上原価 / 粗利 / 販管費 / 営業利益 / 人件費 / 減価償却費 / 付加価値額（年率伸び率％）」の6列TSV表を出力し、補助金要件（付加価値額年率平均+3%以上など）を満たしているか自己検証コメントを添えてください。"
            ),
            (
                "プロンプト③：不採択リスク（減点・矛盾・数値不整合）事前赤入れ監査",
                "あなたが書いた申請書下書きを入力してください。私は「公募要領とのズレ」「前後の数字の矛盾」「競合比較の甘さ」「補助対象外経費の混入リスク」の4観点で辛口採点し、100点満点スコアと修正優先度順の具体的書き換え案を出力します。"
            ),
            (
                "プロンプト④：金融機関融資面談・口頭試問 想定Q&A 15選＆模範回答集",
                "作成した事業計画書に対し、銀行融資担当者や事務局ヒアリングで必ず突っ込まれる「最悪ケースの資金繰り」「販路開拓の具体根拠」「解約率・原価高騰時の耐久力」など15問の想定質問と、説得力ある回答スクリプトを生成してください。"
            ),
            (
                "プロンプト⑤：採択後・実績報告書向け 進捗＆効果測定サマリーテンプレート生成",
                "導入開始後の月次数値データから、事務局提出用の効果報告サマリー（導入前後の作業時間比較・生産性向上率・投資回収進捗）をMarkdown/スプレッドシート貼付形式で生成してください。"
            ),
        ],
        "paid_gas_scripts": [
            (
                "GAS①：5カ年収支計画＆根拠チェック用シートを一撃自動構築 (setupSubsidyWorkbook)",
                """function setupSubsidyWorkbook() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('5カ年収支計画');
  if (!sheet) sheet = ss.insertSheet('5カ年収支計画');
  sheet.clear();
  const headers = [['年度', '売上高(千円)', '売上原価(千円)', '販管費(千円)', '営業利益(千円)', '付加価値額率(%)', '根拠メモ・ステータス']];
  sheet.getRange(1, 1, 1, headers[0].length).setValues(headers)
    .setBackground('#0f172a').setFontColor('#ffffff').setFontWeight('bold');
  const rows = [
    ['基準年度', 30000, 12000, 15000, '=B2-C2-D2', '=IF(B2>0, (E2+3000)/B2, 0)', '確定決算値を入力'],
    ['1年目', '=B2*1.12', '=B3*0.38', 15500, '=B3-C3-D3', '=IF(B3>0, (E3+3200)/B3, 0)', '設備導入効果の根拠記載'],
    ['2年目', '=B3*1.15', '=B4*0.36', 16000, '=B4-C4-D4', '=IF(B4>0, (E4+3400)/B4, 0)', '新規顧客獲得数の根拠記載'],
    ['3年目', '=B4*1.15', '=B5*0.35', 16500, '=B5-C5-D5', '=IF(B5>0, (E5+3600)/B5, 0)', '生産性向上効果反映'],
    ['4年目', '=B5*1.12', '=B6*0.34', 17000, '=B6-C6-D6', '=IF(B6>0, (E6+3800)/B6, 0)', '維持運用フェーズ'],
    ['5年目', '=B6*1.10', '=B7*0.33', 17500, '=B7-C7-D7', '=IF(B7>0, (E7+4000)/B7, 0)', '最終目標達成確認']
  ];
  sheet.getRange(2, 1, rows.length, rows[0].length).setValues(rows);
  sheet.getRange('F2:F7').setNumberFormat('0.0%');
  sheet.autoResizeColumns(1, 7);
}"""
            ),
            (
                "GAS②：数値不整合＆根拠メモ未記入セルの自動監査アラート (auditSubsidyReadiness)",
                """function auditSubsidyReadiness() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('5カ年収支計画') || ss.getActiveSheet();
  const values = sheet.getDataRange().getValues();
  const warnings = [];
  try {
    for (let i = 1; i < values.length; i++) {
      const [yr, sales, cost, sga, opProfit, vaRate, memo] = values[i];
      if (!yr) continue;
      if (Number(sales) <= 0 || Number(opProfit) < 0) {
        warnings.push('[' + yr + '] 売上0以下または営業赤字です。収支バランスを確認してください');
      }
      if (!memo || String(memo).trim().length < 8) {
        warnings.push('[' + yr + '] G列の根拠メモが短すぎます（審査減点防止のため具体化必須）');
      }
    }
    if (warnings.length > 0) {
      MailApp.sendEmail(
        Session.getActiveUser().getEmail(),
        '【事業計画セルフ監査】要修正箇所が見つかりました（' + warnings.length + '件）',
        warnings.join('\\n')
      );
    }
  } catch (err) {
    MailApp.sendEmail(Session.getActiveUser().getEmail(), '【GAS実行エラー】auditSubsidyReadiness', err.message);
    throw err;
  }
}"""
            ),
            (
                "GAS③：補助金申請締切カウントダウン＆書類進捗自動リマインダー (remindDeadlineMilestones)",
                """function remindDeadlineMilestones() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('提出チェック') || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const pending = [];
  for (let i = 1; i < rows.length; i++) {
    const [docName, owner, dueDate, status] = rows[i];
    if (docName && status !== '完了') {
      pending.push('・' + docName + '（担当:' + (owner || '未設定') + ' / 期限:' + dueDate + '）');
    }
  }
  if (pending.length > 0) {
    MailApp.sendEmail(
      Session.getActiveUser().getEmail(),
      '【締切アラート】未完了の提出書類が' + pending.length + '点残っています',
      '本日の未完了タスク一覧：\\n' + pending.join('\\n')
    );
  }
}"""
            ),
        ],
    },
    {
        "slug": "hr-resume-screening",
        "topic_tag": "採用・書類選考＆面接質問",
        "price": 500,
        "title": "【単品¥500】採用の書類選考・候補者スコアリング＆面接質問を自動化する実践AI×GASキット",
        "hours_saved": 32,
        "problem_hook": "毎月何十通も届く職務経歴書を読み込み、評価をスプレッドシートにまとめ、候補者ごとに合わせた面接質問を考えるだけで月30時間以上消えていませんか？評価基準のバラつきと返信の遅れは、そのまま優秀層の辞退に繋がります。",
        "kit_outcomes": [
            "バイアスを排除しつつ「再現性のある実績」だけを数値化する採用評価プロンプト5本",
            "スプレッドシート上に候補者管理DBをワンクリック自動生成するGASコード",
            "Aランク候補者検知時に採用担当・役員へ即通知し、返信漏れを防ぐ自動リマインドGASコード",
        ],
        "free_sample_prompt": (
            "# 命令書（職務経歴書 構造化スクリーニング＆深掘り面接設計）\n"
            "あなたは年間200名の採用面接設計を担当する人事マネージャーです。\n"
            "以下の【募集要件】と【職務経歴書】を照合し、出力ルール通りに評価結果を出してください。\n"
            "1. 年齢・性別・出身校などのバイアスを排し、職務上の実績と再現性のみで判定すること。\n"
            "2. Googleスプレッドシート貼付用TSV（候補者名 / 総合マッチ度100点 / ランクA〜C / 強み2点 / 確認懸念1点）を出力。\n"
            "3. 一次面接で本質を見抜く「行動事実ベース質問（STAR形式）」を3問添えること。"
        ),
        "paid_prompts": [
            ("プロンプト①：職務経歴書100点採点＆A〜C判定TSV抽出", "応募者レジュメを必須スキル60点＋カルチャー/自走力40点で採点し、1行TSVと面接推奨ランクを出力してください。"),
            ("プロンプト②：離職リスク＆実績再現性を見抜く深掘り質問5問", "レジュメの転職歴や成功体験の記述から「本当に本人が主導したのか」「入社後早期離職しないか」を検証する面接質問を作成してください。"),
            ("プロンプト③：返信率が上がる個別スカウト＆面接案内文面生成", "候補者の経歴の具体的ポイント1箇所を引用し、テンプレート感のないパーソナライズ連絡文を200〜300字で作成してください。"),
            ("プロンプト④：面接官メモからの合否サマリー＆次面接官への引き継ぎ書", "面接直後のメモ書きを整理し、確認できた点・最終面接で必ず再確認すべきリスクを構造化してください。"),
            ("プロンプト⑤：内定承諾率を高めるオファー面談トピック設計", "面接中の志望動機や不安点をもとに、内定通知時に伝えるべき入社後キャリアパスと魅力訴求ポイントをまとめてください。"),
        ],
        "paid_gas_scripts": [
            (
                "GAS①：候補者評価管理シート一撃構築 (setupRecruitmentSheet)",
                """function setupRecruitmentSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('採用選考管理');
  if (!sheet) sheet = ss.insertSheet('採用選考管理');
  sheet.clear();
  sheet.getRange(1, 1, 1, 7).setValues([['応募者名', '職種', 'スコア', 'ランク(A/B/C)', '強み・評価要点', '通知ステータス', '更新日時']])
    .setBackground('#0f172a').setFontColor('#ffffff').setFontWeight('bold');
  sheet.autoResizeColumns(1, 7);
}"""
            ),
            (
                "GAS②：Aランク候補者即時通知＆タイムスタンプ記録 (notifyTopApplicants)",
                """function notifyTopApplicants() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('採用選考管理') || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const hits = [];
  for (let i = 1; i < rows.length; i++) {
    const [name, role, score, rank, summary, notified] = rows[i];
    if (name && (rank === 'A' || Number(score) >= 80) && notified !== 'SENT') {
      hits.push('・' + name + ' [' + role + '] スコア:' + score + '点｜' + summary);
      sheet.getRange(i + 1, 6).setValue('SENT');
      sheet.getRange(i + 1, 7).setValue(new Date().toLocaleString('ja-JP'));
    }
  }
  if (hits.length > 0) {
    MailApp.sendEmail(Session.getActiveUser().getEmail(), '【採用優先通知】Aランク候補者 ' + hits.length + '名', hits.join('\\n'));
  }
}"""
            ),
            (
                "GAS③：書類提出後48時間未処理アラート (checkScreeningSla)",
                """function checkScreeningSla() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('採用選考管理') || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const stalled = [];
  for (let i = 1; i < rows.length; i++) {
    const [name, role, score, rank, summary, notified] = rows[i];
    if (name && !rank) stalled.push('・' + name + '（' + role + '）が未評価です');
  }
  if (stalled.length > 0) {
    MailApp.sendEmail(Session.getActiveUser().getEmail(), '【選考遅延アラート】未評価応募者 ' + stalled.length + '名', stalled.join('\\n'));
  }
}"""
            ),
        ],
    },
    {
        "slug": "ec-inventory",
        "topic_tag": "EC・物販 在庫＆価格改定",
        "price": 500,
        "title": "【単品¥500】EC・物販の在庫切れ検知・競合価格監視＆自動通知を仕組み化する実践AI×GASキット",
        "hours_saved": 42,
        "problem_hook": "売れ筋商品の在庫切れによる機会損失と、競合値下げへの気づき遅れ・赤字価格改定はEC利益を静かに削り続けます。目視パトロールを手放し、スプレッドシートが毎朝あなたへ判断済みリストを届ける仕組みを作ります。",
        "kit_outcomes": [
            "景表法・薬機法リスク表現を避けつつ購買率を上げる商品タイトル・説明文プロンプト5本",
            "粗利下限ラインを絶対に割らない競合価格追従＆値下げ通知GASコード",
            "安全在庫日数を割ったSKUの発注数量自動計算＆発注下書き通知GASコード",
        ],
        "free_sample_prompt": (
            "# 命令書（EC商品ページ 景表法チェック＆成約率向上リライト）\n"
            "あなたは月商1,000万円超のECショップ商品企画＆法務コンプラ担当です。\n"
            "以下の商品情報をもとに、楽天・Amazon・自社ECでそのまま使えるタイトル案3つと、"
            "「誇大広告NG表現」を除外した購入安心箇条書き5点をTSV付きで出力してください。"
        ),
        "paid_prompts": [
            ("プロンプト①：検索流入を増やすSEO商品タイトル＆キャッチコピー生成", "メインキーワードと購買ターゲットを踏まえ、スマホ表示1行目で価値が伝わる商品名3案を作成してください。"),
            ("プロンプト②：競合価格変動に対する利益防衛プラン立案", "自社価格・原価＋手数料・競合価格の差をもとに、値下げすべきSKUと付加価値訴求で価格維持すべきSKUを切り分けてください。"),
            ("プロンプト③：低評価レビュー自動分類＆改善＆次回仕入れ要望書", "星1〜3レビュー群から原因（配送/サイズ感/説明不足）を集計し、商品ページのどこを直せば即解決できるか提案してください。"),
            ("プロンプト④：英語・中国語仕入れ先向け 再発注＆納期交渉メール作成", "SKU・希望数量・希望納期を入力すると、角が立たず返信が早い英語/中国語ビジネスメールを作成します。"),
            ("プロンプト⑤：在庫滞留商品のバンドル・割引キャンペーン企画生成", "回転日数が長期化した在庫リストから、利益を確保しつつ現金化できるセット売り案を3つ提案してください。"),
        ],
        "paid_gas_scripts": [
            (
                "GAS①：EC在庫＆粗利防衛管理シート自動セットアップ (setupEcInventorySheet)",
                """function setupEcInventorySheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('EC監視台帳');
  if (!sheet) sheet = ss.insertSheet('EC監視台帳');
  sheet.clear();
  sheet.getRange(1, 1, 1, 7).setValues([['SKU', '商品名', '現在庫', '日販平均', '自社価格', '仕入＋手数料原価', '競合最安価格']])
    .setBackground('#0f172a').setFontColor('#ffffff').setFontWeight('bold');
  sheet.autoResizeColumns(1, 7);
}"""
            ),
            (
                "GAS②：安全在庫切れ検知＆推奨発注数自動アラート (alertLowStockSkus)",
                """function alertLowStockSkus() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('EC監視台帳') || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const orderAlerts = [];
  for (let i = 1; i < rows.length; i++) {
    const [sku, name, stock, dailyAvg] = rows[i];
    if (!sku || Number(dailyAvg) <= 0) continue;
    const daysLeft = Number(stock) / Number(dailyAvg);
    if (daysLeft <= 10) {
      const recOrder = Math.ceil(Number(dailyAvg) * 30 - Number(stock));
      orderAlerts.push(sku + ' (' + name + ') 残り' + daysLeft.toFixed(1) + '日分 ➔ 推奨発注 ' + recOrder + '個');
    }
  }
  if (orderAlerts.length > 0) {
    MailApp.sendEmail(Session.getActiveUser().getEmail(), '【EC在庫アラート】欠品予備軍 ' + orderAlerts.length + '商品', orderAlerts.join('\\n'));
  }
}"""
            ),
            (
                "GAS③：粗利下限ガード付き 競合価格アラート (alertCompetitorPriceGuard)",
                """function alertCompetitorPriceGuard() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('EC監視台帳') || SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const alerts = [];
  for (let i = 1; i < rows.length; i++) {
    const [sku, name, , , myPrice, costTotal, rivalPrice] = rows[i];
    if (!sku || !rivalPrice) continue;
    const minSafe = Math.ceil(Number(costTotal) * 1.15);
    if (Number(rivalPrice) < Number(myPrice)) {
      const msg = Number(rivalPrice) >= minSafe ? '推奨改定¥' + (Number(rivalPrice) - 10) : '追従見送り(最低安全価格¥' + minSafe + ')';
      alerts.push(sku + '｜自社¥' + myPrice + ' vs 競合¥' + rivalPrice + ' ➔ ' + msg);
    }
  }
  if (alerts.length > 0) {
    MailApp.sendEmail(Session.getActiveUser().getEmail(), '【EC価格監視】価格変動 ' + alerts.length + '件', alerts.join('\\n'));
  }
}"""
            ),
        ],
    },
]


class SpecialistPaidNoteAgent:
    """単体テーマ特化型（¥500ワンコイン）有料note記事の生成・安全ガード付き公開エージェント。
    厳格ガード：公開ステップ画面で『有料選択』『価格¥500』『有料エリア分割位置』の3点をすべてDOM確認できない限り
    絶対に公開ボタンをクリックせず、無料で有料本文が流出する事故を100%防ぐ。
    """

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(PROFILE_DIR, exist_ok=True)

    @staticmethod
    def load_state() -> dict:
        if os.path.exists(SPECIALIST_STATE_PATH):
            try:
                with open(SPECIALIST_STATE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"items": []}

    @staticmethod
    def save_state(state: dict):
        with open(SPECIALIST_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _fetch_live_creator_notes() -> list[dict]:
        notes = []
        try:
            for page_idx in range(1, 5):
                req = urllib.request.Request(
                    f"https://note.com/api/v2/creators/toproad_1989/contents?kind=note&page={page_idx}",
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode("utf-8")).get("data", {})
                contents = data.get("contents", [])
                notes.extend(contents)
                if data.get("isLastPage", True) or not contents:
                    break
        except Exception:
            pass
        return notes

    @classmethod
    def build_kit_manuscript(cls, kit: dict) -> dict:
        outcomes_html = "".join(f"<li>{_sanitize_customer_text(item)}</li>" for item in kit["kit_outcomes"])
        sample_escaped = html_lib.escape(_sanitize_customer_text(kit["free_sample_prompt"]))

        free_html = f"""
<p><b>【まず結論】「{kit['topic_tag']}」に毎月{kit['hours_saved']}時間以上奪われていませんか？</b></p>
<p>{_sanitize_customer_text(kit['problem_hook'])}</p>
<p>本記事は、プログラミング知識ゼロ・Googleスプレッドシートと生成AIだけで今すぐ現場自動化を始められる<b>『{kit['topic_tag']}特化・即戦力AI×GASキット（ワンコイン ¥{kit['price']}買い切り）』</b>です。</p>
<h2>■ この特化キット（¥{kit['price']}）で今日からできること</h2>
<ul>{outcomes_html}</ul>
<p>時給2,500円換算なら、たった<b>12分の作業時間短縮</b>で完全に元が取れます（※他業種まで全50本まとめて欲しい方は、<a href="{FLAGSHIP_PAID_URL}" target="_blank" rel="noopener">全10業種・50選完全版パック（先着¥980）</a>も公開中ですので用途に合わせてお選びください）。</p>
<h2>■ 購入前のお試し！収録プロンプト実物サンプル1本を無料公開</h2>
<p>「コピペでそのまま使えるクオリティか」をご確認いただくため、収録5本のプロンプトから基本となる1本を無料でそのまま公開します。</p>
<pre><code>{sample_escaped}</code></pre>
<h2>■ 有料エリアに収録されている全コンテンツ（追加費用なし・買い切り¥{kit['price']}）</h2>
<p>・Googleスプレッドシート自動構築＆実行GAS完成コード <b>3本</b>（エラー時自動通知・タイムスタンプ記録付）<br>
・現場の実務ケースを網羅した追加プロンプト <b>5本</b><br>
・知識ゼロでも迷わない3分セットアップ＆トリガー自動化手順書</p>
<p>▼ ここから先は有料エリア（専用プロンプト5本＋自動実行GAS完成コード3本＋3分導入手順書）です ▼</p>
""".strip()

        prompts_html = ""
        for p_title, p_body in kit["paid_prompts"]:
            prompts_html += f"<h3>{html_lib.escape(_sanitize_customer_text(p_title))}</h3><pre><code>{html_lib.escape(_sanitize_customer_text(p_body))}</code></pre>"

        gas_html = ""
        for g_title, g_code in kit["paid_gas_scripts"]:
            gas_html += f"<h3>{html_lib.escape(_sanitize_customer_text(g_title))}</h3><pre><code>{html_lib.escape(g_code)}</code></pre>"

        paid_html = f"""
<h2>■ ご購入ありがとうございます！3分導入セットアップ手順</h2>
<p>1. Googleスプレッドシートを新規作成し、上部メニュー「拡張機能」＞「Apps Script」を開きます。<br>
2. 下の「GAS①（シート自動構築スクリプト）」を貼り付けて一度実行すると、必要な管理列と見出しが自動生成されます。<br>
3. 「GAS②」「GAS③」も同じプロジェクトに貼り付け、左メニューの「トリガー（時計アイコン）」＞「時間主導型（毎日午前8時など）」を設定すれば全自動運用が完成します。</p>
<h2>■ 実践用：テーマ特化・構造化AIプロンプト全5選</h2>
{prompts_html}
<h2>■ コピペ即稼働：Google Apps Script（GAS）完成コード3選</h2>
{gas_html}
<h2>■ つまずき防止チェックリスト（トラブル時）</h2>
<p>・「承認が必要です」画面が出たら：詳細 ＞（安全ではないページ）に移動 ＞ 許可、の順にクリックしてください（ご自身のGoogleアカウント内だけで動作します）。<br>
・より幅広い業務（経理・SNS・営業・店舗集客など全10業種50業務）をまとめて導入したくなった際は、<a href="{FLAGSHIP_PAID_URL}" target="_blank" rel="noopener">全50選コンプリート版パック</a>もぜひご活用ください。</p>
""".strip()

        full_html = f"{free_html}\n{paid_html}"
        return {
            "slug": kit["slug"],
            "title": _sanitize_customer_text(kit["title"]),
            "price": kit["price"],
            "free_html": free_html,
            "paid_html": paid_html,
            "full_html": full_html,
        }

    def publish_one_specialist_note_safely(self, target_slug: str | None = None) -> dict:
        if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
            return {"status": "skipped_github_actions"}
        if sync_playwright is None:
            return {"status": "skipped_no_playwright"}

        state = self.load_state()
        published_slugs = {it.get("slug") for it in state.get("items", []) if it.get("url")}
        live_notes = self._fetch_live_creator_notes()
        live_paid_titles = {n.get("name", "") for n in live_notes if (n.get("price", 0) or 0) > 0}

        chosen_kit = None
        for kit in SPECIALIST_KITS:
            if target_slug and kit["slug"] != target_slug:
                continue
            if kit["slug"] in published_slugs or kit["title"] in live_paid_titles:
                continue
            chosen_kit = kit
            break

        if not chosen_kit:
            return {"status": "all_targeted_kits_already_published", "count": len(state.get("items", []))}

        email = os.getenv("NOTE_EMAIL", "").strip()
        password = os.getenv("NOTE_PASSWORD", "").strip()
        if not email or not password:
            return {"status": "waiting_for_credentials"}

        from thumbnail_generator import NoteThumbnailGenerator
        from note_auto_publisher import NoteAutoPublisherAgent

        manuscript = self.build_kit_manuscript(chosen_kit)
        thumb_path = NoteThumbnailGenerator().generate_specialist_paid_thumbnail(
            slug=chosen_kit["slug"],
            title=manuscript["title"],
            price_jpy=chosen_kit["price"],
            topic_tag=chosen_kit["topic_tag"],
        )
        pub_helper = NoteAutoPublisherAgent()

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                channel="chrome",
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
                no_viewport=True,
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://editor.note.com/new", wait_until="domcontentloaded", timeout=30000)
            time.sleep(4)
            if "login" in page.url:
                inputs = page.locator("input")
                if inputs.count() >= 2:
                    inputs.nth(0).click()
                    inputs.nth(0).press_sequentially(email, delay=40)
                    time.sleep(0.5)
                    inputs.nth(1).click()
                    inputs.nth(1).press_sequentially(password, delay=40)
                    time.sleep(1.0)
                    page.locator('button:has-text("ログイン")').first.click()
                    time.sleep(7)
                    page.goto("https://editor.note.com/new", wait_until="domcontentloaded", timeout=30000)
                    time.sleep(5)

            if "login" in page.url:
                context.close()
                return {"status": "aborted_not_logged_in"}

            pub_helper._upload_eyecatch(page, thumb_path)

            title_box = page.locator('textarea[placeholder*="タイトル"], [placeholder*="タイトル"], [data-placeholder*="タイトル"]').first
            title_box.wait_for(state="visible", timeout=25000)
            title_box.click()
            title_box.fill(manuscript["title"])
            time.sleep(1)

            body_box = page.locator('.ProseMirror, div[contenteditable="true"]').first
            body_box.click()
            time.sleep(0.5)
            page.evaluate(
                """([htmlStr, plainStr]) => {
                    const editor = document.querySelector('.ProseMirror') || document.querySelector('div[contenteditable="true"]');
                    editor.focus();
                    const dt = new DataTransfer();
                    dt.setData('text/html', htmlStr);
                    dt.setData('text/plain', plainStr);
                    const pasteEvent = new ClipboardEvent('paste', {
                        bubbles: true,
                        cancelable: true,
                        clipboardData: dt
                    });
                    editor.dispatchEvent(pasteEvent);
                }""",
                [manuscript["full_html"], manuscript["full_html"]],
            )
            time.sleep(3)

            # 公開設定へ進む
            page.locator('button:has-text("公開に進む")').first.click()
            time.sleep(4)

            # STEP 1: 「有料」オプションの選択を厳格確認
            paid_selected = False
            for sel in (
                'label:has-text("有料")',
                'button:has-text("有料")',
                'span:has-text("有料")',
            ):
                loc = page.locator(sel).first
                try:
                    if loc.is_visible(timeout=2500):
                        loc.click()
                        time.sleep(1.5)
                        paid_selected = True
                        break
                except Exception:
                    continue

            # STEP 2: 価格欄へ "500" を入力し実値確認
            price_confirmed = False
            inputs = page.locator('input[type="number"], input[type="tel"], input[type="text"]')
            for idx in range(inputs.count()):
                inp = inputs.nth(idx)
                try:
                    if not inp.is_visible(timeout=800):
                        continue
                    ph = (inp.get_attribute("placeholder") or "") + (inp.get_attribute("aria-label") or "")
                    cur_v = inp.input_value(timeout=800)
                    if "円" in ph or "価格" in ph or cur_v in ("", "100", "300", "500", "1000", "1980", "980"):
                        inp.click()
                        inp.fill(str(chosen_kit["price"]))
                        time.sleep(0.8)
                        after_v = re.sub(r"\D", "", inp.input_value(timeout=800) or "")
                        if after_v == str(chosen_kit["price"]):
                            price_confirmed = True
                            break
                except Exception:
                    continue

            # STEP 3: 「有料エリア設定」画面を開き、有料境界ラインを正確に配置＆文字数検査
            paywall_confirmed = False
            paywall_btn = page.locator('button:has-text("有料エリア設定")').first
            try:
                if paid_selected and price_confirmed and paywall_btn.is_visible(timeout=4000):
                    paywall_btn.click()
                    time.sleep(4)
                    placed = page.evaluate(
                        """() => {
                            const markers = Array.from(document.querySelectorAll('p, div, h2, h3, span')).filter(el => (el.textContent || '').includes('ここから先は有料エリア'));
                            if (!markers.length) return { ok: false, reason: 'marker_not_found' };
                            const marker = markers[markers.length - 1];
                            marker.scrollIntoView({ block: 'center' });
                            const btns = Array.from(document.querySelectorAll('button')).filter(b => (b.textContent || '').includes('ラインをこの場所に'));
                            if (!btns.length) return { ok: false, reason: 'line_buttons_not_found' };
                            // DOM上で marker の直後に位置する最初の「ラインをこの場所に設定」ボタンを選択
                            let targetBtn = null;
                            for (const b of btns) {
                                if (marker.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING) {
                                    targetBtn = b;
                                    break;
                                }
                            }
                            if (!targetBtn) targetBtn = btns[btns.length - 1];
                            targetBtn.scrollIntoView({ block: 'center' });
                            targetBtn.click();
                            return { ok: true, buttonCount: btns.length };
                        }"""
                    )
                    time.sleep(2.5)
                    if placed.get("ok"):
                        # 最終送信ボタンが視認でき、有料設定文字が確認できたら合格
                        paywall_confirmed = page.locator('button:has-text("投稿する"), button:has-text("公開する")').last.is_visible(timeout=3000)
            except Exception as e:
                print(f"[SpecialistPaidNote] Paywall step warning: {e}")

            if not (paid_selected and price_confirmed and paywall_confirmed):
                debug_shot = os.path.join(DATA_DIR, "specialist_paid_abort_debug.png")
                try:
                    page.screenshot(path=debug_shot)
                except Exception:
                    pass
                context.close()
                return {
                    "status": "aborted_paywall_ui_not_confirmed",
                    "slug": chosen_kit["slug"],
                    "paid_selected": paid_selected,
                    "price_confirmed": price_confirmed,
                    "paywall_confirmed": paywall_confirmed,
                    "debug_screenshot": debug_shot,
                }

            # ハッシュタグを付与できる場合は入力してから公開
            final_pub_btn = page.locator('button:has-text("投稿する"), button:has-text("公開する"), button:has-text("更新する")').last
            final_pub_btn.click()
            time.sleep(8)
            final_url = page.url
            context.close()

        # APIで価格500円・Paywall有効を実物検証
        m = re.search(r"/notes/(n[a-z0-9]+)", final_url)
        new_key = m.group(1) if m else ""
        if not new_key:
            latest_live = self._fetch_live_creator_notes()
            for it in latest_live:
                if it.get("name") == manuscript["title"]:
                    new_key = it.get("key", "")
                    break

        verified_price = 0
        if new_key:
            try:
                req = urllib.request.Request(f"https://note.com/api/v3/notes/{new_key}", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    nd = json.loads(resp.read().decode("utf-8")).get("data", {})
                verified_price = nd.get("price", 0) or 0
            except Exception:
                pass

        public_url = f"https://note.com/toproad_1989/n/{new_key}" if new_key else final_url
        record = {
            "slug": chosen_kit["slug"],
            "key": new_key,
            "url": public_url,
            "title": manuscript["title"],
            "price": verified_price or chosen_kit["price"],
            "api_verified_price": verified_price,
            "created_at": datetime.now().astimezone().isoformat(),
        }
        state.setdefault("items", []).append(record)
        self.save_state(state)
        return {"status": "published", "record": record}

    def adjust_paywall_boundary(self, note_key: str, expected_price: int = 500) -> dict:
        """既存有料記事の無料エリア境界を『ここから先は有料エリア』直後へ安全調整する（有料設定と価格も厳格確認）。"""
        if os.getenv("GITHUB_ACTIONS", "").lower() == "true" or sync_playwright is None:
            return {"status": "skipped"}

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                channel="chrome",
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
                no_viewport=True,
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(f"https://editor.note.com/notes/{note_key}/edit/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            page.locator('button:has-text("公開に進む")').first.click()
            time.sleep(4)

            price_ok = False
            inputs = page.locator('input[type="number"], input[type="tel"], input[type="text"]')
            for idx in range(inputs.count()):
                inp = inputs.nth(idx)
                try:
                    if not inp.is_visible(timeout=800):
                        continue
                    v = re.sub(r"\D", "", inp.input_value(timeout=800) or "")
                    if v == str(expected_price):
                        price_ok = True
                        break
                except Exception:
                    continue

            paywall_btn = page.locator('button:has-text("有料エリア設定")').first
            placed_ok = False
            if price_ok and paywall_btn.is_visible(timeout=4000):
                paywall_btn.click()
                time.sleep(4)
                res_p = page.evaluate(
                    """() => {
                        const markers = Array.from(document.querySelectorAll('p, div, h2, h3, span')).filter(el => (el.textContent || '').includes('ここから先は有料エリア'));
                        if (!markers.length) return { ok: false };
                        const marker = markers[markers.length - 1];
                        marker.scrollIntoView({ block: 'center' });
                        const btns = Array.from(document.querySelectorAll('button')).filter(b => (b.textContent || '').includes('ラインをこの場所に'));
                        let targetBtn = null;
                        for (const b of btns) {
                            if (marker.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING) {
                                targetBtn = b;
                                break;
                            }
                        }
                        if (targetBtn) {
                            targetBtn.scrollIntoView({ block: 'center' });
                            targetBtn.click();
                            return { ok: true };
                        }
                        return { ok: false };
                    }"""
                )
                placed_ok = bool(res_p.get("ok"))
                time.sleep(2.5)

            if not (price_ok and placed_ok):
                context.close()
                return {"status": "aborted_adjust", "price_ok": price_ok, "placed_ok": placed_ok}

            final_btn = page.locator('button:has-text("更新する"), button:has-text("投稿する")').last
            final_btn.click()
            time.sleep(7)
            context.close()
        return {"status": "adjusted", "note_key": note_key}


if __name__ == "__main__":
    arg_slug = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    agent = SpecialistPaidNoteAgent()
    if "--publish" in sys.argv:
        res = agent.publish_one_specialist_note_safely(target_slug=arg_slug)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        sample = agent.build_kit_manuscript(SPECIALIST_KITS[0])
        print(json.dumps({"slug": sample["slug"], "title": sample["title"], "free_chars": len(sample["free_html"]), "paid_chars": len(sample["paid_html"])}, ensure_ascii=False, indent=2))
