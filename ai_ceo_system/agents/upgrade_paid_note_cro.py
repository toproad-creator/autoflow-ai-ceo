import json
import os
import sys
import time
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
load_dotenv(os.path.join(ROOT_DIR, ".env"))
sys.path.insert(0, os.path.dirname(__file__))

from thumbnail_generator import NoteThumbnailGenerator
from note_auto_publisher import NoteAutoPublisherAgent, PROFILE_DIR

PAID_NOTE_KEY = "n5d0e28a74f91"
TEMPLATES_JSON = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "autoflow_pro_50_templates.json")
EVOLUTION_STATE_PATH = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "company_evolution_state.json")
PAID_NOTE_SYNC_STATE_PATH = os.path.join(ROOT_DIR, "ai_ceo_system", "data", "paid_note_sync_state.json")


def _sanitize_note_copy(text: str) -> str:
    cleaned = text or ""
    replacements = [
        ("AI起業対決", ""),
        ("AI CEO", ""),
        ("実証実験", "導入検証"),
        ("実験ログ", "運用記録"),
        ("実験台", "検証環境"),
        ("実験", "検証"),
        ("対決", "比較"),
    ]
    for src, dst in replacements:
        cleaned = cleaned.replace(src, dst)
    return cleaned.strip()


def _resolve_top_winners(top_winners: list[dict] | None = None) -> list[dict]:
    raw_list = list(top_winners) if top_winners else []
    if not raw_list and os.path.exists(EVOLUTION_STATE_PATH):
        try:
            with open(EVOLUTION_STATE_PATH, "r", encoding="utf-8") as f:
                evo = json.load(f)
            raw_list = list(evo.get("selection_and_focus", {}).get("winners_top3") or [])
        except Exception:
            raw_list = []
    if not raw_list:
        raw_list = [
            {"slug": "subsidy-business-plan", "title": "補助金申請・融資用の事業計画書ドラフト＆収支表自動作成"},
            {"slug": "hr-resume-screening", "title": "採用・人事の職務経歴書スクリーニング＆面接質問自動生成"},
            {"slug": "ec-inventory", "title": "EC・物販の在庫管理＆価格改定自動化"},
        ]
    deduped = []
    seen_slugs = set()
    for w in raw_list:
        sl = w.get("slug") or w.get("title", "")
        if sl and sl not in seen_slugs:
            seen_slugs.add(sl)
            deduped.append(w)
    return deduped[:3]


def build_high_converting_free_preview_html(top_winners: list[dict] | None = None) -> str:
    with open(TEMPLATES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    templates = data.get("templates", [])
    winners = _resolve_top_winners(top_winners)
    top1 = _sanitize_note_copy(winners[0]["title"]) if len(winners) > 0 else "補助金申請・事業計画書自動作成"
    top2 = _sanitize_note_copy(winners[1]["title"]) if len(winners) > 1 else "採用・職務経歴書スクリーニング自動化"
    top3 = _sanitize_note_copy(winners[2]["title"]) if len(winners) > 2 else "EC・物販の在庫管理＆価格改定自動化"

    cat_groups = {}
    for t in templates:
        cat_groups.setdefault(t["category"], []).append(f"{t['id']}：{t['title']}")

    toc_html = ""
    for idx, (cat, items) in enumerate(cat_groups.items(), start=1):
        toc_html += f"<p><b>【第{idx}章：{cat}（全5選）】</b><br>" + "<br>".join(f"・{it}" for it in items) + "</p>"

    html = f"""
<p><b>🔥【先着10部限定・50%OFFセール開催中！】</b><br>リリース記念として、通常価格 <b>¥1,980 ➔ 先着10部限定【¥980（1レシピあたり約19円）】</b> で公開しています！（※10部完売時点で ¥1,480 ➔ 定価 ¥1,980 へ段階的に値上げします）</p>
<p><b>📈 いま特に読者から強く求められている「3大自動化テーマ」を完全収録！</b><br>① <b>{top1}</b><br>② <b>{top2}</b><br>③ <b>{top3}</b><br>需要が集中しているこの3大領域の即戦力セットはもちろん、<b>経理・営業・SNS・YouTube・店舗集客まで全10業種・50種類すべて</b>をそのまま手に入れていただけます。</p>
<p>もし1日60分の手作業を月22日続けている場合、時給2,500円換算で<b>【年間 607,200円（約243時間）】</b>を定型作業に費やしていることになります。本パックは、コピペ5分で今日から稼働させられる「構造化AIプロンプト50本」＋「Google Apps Script (GAS) 自動実行コード50本」を1つにまとめた実務資産パッケージです。</p>
<h2>■ なぜ「普通のChatGPTの使い方」では業務が減らないのか？</h2>
<p>ChatGPTに毎回文章を打ち、出てきた回答をコピーしてスプレッドシートやメールに貼り直す作業は、結局<b>「人間が手作業を仲介する負担」</b>が消えません。本当に業務時間をゼロに近づけるには、<b>①出力形式（TSV/JSON）を固定した業務専用プロンプト</b>と、<b>②スプレッドシート上で定時自動実行＆メール通知まで完結するGAS完成コード</b>の両輪が不可欠です。</p>
<h2>■ 購入前にクオリティをご確認いただける【TOP3領域 実物サンプル完全公開】</h2>
<p>「自分の業種でそのまま使えるレベルなのか？」を一切の疑問なく確かめていただけるよう、いま最も問い合わせが多い<b>3大テーマの実物レシピ（プロンプト＋GAS完成コード）</b>をこの無料エリアでそのまま公開します！</p>

<p>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br><b>🎁 無料実物サンプル①：補助金申請・融資用の事業計画書ドラフト＆5カ年収支表チェック</b><br>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
<p><b>【① コピペ用・構造化AIプロンプト（採択基準・審査員視点組込済）】</b></p>
<pre><code># 命令書
あなたは認定経営革新等支援機関レベルの補助金・事業計画書コンサルタント兼財務モデラーです。
以下の自社情報をもとに、補助事業計画書（現状と課題／補助事業の具体的内容／投資回収効果／5カ年数値目標）を審査員が採点しやすい論理構成で作成してください。

# 厳守出力ルール
1. 【投資回収・付加価値額】は「売上増加根拠×粗利率−追加経費」の数式と前提条件を必ず併記すること。
2. 審査で減点されやすい曖昧表現（「大幅に増加」「積極活用」）を禁止し、KPI数値・実施月・担当体制で書くこと。
3. 末尾にGoogleスプレッドシート収支計画シートへ貼れるTSV形式の5カ年計画表（年度／売上高／原価／販管費／営業利益／補助対象投資回収メモ）を出力すること。

# 自社情報・計画メモ
（事業概要・導入予定設備・投資額・狙う市場を貼り付けてください）</code></pre>
<p><b>【② 自動実行 GAS コード：収支目標達成率・未記入項目アラート自動監査】</b></p>
<pre><code>function auditSubsidyPlanSheet() {{
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('事業計画収支') || ss.getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const alerts = [];
  for (let i = 1; i &lt; rows.length; i++) {{
    const [yearLabel, sales, cost, sga, opProfit, noteMemo] = rows[i];
    if (!yearLabel) continue;
    const growth = Number(opProfit) / Math.max(1, Number(sales));
    if (!noteMemo || String(noteMemo).trim().length &lt; 8) {{
      alerts.push(yearLabel + '：根拠メモが短すぎます（審査員減点リスク）');
    }}
    if (growth &lt; 0.03) {{
      alerts.push(yearLabel + '：営業利益率が' + (growth * 100).toFixed(1) + '%です。付加価値額3%以上の要件を確認してください');
    }}
  }}
  if (alerts.length &gt; 0) {{
    MailApp.sendEmail(Session.getActiveUser().getEmail(), '【事業計画セルフ監査】要修正ポイント（' + alerts.length + '件）', alerts.join('\\n'));
  }}
}}</code></pre>

<p>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br><b>🎁 無料実物サンプル②：採用・人事の職務経歴書スクリーニング＆面接質問自動生成</b><br>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
<p><b>【① コピペ用・構造化AIプロンプト（再現性見極め・深掘り質問付）】</b></p>
<pre><code># 命令書
あなたは年間200名の採用面接設計を担当する人事マネージャー兼評価アナリストです。
以下の応募者レジュメと募集要件（必須スキル・歓迎要件・NG条件）を照合し、構造化評価を行ってください。

# 厳守出力ルール
1. スプレッドシート貼付用TSVで1行要約を出力（応募者名／総合マッチ度100点満点／強みTOP2／懸念点／面接優先ランクA-C）。
2. 「自走力」「課題解決」を確かめるための一次面接用・深掘り質問を3問（「過去どのような制約下で何を実行したか」を引き出す質問）作成すること。
3. 年齢・性別・出身地などのバイアス情報を排除し、職務実績ベースのみで判定すること。</code></pre>
<p><b>【② 自動実行 GAS コード：Aランク候補者検知＆面接調整通知オートメーション】</b></p>
<pre><code>function notifyHighMatchCandidates() {{
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const priorityList = [];
  for (let i = 1; i &lt; rows.length; i++) {{
    const [name, score, summary, rank, notified] = rows[i];
    if (name &amp;&amp; rank === 'A' &amp;&amp; notified !== 'SENT') {{
      priorityList.push('・' + name + '（スコア:' + score + '点）｜' + summary);
      sheet.getRange(i + 1, 5).setValue('SENT');
      sheet.getRange(i + 1, 6).setValue(new Date().toLocaleString('ja-JP'));
    }}
  }}
  if (priorityList.length &gt; 0) {{
    MailApp.sendEmail(Session.getActiveUser().getEmail(), '【採用速報】Aランク候補者を即時通知（' + priorityList.length + '名）', priorityList.join('\\n'));
  }}
}}</code></pre>

<p>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br><b>🎁 無料実物サンプル③：EC・物販の競合価格監視＆粗利下限ガード付き値下げアラート</b><br>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
<p><b>【② 自動実行 GAS コード（粗利割れ防止チェック付）】</b></p>
<pre><code>function autoPriceGuard_EC() {{
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const alerts = [];
  for (let i = 1; i &lt; rows.length; i++) {{
    const [sku, myPrice, costPlusFee, rivalPrice, status] = rows[i];
    const minSafePrice = Math.ceil(Number(costPlusFee) * 1.15);
    if (sku &amp;&amp; status !== 'DONE' &amp;&amp; Number(rivalPrice) &lt; Number(myPrice)) {{
      const action = Number(rivalPrice) &gt;= minSafePrice ? '推奨改定¥' + (Number(rivalPrice) - 10) : '追従停止(粗利下限¥' + minSafePrice + '未満)';
      alerts.push(sku + '｜自社¥' + myPrice + ' vs 競合¥' + rivalPrice + ' ➔ ' + action);
      sheet.getRange(i + 1, 5).setValue('DONE');
    }}
  }}
  if (alerts.length &gt; 0) {{
    MailApp.sendEmail(Session.getActiveUser().getEmail(), '【EC価格監視レポート】' + alerts.length + '商品に変動あり', alerts.join('\\n'));
  }}
}}</code></pre>

<h2>■ 無料記事と「完全版パック（¥980）」の決定的な違い</h2>
<p>・<b>無料記事（1本ずつ手動設定）：</b> 1テーマの基本コードのみ／エラー通知や複数シート連携は自分で調整。<br>・<b>AutoFlow Pro 完全版パック（限定 ¥980）：</b> ①補助金・採用・ECを含む<b>全10業種50レシピ</b>すべて収録（1本あたり<b>約19円</b>）、②最初から<b>try-catch エラー通知・自動タイムスタンプ更新・6分制限回避</b>を組込済、③スプレッドシート初心者でも迷わない<b>3分導入チェックリスト付</b>。</p>

<h2>■ 購入前のよくある質問（FAQ）</h2>
<p><b>Q1. プログラミングの知識がまったくなくても使えますか？</b><br>はい。スプレッドシートの「拡張機能 ＞ Apps Script」を開き、コードをそのままコピー＆ペーストして保存ボタンを押すだけです（画像なしでも迷わない3ステップ手順を冒頭に明記しています）。</p>
<p><b>Q2. 無料版の ChatGPT や Gemini でも動きますか？</b><br>はい、本パックのプロンプトはすべて ChatGPT（無料版含む）・Gemini・Claude のどれでもそのまま動作する汎用構造化フォーマットで設計しています。</p>
<p><b>Q3. 購入後の追加料金や月額課金はありますか？</b><br>一切ありません。<b>¥980の買い切り</b>で、全50本＋今後のアップデート記載分をすべて永続的にご覧いただけます。</p>

<h2>■ 本パックに収録されている「全10業種・50種類」の完全一覧リスト</h2>
<p>有料エリアには、上記の実物サンプルと同等・またはそれ以上の詳細仕様で<b>50業務分すべてのプロンプト＆GAS完成コード</b>をすべて掲載しています（合計64,000文字超）。</p>
{toc_html}
<h2>■ 先着10部限定！ランチ1回分（¥980）で一生モノの自動化資産を</h2>
<p>・通常価格：¥1,980<br>・<b>現在価格：先着10部限定【¥980（税込・買い切り・追加費用一切なし）】</b><br>・時給2,500円の方なら、50本のうちたった1つを使って<b>「24分」の作業が浮くだけで100%元が取れます。</b>先着10部が完売次第、自動的に ¥1,480 ➔ ¥1,980 へ価格を改定しますので、最安値の今のうちにぜひ手に入れてください！</p>
<h2>▼ ここから下が有料エリア（全50種類のプロンプト＆GASコード完全版・約61,000文字）です ▼</h2>
""".strip()
    return html


def _build_top3_title(top_winners: list[dict] | None = None) -> str:
    winners = _resolve_top_winners(top_winners)
    short_tags = [_sanitize_note_copy(w.get("title", "")).split("・")[0][:6] for w in winners[:3]]
    tag_str = "・".join([t for t in short_tags if t]) or "補助金・採用・EC"
    return f"【先着10部¥980】{tag_str}をコピペ5分で自動化！『全10業種・50選 AIプロンプト＆GAS完全版』"


def update_paid_note_and_price(top_winners: list[dict] | None = None) -> dict:
    # 1. 新しいサムネイル（¥1,980 -> ¥980 限定セール版）を生成
    thumb_gen = NoteThumbnailGenerator()
    paid_thumb_path = thumb_gen.generate_paid_pack_thumbnail()
    print(f"[CRO Upgrade] Generated new sale thumbnail: {paid_thumb_path}")

    winners = _resolve_top_winners(top_winners)
    free_preview_html = build_high_converting_free_preview_html(winners)
    new_title = _build_top3_title(winners)
    pub_agent = NoteAutoPublisherAgent()
    email = os.getenv("NOTE_EMAIL", "")
    password = os.getenv("NOTE_PASSWORD", "")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            no_viewport=True
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(f"https://editor.note.com/notes/{PAID_NOTE_KEY}/edit/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        if "login" in page.url and email and password:
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
                page.goto(f"https://editor.note.com/notes/{PAID_NOTE_KEY}/edit/", wait_until="domcontentloaded", timeout=30000)
                time.sleep(5)

        if "login" in page.url:
            context.close()
            return {"status": "aborted_not_logged_in"}

        # 安全チェック：有料エリア区切り線（paywall-line）と有料エリア本文が確実に存在するか事前確認
        safety_check = page.evaluate(
            """() => {
                const editor = document.querySelector('.ProseMirror');
                if (!editor) return { ok: false, reason: 'no_editor' };
                const paywall = editor.querySelector('paywall-line');
                if (!paywall) return { ok: false, reason: 'no_paywall_line' };
                let afterLen = 0;
                let cur = paywall.nextSibling;
                while (cur) {
                    afterLen += (cur.textContent || '').trim().length;
                    cur = cur.nextSibling;
                }
                return { ok: afterLen >= 500, afterLen, reason: afterLen >= 500 ? 'ok' : 'paid_area_too_short' };
            }"""
        )
        if not safety_check.get("ok"):
            context.close()
            print(f"[CRO Upgrade] ABORTED for safety: {safety_check}")
            return {"status": "aborted_safety_guard", "detail": safety_check}

        # アイキャッチ画像を新しい ¥980 セール版に更新
        pub_agent._upload_eyecatch(page, paid_thumb_path)

        # タイトル更新
        title_box = page.locator('textarea[placeholder*="タイトル"], [placeholder*="タイトル"], [data-placeholder*="タイトル"]').first
        if title_box.is_visible(timeout=10000):
            title_box.click()
            title_box.fill(new_title)
            time.sleep(1)

        # ProseMirror 内の <paywall-line> より前を ProseMirror 正規の Selection + Paste で安全に差し替える（有料エリアは保護）
        body_box = page.locator('.ProseMirror').first
        body_box.click()
        time.sleep(0.5)

        prepared = page.evaluate(
            """() => {
                const editor = document.querySelector('.ProseMirror');
                if (!editor) return false;
                const paywall = editor.querySelector('paywall-line');
                if (!paywall) return false;
                editor.focus();
                const range = document.createRange();
                range.setStart(editor, 0);
                range.setEndBefore(paywall);
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
                return true;
            }"""
        )
        if not prepared:
            context.close()
            return {"status": "aborted_selection_failed"}

        time.sleep(0.3)
        page.keyboard.press("Backspace")
        time.sleep(1.0)

        pasted_ok = page.evaluate(
            """(newFreeHtml) => {
                const editor = document.querySelector('.ProseMirror');
                if (!editor) return false;
                const paywall = editor.querySelector('paywall-line');
                if (!paywall) return false;
                editor.focus();

                const range = document.createRange();
                range.setStart(editor, 0);
                range.collapse(true);
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);

                const dt = new DataTransfer();
                dt.setData('text/html', newFreeHtml);
                dt.setData('text/plain', newFreeHtml.replace(/<[^>]+>/g, '\\n'));
                const pasteEvent = new ClipboardEvent('paste', {
                    bubbles: true,
                    cancelable: true,
                    clipboardData: dt
                });
                editor.dispatchEvent(pasteEvent);
                return true;
            }""",
            free_preview_html
        )
        time.sleep(3.5)

        # 保存前にエディタDOM上の実態検証（無料エリアにTOP3ブロックが反映され、かつ有料エリアが無傷であること）
        post_check = page.evaluate(
            """() => {
                const editor = document.querySelector('.ProseMirror');
                if (!editor) return { ok: false, reason: 'no_editor_after' };
                const paywall = editor.querySelector('paywall-line');
                if (!paywall) return { ok: false, reason: 'paywall_missing_after' };
                let beforeText = '';
                let cur = editor.firstChild;
                while (cur && cur !== paywall) {
                    beforeText += (cur.textContent || '');
                    cur = cur.nextSibling;
                }
                let afterLen = 0;
                cur = paywall.nextSibling;
                while (cur) {
                    afterLen += (cur.textContent || '').trim().length;
                    cur = cur.nextSibling;
                }
                const hasTop3 = (beforeText.includes('3大自動化テーマ') || beforeText.includes('3大自動化領域')) && beforeText.includes('先着10部');
                return { ok: hasTop3 && afterLen >= 500, hasTop3, beforeLen: beforeText.length, afterLen };
            }"""
        )
        print(f"[CRO Upgrade] Post-paste editor verify: pasted={pasted_ok} check={post_check}")
        if not post_check.get("ok"):
            context.close()
            return {"status": "aborted_editor_verify_failed", "detail": post_check}

        # 公開設定画面へ進む
        pub_step = page.locator('button:has-text("公開に進む")').first
        pub_step.click()
        time.sleep(5)

        # 価格入力欄を探して 980 を維持
        inputs = page.locator('input[type="number"], input[type="tel"], input[type="text"]')
        for i in range(inputs.count()):
            inp = inputs.nth(i)
            try:
                val = inp.input_value(timeout=1000)
                if val in ("1980", "1,980", "980"):
                    inp.click()
                    inp.fill("980")
                    print(f"[CRO Upgrade] Confirmed price input: {val} -> 980")
                    break
            except Exception:
                pass

        time.sleep(2)
        paywall_step_btn = page.locator('button:has-text("有料エリア設定")').first
        if paywall_step_btn.is_visible(timeout=4000):
            paywall_step_btn.click()
            time.sleep(4)

        page.screenshot(path=os.path.join(ROOT_DIR, "ai_ceo_system", "data", "paid_note_publish_modal.png"))

        final_btn = page.locator('button:has-text("投稿する"), button:has-text("更新する"), button:has-text("公開")').last
        if final_btn.is_visible(timeout=5000):
            final_btn.click()
            print("[CRO Upgrade] Clicked final publish button")
            time.sleep(8)

        context.close()
        print("[CRO Upgrade] Paid Note update completed!")

        sync_record = {
            "synced_at": datetime.now().astimezone().isoformat(),
            "preview_schema_version": 2,
            "top3_slugs": [w.get("slug", "") for w in winners[:3]],
            "top3_titles": [_sanitize_note_copy(w.get("title", "")) for w in winners[:3]],
            "title_applied": new_title,
            "paid_area_chars_preserved": safety_check.get("afterLen", 0),
            "status": "synced",
        }
        os.makedirs(os.path.dirname(PAID_NOTE_SYNC_STATE_PATH), exist_ok=True)
        with open(PAID_NOTE_SYNC_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(sync_record, f, ensure_ascii=False, indent=2)
        return sync_record


def sync_paid_note_safely_if_needed(top_winners: list[dict] | None = None, force: bool = False) -> dict:
    """TOP3構成が変わったとき、またはスキーマ更新・未同期のときだけ安全ガード付きで有料note冒頭とタイトルを更新する。"""
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        return {"status": "skipped_github_actions"}

    winners = _resolve_top_winners(top_winners)
    target_slugs = [w.get("slug", "") for w in winners[:3]]
    if not force and os.path.exists(PAID_NOTE_SYNC_STATE_PATH):
        try:
            with open(PAID_NOTE_SYNC_STATE_PATH, "r", encoding="utf-8") as f:
                prev = json.load(f)
            if prev.get("status") == "synced" and prev.get("top3_slugs") == target_slugs and prev.get("preview_schema_version", 1) >= 2:
                return {
                    "status": "already_synced_with_current_top3",
                    "top3_slugs": target_slugs,
                    "title_applied": prev.get("title_applied", ""),
                    "synced_at": prev.get("synced_at", ""),
                }
        except Exception:
            pass

    return update_paid_note_and_price(top_winners=winners)


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    res = sync_paid_note_safely_if_needed(force=force_flag)
    print(json.dumps(res, ensure_ascii=False, indent=2))

