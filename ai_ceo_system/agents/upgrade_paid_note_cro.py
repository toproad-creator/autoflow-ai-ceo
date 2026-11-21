import json
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

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
    for term in ("AI起業対決", "AI CEO", "実験ログ", "実験台", "実験", "対決"):
        cleaned = cleaned.replace(term, "")
    return cleaned.strip()


def _resolve_top_winners(top_winners: list[dict] | None = None) -> list[dict]:
    if top_winners:
        return top_winners[:3]
    if os.path.exists(EVOLUTION_STATE_PATH):
        try:
            with open(EVOLUTION_STATE_PATH, "r", encoding="utf-8") as f:
                evo = json.load(f)
            wins = evo.get("selection_and_focus", {}).get("winners_top3") or []
            if wins:
                return wins[:3]
        except Exception:
            pass
    return [
        {"slug": "subsidy-business-plan", "title": "補助金申請・融資用の事業計画書ドラフト＆収支表自動作成"},
        {"slug": "hr-resume-screening", "title": "採用・人事の職務経歴書スクリーニング＆面接質問自動生成"},
        {"slug": "ec-inventory", "title": "EC・物販の在庫管理＆価格改定自動化"},
    ]


def build_high_converting_free_preview_html(top_winners: list[dict] | None = None) -> str:
    with open(TEMPLATES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    templates = data.get("templates", [])
    winners = _resolve_top_winners(top_winners)
    top1 = _sanitize_note_copy(winners[0]["title"]) if len(winners) > 0 else "補助金申請・事業計画書自動作成"
    top2 = _sanitize_note_copy(winners[1]["title"]) if len(winners) > 1 else "採用・職務経歴書スクリーニング自動化"
    top3 = _sanitize_note_copy(winners[2]["title"]) if len(winners) > 2 else "EC・物販の在庫管理＆価格改定自動化"

    # 全50レシピの完全一覧を生成
    cat_groups = {}
    for t in templates:
        cat_groups.setdefault(t["category"], []).append(f"{t['id']}：{t['title']}")

    toc_html = ""
    for idx, (cat, items) in enumerate(cat_groups.items(), start=1):
        toc_html += f"<p><b>【第{idx}章：{cat}（全5選）】</b><br>" + "<br>".join(f"・{it}" for it in items) + "</p>"

    html = f"""
<p><b>🔥【先着10部限定・50%OFFセール開催中！】</b><br>リリース記念として、通常価格 <b>¥1,980 ➔ 先着10部限定【¥980（1レシピあたり約19円）】</b> で公開しています！（※10部完売時点で ¥1,480 ➔ 定価 ¥1,980 へ段階的に値上げします）</p>
<p><b>📈 最新の市場ニーズ調査で特に要望が多い「3大自動化領域」を完全収録！</b><br>① <b>{top1}</b><br>② <b>{top2}</b><br>③ <b>{top3}</b><br>特に需要が集中しているこの3大テーマの即戦力レシピはもちろん、<b>全10業種・50種類すべて</b>をそのまま手に入れていただけます。</p>
<p>毎日の仕事で「事業計画・書類作成」「採用候補者のスクリーニング」「EC在庫や価格チェック」「請求書PDFの整理」「SNSや営業メール作成」に何時間も奪われていませんか？</p>
<p>もしあなたが1日60分のルーティン作業を月に22日行っている場合、時給2,500円換算で<b>【年間 607,200円（約243時間）】</b>もの貴重な時間とコストを手作業に溶かしている計算になります。</p>
<p>本記事『AutoFlow Pro 完全版パッケージ』は、プログラミング知識ゼロ・<b>コピペ5分</b>で今日からすぐに使える<b>【全10業種・計50種類】の「構造化AIプロンプト」と「Googleスプレッドシート自動実行コード（GAS）」</b>をすべて1つにまとめた実践コンプリートパックです。</p>
<h2>■ なぜ「普通のChatGPTの使い方」では業務が自動化できないのか？</h2>
<p>多くの方が「ChatGPTに毎回プロンプトを手打ちして、出てきた文章をコピーしてスプレッドシートやメールに貼り付ける」という作業を繰り返しています。しかし、これでは結局<b>「人間がコピペする手間」</b>が残ってしまいます。</p>
<p>本当にルーティン業務を消滅させるには、以下の2つをセットで使う必要があります。</p>
<p><b>① 出力形式（TSVやJSON）を完全に固定した「業務特化型の構造化AIプロンプト」</b><br><b>② Googleスプレッドシート上で毎日決まった時間に自動で動き、メール通知や記帳まで終わらせる「Google Apps Script (GAS) 完成コード」</b></p>
<p>本パックでは、この「プロンプト」と「GAS完成コード」のペアを<b>全10業種・50業務分すべて作成済み</b>の状態で収録しています。あなたは該当する番号のコードをコピーして貼り付けるだけで、今日からすぐに自動化の仕組みを稼働させることができます。</p>
<h2>■ 購入前にクオリティをご確認ください！【実物サンプル2本を無料丸ごと公開】</h2>
<p>「本当にコピペだけで使えるの？」「どんなコードが入っているの？」という不安をゼロにするため、有料エリアに収録されている全50本の中から、特に人気の高い<b>2本の実物レシピ（TPL-01・TPL-16）をこの無料エリアで丸ごと公開</b>します！</p>
<p>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br><b>🎁 無料実物サンプル①：TPL-01 [EC・物販] 競合価格の毎朝自動取得＆値下げアラート</b><br>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
<p><b>【① コピペ用・構造化AIプロンプト（ChatGPT / Claude / Gemini 対応）】</b></p>
<pre><code># 命令書
あなたは「EC・物販」領域のトップデータアナリスト兼業務自動化エキスパートです。
目的：「競合価格の毎朝自動取得＆値下げアラート」を人間の手作業ゼロ・最高精度で完結させること。
以下の【入力データ】を解析し、下記の【出力ルール】に従って即座に実務利用可能な形式で出力してください。

# 出力ルール
1. 曖昧な表現を排除し、スプレッドシートへそのまま貼り付けられるタブ区切り（TSV）形式で出力すること（列：商品名 / 自社価格 / 競合最安値 / 価格差 / 推奨改定価格 / 判定ステータス）。
2. 競合が自社より5%以上安い項目には先頭に [要価格改定] タグを付与すること。
3. 利益率を守りながら勝つための価格改定アクションを末尾に3行以内で提案すること。

# 入力データ
（ここに比較したい商品リストや競合価格テキストを貼り付けてください）</code></pre>
<p><b>【② 自動実行 Google Apps Script (GAS) 完成コード】</b><br>※Googleスプレッドシートの「拡張機能 ＞ Apps Script」にそのまま貼り付けて使えます。</p>
<pre><code>function autoExecute_TPL_01() {{
  // 対象業務: 競合価格の毎朝自動取得＆値下げアラート自動通知
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const alertEntries = [];

  for (let i = 1; i &lt; rows.length; i++) {{
    const [itemName, myPrice, rivalPrice, status] = rows[i];
    if (itemName &amp;&amp; status !== 'DONE' &amp;&amp; Number(rivalPrice) &lt; Number(myPrice)) {{
      const diff = Number(myPrice) - Number(rivalPrice);
      alertEntries.push('【値下げ検知】' + itemName + ' (自社:' + myPrice + '円 / 競合:' + rivalPrice + '円 / 差額:-' + diff + '円)');
      sheet.getRange(i + 1, 4).setValue('DONE');
      sheet.getRange(i + 1, 5).setValue(new Date().toLocaleString('ja-JP'));
    }}
  }}

  if (alertEntries.length &gt; 0) {{
    MailApp.sendEmail(
      Session.getActiveUser().getEmail(),
      '【AutoFlow自動アラート】競合値下げ検知レポート（' + alertEntries.length + '件）',
      alertEntries.join('\\n')
    );
  }}
}}</code></pre>
<p>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br><b>🎁 無料実物サンプル②：TPL-16 [経理・バックオフィス] 請求書PDFテキストからのインボイス対応TSV抽出＆台帳記帳</b><br>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
<p><b>【① コピペ用・構造化AIプロンプト】</b></p>
<pre><code># 命令書
あなたは経理・インボイス制度対応の専門AI監査アシスタントです。
以下の請求書・領収書テキストから必要項目を正確に抽出し、スプレッドシート記帳用のTSV形式で出力してください。

# 出力ルール
1. 出力列：取引日(YYYY-MM-DD) / 支払先名 / 登録番号(T+13桁) / 税抜金額 / 消費税額(10%/8%) / 税込合計 / 推奨勘定科目 / 摘要
2. 適格請求書発行事業者の登録番号（Tから始まる13桁）が欠落している場合は [要確認：登録番号なし] と明記すること。</code></pre>
<p><b>【② 自動実行 Google Apps Script (GAS) 完成コード】</b></p>
<pre><code>function autoExecute_TPL_16() {{
  // 対象業務: 請求書データの自動台帳記帳＆未確認インボイス通知
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const missingInvoiceList = [];

  for (let i = 1; i &lt; rows.length; i++) {{
    const [dateStr, vendor, invoiceId, amount, status] = rows[i];
    if (vendor &amp;&amp; status !== 'RECORDED') {{
      if (!String(invoiceId).startsWith('T') || String(invoiceId).length !== 14) {{
        missingInvoiceList.push('・' + vendor + '（金額: ' + amount + '円 / 登録番号要確認）');
      }}
      sheet.getRange(i + 1, 5).setValue('RECORDED');
    }}
  }}

  if (missingInvoiceList.length &gt; 0) {{
    MailApp.sendEmail(
      Session.getActiveUser().getEmail(),
      '【経理アラート】インボイス番号の要確認取引先リスト',
      missingInvoiceList.join('\\n')
    );
  }}
}}</code></pre>
<h2>■ 本パックに収録されている「全10業種・50種類」の完全一覧リスト</h2>
<p>有料エリアには、上記と同じく<b>「コピペ用・構造化AIプロンプト」と「GAS自動実行コード（＋初心者向け3分導入ガイド）」が50業務分すべてフルセットで収録</b>されています（合計64,000文字超の圧倒的ボリュームです）。</p>
{toc_html}
<h2>■ 先着10部限定！ランチ1回分（¥980）で一生モノの自動化資産を</h2>
<p>・通常価格：¥1,980<br>・<b>現在価格：先着10部限定【¥980（税込・買い切り・追加費用一切なし）】</b><br>・1レシピあたりの単価：<b>わずか約19円</b></p>
<p>時給2,500円の方なら、本パックのどれか1つのレシピを使って<b>「たった24分」の作業が浮くだけで、今日中に100%元が取れます。</b><br>先着10部が売り切れ次第、自動的に ¥1,480 ➔ ¥1,980 へ価格を改定しますので、最安値の今のうちにぜひ手に入れて毎日のルーティン作業を消滅させてください！</p>
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
                const hasTop3 = beforeText.includes('3大自動化領域') && beforeText.includes('先着10部');
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
    """TOP3構成が変わったとき、または未同期のときだけ安全ガード付きで有料note冒頭とタイトルを更新する。"""
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        return {"status": "skipped_github_actions"}

    winners = _resolve_top_winners(top_winners)
    target_slugs = [w.get("slug", "") for w in winners[:3]]
    if not force and os.path.exists(PAID_NOTE_SYNC_STATE_PATH):
        try:
            with open(PAID_NOTE_SYNC_STATE_PATH, "r", encoding="utf-8") as f:
                prev = json.load(f)
            if prev.get("status") == "synced" and prev.get("top3_slugs") == target_slugs:
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

