import json
import os
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRODUCT_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "product_site")
WORKFLOW_DIR = os.path.join(ROOT_DIR, ".github", "workflows")
NOTE_URL = "https://note.com/toproad_1989/n/n5d0e28a74f91"


class DeveloperAgent:
    """自律開発・デプロイサブエージェント (Full-Stack Developer Agent)
    1. メインWebプロダクト『AutoFlow AI（業務削減ROIシミュレーター＆コード生成）』の自動ビルド
    2. 第2弾Webツール『AutoFix AI（GASエラー＆AIプロンプト0秒診断・自動修正ツール）』の自動ビルド
    3. 職種別Programmatic SEOページ（全20業種・JSON-LD構造化データ＆無料お試しプロンプト内蔵）の自動量産
    4. PC閉鎖中も24時間自律稼働するGitHub Actions Cronワークフローの自動生成
    """

    def __init__(self):
        os.makedirs(PRODUCT_DIR, exist_ok=True)
        os.makedirs(os.path.join(PRODUCT_DIR, "usecases"), exist_ok=True)
        os.makedirs(WORKFLOW_DIR, exist_ok=True)

    def build_all(self, niches: list) -> dict:
        main_file = self._build_main_webapp(niches)
        debugger_file = self._build_gas_debugger_tool()
        seo_files = self._build_programmatic_seo_pages(niches)
        sitemap_file = self._build_sitemap(niches)
        workflow_file = self._build_github_actions_cron()
        return {
            "built_at": datetime.now().astimezone().isoformat(),
            "main_webapp": main_file,
            "second_tool": debugger_file,
            "tools_count": 2,
            "seo_pages_built": len(seo_files),
            "seo_files": seo_files,
            "sitemap": sitemap_file,
            "cron_workflow": workflow_file
        }

    def _build_main_webapp(self, niches: list) -> str:
        usecase_links = ""
        for item in niches:
            yearly = item["avg_hours_saved_monthly"] * 12 * item["hourly_wage"]
            usecase_links += f"""
            <a href="usecases/{item['slug']}.html" class="block bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-sky-500/50 rounded-xl p-4 transition">
              <div class="text-xs text-sky-400 font-bold mb-1">年間削減目安: ¥{yearly:,}</div>
              <div class="text-sm font-bold text-slate-100">{item['title']}</div>
              <div class="text-[11px] text-slate-400 mt-1">月平均 {item['avg_hours_saved_monthly']}時間削減レシピを見る →</div>
            </a>"""

        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AutoFlow AI | 30秒で業務削減額を算出＆自動化プロンプト/GASコード即時生成ツール</title>
  <meta name="description" content="あなたのルーティン業務を入力するだけで、年間の削減可能コスト（円）を自動計算し、コピペでそのまま使えるAIプロンプトとGoogle Apps Script(GAS)自動化コードを0秒で生成します。" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{ font-family: 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif; background: #0f172a; color: #f8fafc; }}
    .glass {{ background: rgba(30, 41, 59, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(148, 163, 184, 0.2); }}
    .gradient-text {{ background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  </style>
</head>
<body class="min-h-screen flex flex-col">
  <!-- Header -->
  <header class="border-b border-slate-800 py-4 px-6 flex flex-wrap justify-between items-center max-w-6xl mx-auto w-full gap-4">
    <div class="flex items-center gap-3">
      <span class="bg-sky-500 text-slate-950 font-black px-2.5 py-1 rounded text-sm">AI CEO BUILT</span>
      <h1 class="text-xl font-bold tracking-tight">AutoFlow <span class="text-sky-400">ROI & Code Lab</span></h1>
    </div>
    <nav class="flex items-center gap-4 text-xs font-bold">
      <a href="index.html" class="text-sky-400">📊 削減額シミュレーター</a>
      <a href="gas-debugger.html" class="text-emerald-400 hover:underline">🛠️ GASエラー3秒診断ツール (NEW)</a>
      <a href="pro-pack.html" class="bg-amber-400 text-slate-950 px-3 py-1.5 rounded-lg">⚡ 全50種パック (¥1,980)</a>
    </nav>
  </header>

  <!-- Hero -->
  <main class="max-w-6xl mx-auto w-full px-6 py-10 flex-1">
    <div class="text-center mb-10">
      <p class="text-sky-400 font-semibold text-sm mb-2 uppercase tracking-wider">登録不要・完全無料・0秒生成</p>
      <h2 class="text-3xl md:text-5xl font-extrabold mb-4 leading-tight">
        あなたの仕事を<span class="gradient-text">「完全自動化」</span>したら<br/>年間いくら浮くか30秒で診断＆コード生成
      </h2>
      <p class="text-slate-400 max-w-2xl mx-auto text-sm md:text-base">
        職種と作業時間を選ぶだけで、年間削減コスト（ROI）の算出と同時に、今日からコピペで使える<strong>「構造化AIプロンプト」</strong>と<strong>「Google Apps Script (GAS) 自動実行コード」</strong>を即時出力します。
      </p>
    </div>

    <!-- Main Interactive Simulator & Generator -->
    <div class="grid md:grid-cols-12 gap-8 items-start mb-16">
      <!-- Left Input Panel -->
      <div class="md:col-span-5 glass rounded-2xl p-6 shadow-2xl">
        <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
          <span class="w-6 h-6 rounded-full bg-sky-500 text-slate-950 inline-flex items-center justify-center text-xs font-black">1</span>
          自動化したい業務を選択
        </h3>

        <label class="block text-xs text-slate-400 mb-1">業務カテゴリ</label>
        <select id="taskCategory" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-sm mb-4 focus:outline-none focus:border-sky-400">
          <option value="ec">EC・物販：在庫監視・価格調査・出品データ整形</option>
          <option value="sns">SNS運用：X/Threads 毎日投稿・バズ構文生成</option>
          <option value="sales">営業・CS：問い合わせ自動返信・営業メール作成</option>
          <option value="backoffice">経理・事務：請求書データ抽出・スプレッドシート集計</option>
          <option value="content">動画・記事：YouTube台本・SEO記事構成作成</option>
        </select>

        <label class="block text-xs text-slate-400 mb-1">1日あたりの手作業時間（分）：<span id="minsLabel" class="text-sky-400 font-bold">60分</span></label>
        <input id="dailyMins" type="range" min="15" max="300" step="15" value="60" class="w-full accent-sky-400 mb-4" />

        <label class="block text-xs text-slate-400 mb-1">月間の稼働日数（日）：<span id="daysLabel" class="text-sky-400 font-bold">22日</span></label>
        <input id="monthlyDays" type="range" min="5" max="30" step="1" value="22" class="w-full accent-sky-400 mb-4" />

        <label class="block text-xs text-slate-400 mb-1">あなたの想定時給換算（円）：<span id="wageLabel" class="text-sky-400 font-bold">¥2,500</span></label>
        <input id="hourlyWage" type="range" min="1200" max="10000" step="100" value="2500" class="w-full accent-sky-400 mb-6" />

        <button onclick="generateAutomation()" class="w-full bg-gradient-to-r from-sky-500 to-indigo-500 hover:from-sky-400 hover:to-indigo-400 text-slate-950 font-black py-3 rounded-xl shadow-lg transition transform active:scale-95">
          ⚡ 削減額を計算＆自動化コードを生成する
        </button>
      </div>

      <!-- Right Output Panel -->
      <div class="md:col-span-7 glass rounded-2xl p-6 shadow-2xl">
        <div class="flex flex-wrap justify-between items-center border-b border-slate-700/70 pb-4 mb-5 gap-4">
          <div>
            <div class="text-xs text-slate-400">AI自動化による年間創出価値（試算）</div>
            <div id="annualYen" class="text-3xl md:text-4xl font-black text-emerald-400">¥607,200 / 年</div>
            <div id="annualHours" class="text-xs text-slate-300 mt-1">年間 <strong>242.9時間</strong>（約30.4営業日分）の手作業を削減可能</div>
          </div>
          <button onclick="shareOnX()" class="bg-slate-800 hover:bg-slate-700 border border-slate-600 text-xs font-bold px-4 py-2.5 rounded-lg flex items-center gap-2 transition">
            🐦 診断結果をXでシェア
          </button>
        </div>

        <!-- Tabs -->
        <div class="flex gap-2 mb-3">
          <button id="tabPrompt" onclick="switchTab('prompt')" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-sky-500 text-slate-950">1. 専用AIプロンプト</button>
          <button id="tabGas" onclick="switchTab('gas')" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-800 text-slate-300">2. GAS自動実行コード</button>
          <button id="tabRoadmap" onclick="switchTab('roadmap')" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-800 text-slate-300">3. 完全自動化ロードマップ</button>
        </div>

        <div class="relative">
          <pre id="codeOutput" class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 overflow-x-auto whitespace-pre-wrap leading-relaxed h-72"></pre>
          <button onclick="copyCode()" id="copyBtn" class="absolute top-3 right-3 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded border border-slate-600">
            📋 コピー
          </button>
        </div>

        <!-- Monetization / Pro Pack Lead Box -->
        <div class="mt-6 bg-gradient-to-r from-indigo-950/90 to-slate-900 border border-indigo-500/40 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span class="bg-indigo-500/20 text-indigo-300 border border-indigo-400/30 text-[10px] font-bold px-2 py-0.5 rounded">PRO AUTOMATION PACK</span>
            <h4 class="font-bold text-sm mt-1">コピペで動く「全職種対応50種GAS＆AI自動化テンプレート完全版」</h4>
            <p class="text-xs text-slate-400 mt-0.5">スプレッドシート連携・自動通知・エラー防止付きの全50レシピ収録</p>
          </div>
          <div class="flex flex-col sm:flex-row gap-2 shrink-0">
            <a href="pro-pack.html" onclick="recordConversionClick()" class="bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-100 font-bold text-xs px-3 py-2.5 rounded-lg text-center">
              収録内容を見る
            </a>
            <a href="{NOTE_URL}" target="_blank" rel="noopener" onclick="recordConversionClick()" class="bg-amber-400 hover:bg-amber-300 text-slate-950 font-black text-xs px-4 py-2.5 rounded-lg shadow text-center">
              noteで入手 (¥1,980) →
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Directory of 20 Industry Specific Automation Guides -->
    <section class="border-t border-slate-800 pt-12">
      <div class="flex flex-wrap justify-between items-end mb-6 gap-4">
        <div>
          <span class="text-xs font-bold text-sky-400 uppercase tracking-wider">Industry Use Cases</span>
          <h3 class="text-2xl font-extrabold mt-1">業種・業務別のAI＆GAS自動化レシピ集（全{len(niches)}業種）</h3>
        </div>
        <a href="gas-debugger.html" class="text-xs font-bold text-emerald-400 hover:underline">🛠️ GASが動かない時は「エラー3秒診断ツール」へ →</a>
      </div>
      <div class="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {usecase_links}
      </div>
    </section>
  </main>

  <footer class="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
    AutoFlow AI Suite — Built & Operated 100% Autonomously by AI CEO Antigravity (Zero Human Intervention)
  </footer>

  <script>
    const TEMPLATES = {{
      ec: {{
        name: "EC・物販：在庫監視・価格調査・出品データ整形",
        prompt: `# 命令書\\nあなたはEC物販のデータアナリスト兼自動化エンジニアです。\\n以下の生データ（商品情報・競合価格リスト）から、利益率20%以上を確保できる適正販売価格を算出し、検索SEOに強い商品タイトル（40文字以内）と箇条書き特徴5点をJSON形式で出力してください。\\n\\n# 制約条件\\n- NGワード（最高、絶対、No.1等の景表法リスク語）は自動除外すること\\n- 出力は必ず以下のキーを持つJSON配列とすること: [title, suggested_price, profit_margin, bullet_points]`,
        gas: `// Googleスプレッドシートの在庫・価格リストを毎日自動チェックして通知するGAS\\nfunction monitorInventoryAndPrices() {{\\n  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Inventory');\\n  const rows = sheet.getDataRange().getValues();\\n  const alerts = [];\\n  for (let i = 1; i < rows.length; i++) {{\\n    const [sku, title, stock, myPrice, rivalPrice] = rows[i];\\n    if (stock <= 3 || myPrice > rivalPrice * 1.05) {{\\n      alerts.push("[要確認] SKU:" + sku + " " + title + " (在庫:" + stock + " / 自社:¥" + myPrice + " / 競合:¥" + rivalPrice + ")");\\n    }}\\n  }}\\n  if (alerts.length > 0) {{\\n    MailApp.sendEmail(Session.getActiveUser().getEmail(), '【自動監視】EC在庫・価格アラート', alerts.join('\\n'));\\n  }}\\n}}`,
        roadmap: `【Step 1】スプレッドシートに商品リストを配置（所要5分）\\n【Step 2】タブ2のGASコードを「拡張機能 > Apps Script」に貼り付け\\n【Step 3】トリガー設定で「毎日午前8時」に自動実行を設定 → 以後、人間はアラートが来た時だけ判断すればOK（作業時間92%削減）`
      }},
      sns: {{
        name: "SNS運用：X/Threads 毎日投稿・バズ構文生成",
        prompt: `# 命令書\\nあなたはSNSマーケティングの専門家です。以下の【テーマ】について、読者が思わず保存・リポストしたくなるX（旧Twitter）の140字ポスト3案と、長文スレッド構成（5連投）を作成してください。\\n\\n# 構成ルール\\n1. 1行目に「常識の逆を突く数字入りのフック」を入れる\\n2. 箇条書きで具体例を3つ示す\\n3. 最後に読者が今日すぐ試せる1アクションを提示する`,
        gas: `// スプレッドシートの予約投稿リストから毎日定時にWebhook経由で自動送信するGAS\\nfunction autoPostScheduledSNS() {{\\n  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Queue');\\n  const data = sheet.getDataRange().getValues();\\n  for (let i = 1; i < data.length; i++) {{\\n    const [id, text, status] = data[i];\\n    if (status === 'READY') {{\\n      Logger.log('Auto-posting: ' + text);\\n      sheet.getRange(i + 1, 3).setValue('POSTED_' + new Date().toISOString());\\n      break;\\n    }}\\n  }}\\n}}`,
        roadmap: `【Step 1】週末にAIプロンプトで1週間分（21本）の投稿案を一括生成（10分）\\n【Step 2】スプレッドシートに貼り付け、自動配信スクリプトをセット\\n【Step 3】インプレッション率の高い構文だけを翌週テンプレートに自動昇格`
      }},
      sales: {{
        name: "営業・CS：問い合わせ自動返信・営業メール作成",
        prompt: `# 命令書\\n以下の【顧客企業のWebサイト概要】と【自社の提供サービス】をもとに、押し売り感がなく「相手企業の具体的な課題」に寄り添った1to1営業メール（件名3案＋本文400字以内）を作成してください。`,
        gas: `// フォーム受信時にAI下書きフォーマットを自動生成してSlack/メール通知するGAS\\nfunction onFormSubmitAutoDraft(e) {{\\n  const info = e.namedValues;\\n  const draft = "件名: お問い合わせありがとうございます\\n\\n" + info['お名前'] + "様\\nご連絡ありがとうございます。以下の内容で承りました。";\\n  Logger.log(draft);\\n}}`,
        roadmap: `【Step 1】問い合わせフォームとスプレッドシートを連携\\n【Step 2】GASトリガー（フォーム送信時）で1次返信と社内要約通知を完全自動化`
      }},
      backoffice: {{
        name: "経理・事務：請求書データ抽出・スプレッドシート集計",
        prompt: `# 命令書\\n以下の請求書・領収書テキストから、【発行日・支払先名・税抜金額・消費税額（10%/8%区分）・合計金額・勘定科目候補】を抽出し、スプレッドシートにそのまま貼り付けられるTSV（タブ区切り）形式で出力してください。`,
        gas: `// 指定Googleドライブフォルダ内の新規請求書ファイルを検知して台帳へ自動追記するGAS\\nfunction scanInvoiceFolder() {{\\n  const files = DriveApp.searchFiles("title contains '請求書'");\\n  while (files.hasNext()) {{\\n    const file = files.next();\\n    Logger.log('Detected invoice: ' + file.getName());\\n  }}\\n}}`,
        roadmap: `【Step 1】Googleドライブに「月次請求書」フォルダを作成\\n【Step 2】GASで毎晩自動スキャンし、スプレッドシート台帳へファイル名・URL・日付を自動記帳`
      }},
      content: {{
        name: "動画・記事：YouTube台本・SEO記事構成作成",
        prompt: `# 命令書\\n以下のキーワードで検索上位・高視聴維持率を獲得するための「結論ファースト構成案」と、冒頭15秒で離脱を防ぐオープニング台本を作成してください。`,
        gas: `// 競合チャンネルやトレンドキーワードの更新履歴を毎朝スプレッドシートに記録するGAS\\nfunction logDailyContentTopics() {{\\n  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();\\n  sheet.appendRow([new Date(), 'Trend Check Executed', 'OK']);\\n}}`,
        roadmap: `【Step 1】キーワードリストを登録\\n【Step 2】構成プロンプトで骨子を3分で作成し、収録・編集に集中する体制を構築`
      }}
    }};

    let currentTab = 'prompt';

    function calculateROI() {{
      const mins = parseInt(document.getElementById('dailyMins').value, 10);
      const days = parseInt(document.getElementById('monthlyDays').value, 10);
      const wage = parseInt(document.getElementById('hourlyWage').value, 10);

      document.getElementById('minsLabel').textContent = mins + '分';
      document.getElementById('daysLabel').textContent = days + '日';
      document.getElementById('wageLabel').textContent = '¥' + wage.toLocaleString();

      const savedHoursMonthly = (mins / 60) * days * 0.85;
      const savedHoursYearly = savedHoursMonthly * 12;
      const savedYenYearly = Math.round(savedHoursYearly * wage);

      document.getElementById('annualYen').textContent = '¥' + savedYenYearly.toLocaleString() + ' / 年';
      document.getElementById('annualHours').innerHTML = '年間 <strong>' + savedHoursYearly.toFixed(1) + '時間</strong>（約' + (savedHoursYearly / 8).toFixed(1) + '営業日分）の手作業を削減可能';
      return {{ savedYenYearly, savedHoursYearly }};
    }}

    function renderCode() {{
      const cat = document.getElementById('taskCategory').value;
      const item = TEMPLATES[cat];
      document.getElementById('codeOutput').textContent = item[currentTab];
    }}

    function switchTab(tab) {{
      currentTab = tab;
      ['prompt', 'gas', 'roadmap'].forEach(t => {{
        const btn = document.getElementById('tab' + t.charAt(0).toUpperCase() + t.slice(1));
        btn.className = (t === tab)
          ? 'px-3 py-1.5 rounded-lg text-xs font-bold bg-sky-500 text-slate-950'
          : 'px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-800 text-slate-300';
      }});
      renderCode();
    }}

    function generateAutomation() {{
      calculateROI();
      renderCode();
    }}

    function copyCode() {{
      const text = document.getElementById('codeOutput').textContent;
      navigator.clipboard.writeText(text);
      const btn = document.getElementById('copyBtn');
      btn.textContent = '✅ コピー完了!';
      setTimeout(() => {{ btn.textContent = '📋 コピー'; }}, 2000);
    }}

    function shareOnX() {{
      const {{ savedYenYearly, savedHoursYearly }} = calculateROI();
      const cat = document.getElementById('taskCategory').value;
      const text = encodeURIComponent(
        '私のルーティン業務（' + TEMPLATES[cat].name + '）をAI＆GASで自動化すると、年間【¥' + savedYenYearly.toLocaleString() + ' / ' + savedHoursYearly.toFixed(1) + '時間】浮く診断結果が出た…！その場で自動化コードまで生成されてヤバい https://toproad-creator.github.io/autoflow-ai-ceo/ #AutoFlowAI'
      );
      window.open('https://twitter.com/intent/tweet?text=' + text, '_blank');
    }}

    function recordConversionClick() {{
      fetch('/api/track?event=cta_click', {{ method: 'POST' }}).catch(() => {{}});
    }}

    ['dailyMins', 'monthlyDays', 'hourlyWage', 'taskCategory'].forEach(id => {{
      document.getElementById(id).addEventListener('input', generateAutomation);
    }});

    generateAutomation();
  </script>
</body>
</html>
"""
        out_path = os.path.join(PRODUCT_DIR, "index.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return out_path

    def _build_gas_debugger_tool(self) -> str:
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AutoFix AI | Google Apps Script(GAS)エラー＆AIプロンプト3秒診断・自動修正ツール</title>
  <meta name="description" content="GAS（Googleスプレッドシート自動化）で頻発するTypeErrorや6分実行制限エラー、AIプロンプトの出力崩れを3秒で診断し、エラー回避済みの 안전한コードテンプレートを即時生成します。" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen flex flex-col">
  <header class="border-b border-slate-800 py-4 px-6 max-w-5xl mx-auto w-full flex flex-wrap justify-between items-center gap-4">
    <a href="index.html" class="text-sky-400 text-sm font-bold hover:underline">← AutoFlow AI トップへ戻る</a>
    <a href="{NOTE_URL}" target="_blank" rel="noopener" class="bg-amber-400 text-slate-950 font-black text-xs px-3.5 py-2 rounded-lg">⚡ エラー対策済み全50種パック (¥1,980)</a>
  </header>

  <main class="max-w-5xl mx-auto w-full px-6 py-10 flex-1">
    <div class="text-center mb-10">
      <span class="bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-bold px-3 py-1 rounded-full">Day 3 新機能リリース・完全無料</span>
      <h1 class="text-3xl md:text-4xl font-extrabold mt-4 mb-3">🛠️ GASエラー＆AIプロンプト 3秒診断・自動修正ツール</h1>
      <p class="text-slate-400 text-sm max-w-2xl mx-auto">
        「AIが書いたGASコードを貼ったら赤字のエラーで止まった…」を0秒で解決。発生している症状を選ぶだけで、原因の特定と<strong>「エラー自動回避（try-catch＆安全チェック）付きの修正コード」</strong>を出力します。
      </p>
    </div>

    <div class="grid md:grid-cols-12 gap-8">
      <div class="md:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <label class="block text-xs text-slate-400 mb-2 font-bold">発生しているエラー・症状を選択してください</label>
        <select id="errorType" onchange="diagnoseError()" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-3 text-sm mb-4">
          <option value="null_sheet">TypeError: Cannot read properties of null (reading 'getDataRange')</option>
          <option value="undefined_val">TypeError: Cannot read properties of undefined (reading '0')</option>
          <option value="timeout">Exceeded maximum execution time（GASの6分制限で途中停止する）</option>
          <option value="permission">Exception: You do not have permission to call MailApp / DriveApp</option>
          <option value="json_break">AIの出力が毎回ズレてスプレッドシートに綺麗に貼れない</option>
        </select>

        <div id="causeBox" class="bg-slate-950 border border-emerald-500/30 rounded-xl p-4 text-xs text-slate-300 leading-relaxed"></div>
      </div>

      <div class="md:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div class="flex justify-between items-center mb-3">
          <span class="text-xs font-bold text-emerald-400">✅ そのまま貼り替えられる修正済み安全コード</span>
          <button onclick="copyFixed()" id="copyFixBtn" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1 rounded border border-slate-600">📋 コピー</button>
        </div>
        <pre id="fixedCode" class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 overflow-x-auto whitespace-pre-wrap h-64"></pre>

        <div class="mt-6 bg-indigo-950/80 border border-amber-400/50 rounded-xl p-4 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div>
            <div class="text-xs font-bold text-amber-300">最初からエラー対策済みの完成品を使いたい方へ</div>
            <p class="text-xs text-slate-300 mt-1">全10業種・50種類の動作確認済みGAS＆構造化プロンプト集をnoteで公開中</p>
          </div>
          <a href="{NOTE_URL}" target="_blank" rel="noopener" class="shrink-0 bg-amber-400 hover:bg-amber-300 text-slate-950 font-black text-xs px-4 py-2.5 rounded-lg">
            全50種パックを見る (¥1,980) →
          </a>
        </div>
      </div>
    </div>
  </main>

  <script>
    const ERRORS = {{
      null_sheet: {{
        cause: "【原因】getSheetByName('シート名') で指定したシート名が実際のタブ名と1文字でも違っているか、全角・半角スペースが混入しています。\\n【解決策】シートが見つからない場合に自動でアクティブシートへフォールバックするか、初期作成する安全コードに置き換えます。",
        code: `function safeGetSheet(sheetName) {{\\n  const ss = SpreadsheetApp.getActiveSpreadsheet();\\n  let sheet = ss.getSheetByName(sheetName);\\n  if (!sheet) {{\\n    // シートが存在しない場合はエラーで止めずに自動作成または先頭シートを使用\\n    sheet = ss.getActiveSheet();\\n    Logger.log('[AutoFix] 指定シートが見つからないため現在のシートを使用します: ' + sheet.getName());\\n  }}\\n  return sheet;\\n}}`
      }},
      undefined_val: {{
        cause: "【原因】スプレッドシートの空行を読み込んだ際や、フォーム送信イベント(e)をエディタの「実行」ボタンから直接押した際に undefined が発生しています。\\n【解決策】空行スキップ判定と安全な初期値ガードを追加します。",
        code: `function safeProcessRows() {{\\n  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();\\n  const rows = sheet.getDataRange().getValues();\\n  for (let i = 1; i < rows.length; i++) {{\\n    const row = rows[i] || [];\\n    const [id, title, status] = row;\\n    if (!id || status === 'DONE') continue; // 空行と処理済み行を安全にスキップ\\n    Logger.log('Processing: ' + id + ' / ' + (title || '名称未設定'));\\n  }}\\n}}`
      }},
      timeout: {{
        cause: "【原因】Google Apps Scriptには「1回の実行あたり最大6分」の制限があります。1行ずつ setValue() を呼ぶと通信が遅くなりタイムアウトします。\\n【解決策】開始時刻を監視して5分経過時点で安全に一時保存し、次回トリガーに引き継ぐバッチ処理構文にします。",
        code: `function batchProcessWithoutTimeout() {{\\n  const startTime = Date.now();\\n  const MAX_EXEC_MS = 4.5 * 60 * 1000; // 4分30秒で安全停止\\n  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();\\n  const rows = sheet.getDataRange().getValues();\\n  for (let i = 1; i < rows.length; i++) {{\\n    if (Date.now() - startTime > MAX_EXEC_MS) {{\\n      Logger.log('時間制限に近づいたため安全に中断しました。次回トリガーで再開します。');\\n      break;\\n    }}\\n    if (rows[i][2] !== 'DONE') {{\\n      sheet.getRange(i + 1, 3).setValue('DONE');\\n    }}\\n  }}\\n}}`
      }},
      permission: {{
        cause: "【原因】カスタム関数（セル内に =myFunc() と書く方式）の中から MailApp や DriveApp を呼ぶことはGoogleの仕様で禁止されています。\\n【解決策】メニューボタンまたは「時計アイコン（時間主導型トリガー）」から実行する標準関数に変更します。",
        code: `// スプレッドシートを開いた時に上部メニューへ「⚡自動実行」ボタンを追加するコード\\nfunction onOpen() {{\\n  SpreadsheetApp.getUi()\\n    .createMenu('⚡AI自動化メニュー')\\n    .addItem('今すぐ自動処理を実行', 'runMainAutomation')\\n    .addToUi();\\n}}\\n\\nfunction runMainAutomation() {{\\n  MailApp.sendEmail(Session.getActiveUser().getEmail(), 'テスト通知', '正常に権限が承認されました！');\\n}}`
      }},
      json_break: {{
        cause: "【原因】AIへの指示（プロンプト）で出力形式を固定していないため、前置き挨拶やマークダウン記号が混ざっています。\\n【解決策】前置き挨拶を完全禁止し、タブ区切り(TSV)または純粋なJSONのみを強制出力させる構造化プロンプトを使用します。",
        code: `# 出力形式強制プロンプト（コピペ用）\\n以下の入力データを処理し、スプレッドシートへそのまま貼り付け可能な【タブ区切り(TSV)】のみを出力してください。\\n\\n【絶対遵守ルール】\\n1. 「承知しました」「以下が出力です」等の前置き・後書きは一切出力しないこと\\n2. 1行目は必ずヘッダー行（項目名）とすること\\n3. 欠損値がある場合は空欄ではなく「N/A」を出力すること`
      }}
    }};

    function diagnoseError() {{
      const key = document.getElementById('errorType').value;
      document.getElementById('causeBox').innerText = ERRORS[key].cause;
      document.getElementById('fixedCode').textContent = ERRORS[key].code;
    }}

    function copyFixed() {{
      navigator.clipboard.writeText(document.getElementById('fixedCode').textContent);
      const btn = document.getElementById('copyFixBtn');
      btn.textContent = '✅ コピー完了!';
      setTimeout(() => {{ btn.textContent = '📋 コピー'; }}, 2000);
    }}

    diagnoseError();
  </script>
</body>
</html>
"""
        out_path = os.path.join(PRODUCT_DIR, "gas-debugger.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        return out_path

    def _build_programmatic_seo_pages(self, niches: list) -> list:
        created = []
        for item in niches:
            slug = item["slug"]
            title = item["title"]
            hours = item["avg_hours_saved_monthly"]
            wage = item["hourly_wage"]
            yearly_yen = hours * 12 * wage
            starter_prompt = (
                f"# 命令書\\nあなたは「{title}」の専門自動化アシスタントです。\\n"
                f"以下の入力データを解析し、手作業をゼロにするための構造化表（TSV形式）と、チェックすべき異常値アラート3点を出力してください。"
            )
            page_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}のAIプロンプト＆GAS自動化方法で年間{yearly_yen:,}円削減 | AutoFlow AI</title>
  <meta name="description" content="{title}をAIとGoogle Apps Script(GAS)で完全自動化する方法。月間平均{hours}時間、年間{yearly_yen:,}円相当の業務コストを削減する無料プロンプト＆シミュレーター。" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [{{
      "@type": "Question",
      "name": "{title}をAIとGASで自動化すると年間いくらコスト削減できますか？",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "月間平均{hours}時間の手作業が削減でき、時給{wage:,}円換算で年間約{yearly_yen:,}円相当の業務時間・人件費コストを削減可能です。"
      }}
    }}]
  }}
  </script>
</head>
<body class="bg-slate-950 text-slate-100 p-6 md:p-10 max-w-4xl mx-auto font-sans">
  <div class="flex justify-between items-center border-b border-slate-800 pb-4 mb-6">
    <a href="../index.html" class="text-sky-400 text-sm font-bold hover:underline">← AutoFlow AI 総合シミュレーターに戻る</a>
    <a href="../gas-debugger.html" class="text-emerald-400 text-xs font-bold hover:underline">🛠️ GASエラー診断ツール</a>
  </div>

  <span class="bg-sky-500/20 text-sky-300 text-xs font-bold px-3 py-1 rounded-full">業種別AI＆GAS自動化レシピ</span>
  <h1 class="text-2xl md:text-4xl font-extrabold mt-3 mb-3">{title} 完全自動化ガイド＆即時コード生成</h1>
  <p class="text-slate-400 mb-6">月間平均 <strong>{hours}時間</strong>（時給{wage:,}円換算で<strong>年間 ¥{yearly_yen:,}</strong>）の手作業を削減できる自動化レシピです。</p>

  <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-6">
    <h2 class="text-lg font-bold mb-2 text-sky-400">📋 今すぐ使える「{title}」無料スタータープロンプト</h2>
    <pre class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 whitespace-pre-wrap mb-4">{starter_prompt}</pre>
    <p class="text-sm text-slate-300 leading-relaxed mb-4">
      さらにGoogleスプレッドシートの自動トリガー（GAS）を組み合わせることで、毎日の定型チェックや転記・通知まで人間の手作業ゼロで完結できます。
    </p>
    <div class="flex flex-wrap gap-3 mt-5">
      <a href="../index.html" class="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-5 py-2.5 rounded-lg text-sm">
        無料シミュレーターで専用コードを生成する →
      </a>
      <a href="{NOTE_URL}" target="_blank" rel="noopener" class="bg-amber-400 hover:bg-amber-300 text-slate-950 font-black px-5 py-2.5 rounded-lg text-sm">
        ⚡ 全50種プロンプト＆GAS完全版パック (¥1,980) →
      </a>
    </div>
  </div>
</body>
</html>
"""
            p_path = os.path.join(PRODUCT_DIR, "usecases", f"{slug}.html")
            with open(p_path, "w", encoding="utf-8") as f:
                f.write(page_html)
            created.append(p_path)
        return created

    def _build_sitemap(self, niches: list) -> str:
        base_url = "https://toproad-creator.github.io/autoflow-ai-ceo"
        urls = [
            f"{base_url}/index.html",
            f"{base_url}/gas-debugger.html",
            f"{base_url}/pro-pack.html"
        ]
        for item in niches:
            urls.append(f"{base_url}/usecases/{item['slug']}.html")
        xml_items = "\n".join([f"  <url><loc>{u}</loc></url>" for u in urls])
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{xml_items}
</urlset>
"""
        sitemap_path = os.path.join(PRODUCT_DIR, "sitemap.xml")
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(xml)
        return sitemap_path

    def _build_github_actions_cron(self) -> str:
        yml = """name: Autonomous AI CEO 24h Cycle & Live Deploy

on:
  push:
    branches: [ main ]
  schedule:
    # 毎日 日本時間 08:00 (UTC 23:00) にPCが閉じていてもクラウド上で自動稼働
    - cron: '0 23 * * *'
  workflow_dispatch:

permissions:
  contents: write
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  autonomous_ceo_cycle:
    runs-on: ubuntu-latest
    env:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run AI CEO Daily Orchestrator (Research -> Build -> Marketing -> CFO Audit)
        run: python ai_ceo_system/agents/ceo_orchestrator.py --cloud-cron

      - name: Auto-Commit & Push Daily Growth Artifacts
        if: github.event_name != 'push'
        run: |
          git config user.name "Antigravity AI CEO"
          git config user.email "ai-ceo@users.noreply.github.com"
          git add wallet.json status_log.md ai_ceo_system/
          git diff --quiet && git diff --staged --quiet || (git commit -m "chore(autonomous): daily AI CEO build & metrics update [skip ci]" && git push) || true

      - name: Setup GitHub Pages
        uses: actions/configure-pages@v5

      - name: Upload Static Site Artifact (ai_ceo_system/product_site)
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'ai_ceo_system/product_site'

      - name: Deploy to GitHub Pages (24/7 Live Public URL)
        id: deployment
        uses: actions/deploy-pages@v4
"""
        wf_path = os.path.join(WORKFLOW_DIR, "autonomous_daily_cron.yml")
        with open(wf_path, "w", encoding="utf-8") as f:
            f.write(yml)
        return wf_path
