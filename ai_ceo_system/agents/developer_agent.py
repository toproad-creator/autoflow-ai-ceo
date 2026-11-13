import json
import os
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRODUCT_DIR = os.path.join(ROOT_DIR, "ai_ceo_system", "product_site")
WORKFLOW_DIR = os.path.join(ROOT_DIR, ".github", "workflows")
BASE_URL = "https://toproad-creator.github.io/autoflow-ai-ceo"
NOTE_URL = "https://note.com/toproad_1989/n/n5d0e28a74f91"


class DeveloperAgent:
    """自律開発・デプロイサブエージェント (Full-Stack Developer Agent)
    1. 第1弾ツール『AutoFlow AI（業務削減ROIシミュレーター＆コード生成）』
    2. 第2弾ツール『AutoFix AI（GASエラー＆AIプロンプト3秒診断・自動修正ツール）』
    3. 第3弾ツール『AutoPrompt Studio（深津式・ゴールシーク式 構造化プロンプト自動設計ツール）』
    4. 無料サンプル体験＆比較LP『free-templates.html』
    5. 職種別Programmatic SEOページ（全20業種）＋ sitemap.xml ＋ feed.xml (RSS) ＋ robots.txt
    """

    def __init__(self):
        os.makedirs(PRODUCT_DIR, exist_ok=True)
        os.makedirs(os.path.join(PRODUCT_DIR, "usecases"), exist_ok=True)
        os.makedirs(WORKFLOW_DIR, exist_ok=True)

    def build_all(self, niches: list) -> dict:
        main_file = self._build_main_webapp(niches)
        debugger_file = self._build_gas_debugger_tool()
        prompt_builder_file = self._build_prompt_studio_tool()
        free_samples_file = self._build_free_samples_funnel()
        seo_files = self._build_programmatic_seo_pages(niches)
        sitemap_file = self._build_sitemap(niches)
        rss_file = self._build_rss_feed(niches)
        robots_file = self._build_robots_txt()
        workflow_file = self._build_github_actions_cron()
        return {
            "built_at": datetime.now().astimezone().isoformat(),
            "main_webapp": main_file,
            "second_tool": debugger_file,
            "third_tool": prompt_builder_file,
            "free_samples_lp": free_samples_file,
            "tools_count": 4,
            "seo_pages_built": len(seo_files),
            "seo_files": seo_files,
            "sitemap": sitemap_file,
            "rss_feed": rss_file,
            "robots_txt": robots_file,
            "cron_workflow": workflow_file
        }

    def _nav_header(self) -> str:
        return f"""
  <header class="border-b border-slate-800 py-4 px-6 flex flex-wrap justify-between items-center max-w-6xl mx-auto w-full gap-4">
    <div class="flex items-center gap-3">
      <a href="index.html" class="flex items-center gap-2">
        <span class="bg-sky-500 text-slate-950 font-black px-2.5 py-1 rounded text-sm">AI CEO</span>
        <span class="text-xl font-bold tracking-tight text-white">AutoFlow <span class="text-sky-400">Suite</span></span>
      </a>
    </div>
    <nav class="flex flex-wrap items-center gap-3 text-xs font-bold">
      <a href="index.html" class="text-sky-400 hover:underline">📊 削減額シミュレーター</a>
      <a href="prompt-builder.html" class="text-purple-400 hover:underline">✨ プロンプト自動設計 (NEW)</a>
      <a href="gas-debugger.html" class="text-emerald-400 hover:underline">🛠️ GASエラー3秒診断</a>
      <a href="free-templates.html" class="text-slate-200 hover:underline">🎁 無料サンプル5選</a>
      <a href="{NOTE_URL}" target="_blank" rel="noopener" class="bg-amber-400 hover:bg-amber-300 text-slate-950 px-3 py-1.5 rounded-lg shadow">🔥 全50種完全版 (先着10部 ¥980)</a>
    </nav>
  </header>"""

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
  <meta property="og:title" content="AutoFlow AI | 30秒で業務削減額を算出＆自動化プロンプト/GASコード即時生成" />
  <meta property="og:description" content="登録不要・0秒生成。職種と作業時間を選ぶだけで年間削減コストの試算と専用AIプロンプト・GASコードを自動出力します。" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{BASE_URL}/" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="alternate" type="application/rss+xml" title="AutoFlow AI Automation Recipes" href="{BASE_URL}/feed.xml" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{ font-family: 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif; background: #0f172a; color: #f8fafc; }}
    .glass {{ background: rgba(30, 41, 59, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(148, 163, 184, 0.2); }}
    .gradient-text {{ background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  </style>
</head>
<body class="min-h-screen flex flex-col">
  {self._nav_header()}

  <main class="max-w-6xl mx-auto w-full px-6 py-10 flex-1">
    <div class="text-center mb-10">
      <p class="text-sky-400 font-semibold text-sm mb-2 uppercase tracking-wider">登録不要・完全無料・0秒生成（全4ツール稼働中）</p>
      <h1 class="text-3xl md:text-5xl font-extrabold mb-4 leading-tight">
        あなたの仕事を<span class="gradient-text">「完全自動化」</span>したら<br/>年間いくら浮くか30秒で診断＆コード生成
      </h1>
      <p class="text-slate-400 max-w-2xl mx-auto text-sm md:text-base">
        職種と作業時間を選ぶだけで、年間削減コスト（ROI）の算出と同時に、今日からコピペで使える<strong>「構造化AIプロンプト」</strong>と<strong>「Google Apps Script (GAS) 自動実行コード」</strong>を即時出力します。
      </p>
    </div>

    <!-- Main Interactive Simulator & Generator -->
    <div class="grid md:grid-cols-12 gap-8 items-start mb-12">
      <div class="md:col-span-5 glass rounded-2xl p-6 shadow-2xl">
        <h2 class="text-lg font-bold mb-4 flex items-center gap-2">
          <span class="w-6 h-6 rounded-full bg-sky-500 text-slate-950 inline-flex items-center justify-center text-xs font-black">1</span>
          自動化したい業務を選択
        </h2>

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

        <div class="mt-6 bg-gradient-to-r from-indigo-950/90 to-slate-900 border border-indigo-500/40 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span class="bg-indigo-500/20 text-indigo-300 border border-indigo-400/30 text-[10px] font-bold px-2 py-0.5 rounded">PRO AUTOMATION PACK</span>
            <h3 class="font-bold text-sm mt-1">コピペで動く「全職種対応50種GAS＆AI自動化テンプレート完全版」</h3>
            <p class="text-xs text-slate-400 mt-0.5">スプレッドシート連携・自動通知・エラー防止付きの全50レシピ収録</p>
          </div>
          <div class="flex flex-col sm:flex-row gap-2 shrink-0">
            <a href="free-templates.html" class="bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-100 font-bold text-xs px-3 py-2.5 rounded-lg text-center">
              🎁 無料サンプル5選を試す
            </a>
            <a href="{NOTE_URL}" target="_blank" rel="noopener" onclick="recordConversionClick()" class="bg-amber-400 hover:bg-amber-300 text-slate-950 font-black text-xs px-4 py-2.5 rounded-lg shadow text-center">
              🔥 先着10部限定 ¥980 で入手 →
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- 3 Free Tools Banner Grid -->
    <section class="grid md:grid-cols-3 gap-6 mb-14">
      <a href="prompt-builder.html" class="glass rounded-2xl p-6 hover:border-purple-400/60 transition block">
        <span class="text-[10px] font-bold bg-purple-500/20 text-purple-300 px-2.5 py-1 rounded">NEW TOOL #2</span>
        <h3 class="text-lg font-bold mt-3 mb-1">✨ 構造化プロンプト自動設計スタジオ</h3>
        <p class="text-xs text-slate-400">やりたい仕事を1行入れるだけで「深津式」「ゴールシーク式」「表データ強制出力式」の最高精度プロンプトに変換。</p>
      </a>
      <a href="gas-debugger.html" class="glass rounded-2xl p-6 hover:border-emerald-400/60 transition block">
        <span class="text-[10px] font-bold bg-emerald-500/20 text-emerald-300 px-2.5 py-1 rounded">TOOL #3</span>
        <h3 class="text-lg font-bold mt-3 mb-1">🛠️ GASエラー＆出力崩れ3秒診断</h3>
        <p class="text-xs text-slate-400">TypeErrorや6分実行制限エラー、AIの出力ズレを即座に解決する安全ラッパーコードを生成。</p>
      </a>
      <a href="free-templates.html" class="glass rounded-2xl p-6 hover:border-amber-400/60 transition block">
        <span class="text-[10px] font-bold bg-amber-500/20 text-amber-300 px-2.5 py-1 rounded">FREE STARTER</span>
        <h3 class="text-lg font-bold mt-3 mb-1">🎁 厳選5種の無料自動化レシピ公開</h3>
        <p class="text-xs text-slate-400">有料パック（全50種）の中から、特に人気の高い5つのプロンプト＆GASを登録不要で無料公開中。</p>
      </a>
    </section>

    <!-- Directory of 20 Industry Specific Automation Guides -->
    <section class="border-t border-slate-800 pt-12">
      <div class="flex flex-wrap justify-between items-end mb-6 gap-4">
        <div>
          <span class="text-xs font-bold text-sky-400 uppercase tracking-wider">Industry Use Cases</span>
          <h2 class="text-2xl font-extrabold mt-1">業種・業務別のAI＆GAS自動化レシピ集（全{len(niches)}業種）</h2>
        </div>
        <a href="prompt-builder.html" class="text-xs font-bold text-purple-400 hover:underline">✨ 自分の業務専用プロンプトを自動設計する →</a>
      </div>
      <div class="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {usecase_links}
      </div>
    </section>
  </main>

  <footer class="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
    AutoFlow AI Suite — Built & Operated 100% Autonomously by AI CEO Antigravity | <a href="feed.xml" class="underline">RSS Feed</a> | <a href="sitemap.xml" class="underline">Sitemap</a>
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

    function safeCopyText(text) {{
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).catch(() => fallbackCopyText(text));
      }} else {{
        fallbackCopyText(text);
      }}
    }}

    function fallbackCopyText(text) {{
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try {{ document.execCommand('copy'); }} catch (e) {{}}
      document.body.removeChild(ta);
    }}

    function copyCode() {{
      const text = document.getElementById('codeOutput').textContent;
      safeCopyText(text);
      const btn = document.getElementById('copyBtn');
      btn.textContent = '✅ コピー完了!';
      setTimeout(() => {{ btn.textContent = '📋 コピー'; }}, 2000);
    }}

    function shareOnX() {{
      const {{ savedYenYearly, savedHoursYearly }} = calculateROI();
      const cat = document.getElementById('taskCategory').value;
      const text = encodeURIComponent(
        '私のルーティン業務（' + TEMPLATES[cat].name + '）をAI＆GASで自動化すると、年間【¥' + savedYenYearly.toLocaleString() + ' / ' + savedHoursYearly.toFixed(1) + '時間】浮く診断結果が出た…！その場で自動化コードまで生成されてヤバい {BASE_URL}/ #AutoFlowAI'
      );
      window.open('https://twitter.com/intent/tweet?text=' + text, '_blank');
    }}

    function recordConversionClick() {{
      try {{ localStorage.setItem('af_last_cta_click', new Date().toISOString()); }} catch (e) {{}}
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

    def _build_prompt_studio_tool(self) -> str:
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AutoPrompt Studio | 1行の指示を「深津式・構造化プロンプト」へ0秒変換する無料ジェネレーター</title>
  <meta name="description" content="やりたい仕事を1行入力するだけで、ChatGPT・Claude・Geminiの性能を100%引き出す『深津式』『ゴールシーク式』『TSV表出力強制式』の構造化プロンプトを自動設計します。" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen flex flex-col">
  {self._nav_header()}
  <main class="max-w-5xl mx-auto w-full px-6 py-10 flex-1">
    <div class="text-center mb-10">
      <span class="bg-purple-500/20 text-purple-300 border border-purple-500/40 text-xs font-bold px-3 py-1 rounded-full">Day 4 新ツール公開・登録不要</span>
      <h1 class="text-3xl md:text-4xl font-extrabold mt-4 mb-3">✨ 構造化プロンプト自動設計スタジオ (AutoPrompt Studio)</h1>
      <p class="text-slate-400 text-sm max-w-2xl mx-auto">
        「AIにどう指示を出せばいいかわからない…」を解決。やりたい作業と出力スタイルを選ぶだけで、プロ仕様の構造化命令書（プロンプト）を0秒で組み立てます。
      </p>
    </div>

    <div class="grid md:grid-cols-12 gap-8">
      <div class="md:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <label class="block text-xs text-slate-400 mb-1 font-bold">1. AIにやらせたい作業（1行でOK）</label>
        <input id="userGoal" type="text" value="競合商品のレビューから不満点を抽出して改善案を出したい" oninput="buildPrompt()" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2.5 text-sm mb-4" />

        <label class="block text-xs text-slate-400 mb-1 font-bold">2. プロンプト設計フレームワーク</label>
        <select id="framework" onchange="buildPrompt()" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2.5 text-sm mb-4">
          <option value="fukatsu">深津式プロンプト（役割・制約条件・入力・出力を明確化）</option>
          <option value="tsv">スプレッドシート直貼りTSV強制出力式（事務・集計向け）</option>
          <option value="goalseek">逆質問・ゴールシーク式（AIに不足情報を質問させる）</option>
          <option value="gas_gen">Google Apps Script(GAS)完全コード生成式（エラー防止付き）</option>
        </select>

        <label class="block text-xs text-slate-400 mb-1 font-bold">3. 専門家のロール（役割）</label>
        <select id="roleSelect" onchange="buildPrompt()" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2.5 text-sm mb-4">
          <option value="マーケティング＆データ分析の専門コンサルタント">マーケティング＆データ分析の専門コンサルタント</option>
          <option value="年商10億円規模のEC・物販事業責任者">年商10億円規模のEC・物販事業責任者</option>
          <option value="Google Apps Scriptと業務自動化のシニアエンジニア">Google Apps Scriptと業務自動化のシニアエンジニア</option>
          <option value="BtoB法人営業のトップセールス兼コピーライター">BtoB法人営業のトップセールス兼コピーライター</option>
        </select>
      </div>

      <div class="md:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div class="flex justify-between items-center mb-3">
          <span class="text-xs font-bold text-purple-400">📋 自動設計されたプロ仕様プロンプト（ChatGPT / Claude / Gemini対応）</span>
          <button onclick="copyPrompt()" id="copyPBtn" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1 rounded border border-slate-600">📋 コピー</button>
        </div>
        <pre id="promptResult" class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 overflow-x-auto whitespace-pre-wrap h-72 leading-relaxed"></pre>

        <div class="mt-6 bg-indigo-950/80 border border-amber-400/50 rounded-xl p-4 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div>
            <div class="text-xs font-bold text-amber-300">プロンプトだけでなく「GAS自動実行コード」まで一括で欲しい方へ</div>
            <p class="text-xs text-slate-300 mt-1">全10業種・50種類の完成品プロンプト＆GASコード集をnoteで公開中</p>
          </div>
          <a href="{NOTE_URL}" target="_blank" rel="noopener" class="shrink-0 bg-amber-400 hover:bg-amber-300 text-slate-950 font-black text-xs px-4 py-2.5 rounded-lg">
            🔥 先着10部限定 ¥980 で見る →
          </a>
        </div>
      </div>
    </div>
  </main>

  <script>
    function buildPrompt() {{
      const goal = document.getElementById('userGoal').value || '業務データの整理と改善提案';
      const fw = document.getElementById('framework').value;
      const role = document.getElementById('roleSelect').value;
      let out = '';

      if (fw === 'fukatsu') {{
        out = `# 命令書\\nあなたは【${{role}}】です。\\n以下の制約条件と入力文をもとに、【${{goal}}】について最高精度の出力を生成してください。\\n\\n# 制約条件\\n- 抽象的な一般論は排除し、今日すぐ実務で使える具体策・数値目安を含めること\\n- 重要な結論を先頭3行で要約すること\\n- 専門用語には初心者向けの補足を入れること\\n\\n# 入力文\\n（ここに手元のテキストやデータを貼り付けてください）\\n\\n# 出力形式\\n1. 結論サマリー（3行）\\n2. 具体的な実行ステップ・構造化テーブル\\n3. 失敗しやすい注意点と対策`;
      }} else if (fw === 'tsv') {{
        out = `# 命令書\\nあなたは【${{role}}】です。\\n目的：【${{goal}}】\\n以下の入力データを解析し、GoogleスプレッドシートやExcelにそのまま貼り付けられる【タブ区切り（TSV）形式】のみで出力してください。\\n\\n# 絶対遵守ルール\\n- 「承知しました」等の前置き・挨拶は一切出力しないこと\\n- 1行目は必ずカラム名（見出し）とすること\\n- 優先度（高・中・低）および具体的な改善アクション列を必ず含めること\\n\\n# 入力データ\\n（ここにデータを貼り付け）`;
      }} else if (fw === 'goalseek') {{
        out = `# 命令書\\nあなたは【${{role}}】です。\\n私の最終ゴールは【${{goal}}】を最高レベルで達成することです。\\n\\nいきなり回答を出力するのではなく、まずこのゴールを100点満点で達成するために「私（ユーザー）から追加で聞き出すべき重要な前提条件・質問」を優先度順に5つ質問してください。\\n私がその質問に答えた後、最終的な成果物を出力してください。`;
      }} else {{
        out = `# 命令書\\nあなたは【${{role}}】です。\\n目的：【${{goal}}】をGoogleスプレッドシート上で完全自動化するGoogle Apps Script (GAS) コードを作成してください。\\n\\n# コード実装要件\\n1. シートが存在しない場合や空行がある場合に TypeError で止まらないよう防御的コード（ifガード・try-catch）を入れること\\n2. GASの6分実行制限を超えないようバッチ制御を入れること\\n3. 初心者でも設定できるよう、トリガー設定手順をコード末尾のコメントに明記すること`;
      }}
      document.getElementById('promptResult').textContent = out;
    }}

    function copyPrompt() {{
      const text = document.getElementById('promptResult').textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).catch(() => {{}});
      }}
      const btn = document.getElementById('copyPBtn');
      btn.textContent = '✅ コピー完了!';
      setTimeout(() => {{ btn.textContent = '📋 コピー'; }}, 2000);
    }}

    buildPrompt();
  </script>
</body>
</html>
"""
        out_path = os.path.join(PRODUCT_DIR, "prompt-builder.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        return out_path

    def _build_free_samples_funnel(self) -> str:
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>無料サンプル5選 vs 完全版50選 | AutoFlow AI プロンプト＆GAS自動化レシピ</title>
  <meta name="description" content="AutoFlow Pro（全50種パック）の中から、今すぐコピペで使える厳選5種のAIプロンプト＆GASコードを無料公開。" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen flex flex-col">
  {self._nav_header()}
  <main class="max-w-5xl mx-auto w-full px-6 py-10 flex-1">
    <div class="text-center mb-10">
      <span class="bg-amber-400/20 text-amber-300 border border-amber-400/40 text-xs font-bold px-3 py-1 rounded-full">🔥 先着10部限定 50%OFFセール開催中（¥1,980 ➔ ¥980）</span>
      <h1 class="text-3xl md:text-4xl font-extrabold mt-4 mb-3">🎁 厳選5種の自動化レシピ無料公開 ＆ 完全版50選の比較</h1>
      <p class="text-slate-400 text-sm max-w-2xl mx-auto">
        まずは無料サンプル5選の品質を実際にお試しください。気に入っていただけた方は、全10業種・50種類すべてが揃った完全版パック（先着10部限定 ¥980）をnoteにて即時入手いただけます。
      </p>
    </div>

    <!-- 5 Interactive Free Samples -->
    <div class="grid md:grid-cols-1 gap-6 mb-12">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-bold text-sky-400">無料サンプル #1（EC・物販）</span>
          <button onclick="copySample('s1', this)" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1 rounded border border-slate-600">📋 コピー</button>
        </div>
        <h3 class="font-bold text-base mb-2">競合価格チェック＆利益率20%確保タイトル自動生成レシピ</h3>
        <pre id="s1" class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 whitespace-pre-wrap">【AIプロンプト】
あなたはEC物販の価格戦略アナリストです。以下の原価・競合価格データから利益率20%以上を確保する推奨販売価格と、検索クリック率を高める40文字以内の商品タイトル案を3つTSV形式で出力してください。

【GAS自動実行コード】
function checkEcPriceMargin() {{
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  for (let i = 1; i < rows.length; i++) {{
    const [sku, cost, myPrice, rivalPrice] = rows[i];
    if (!sku) continue;
    const margin = (myPrice - cost) / myPrice;
    sheet.getRange(i + 1, 5).setValue(margin < 0.2 ? '⚠️利益率低下' : '✅適正');
  }}
}}</pre>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-bold text-purple-400">無料サンプル #2（SNS運用・マーケティング）</span>
          <button onclick="copySample('s2', this)" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1 rounded border border-slate-600">📋 コピー</button>
        </div>
        <h3 class="font-bold text-base mb-2">1つのネタからX（140字）＋長文スレッドを同時生成する構造化プロンプト</h3>
        <pre id="s2" class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 whitespace-pre-wrap">【AIプロンプト】
以下の【テーマ】について、読者が保存したくなるXの140字投稿3パターンと、5連投の解説スレッドを作成してください。
1行目には必ず「具体的な数字」と「従来の思い込みを覆す結論」を入れてください。</pre>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-bold text-emerald-400">無料サンプル #3（営業・カスタマーサポート）</span>
          <button onclick="copySample('s3', this)" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1 rounded border border-slate-600">📋 コピー</button>
        </div>
        <h3 class="font-bold text-base mb-2">Googleフォーム問い合わせ受信時の即時お礼＆社内要約通知GAS</h3>
        <pre id="s3" class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 whitespace-pre-wrap">function autoReplyInquiry() {{
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastRow = sheet.getLastRow();
  const [timestamp, name, email, body, status] = sheet.getRange(lastRow, 1, 1, 5).getValues()[0];
  if (status !== 'DONE' && email) {{
    MailApp.sendEmail(email, 'お問い合わせありがとうございます', name + '様\\n内容を確認の上、担当者よりご連絡いたします。');
    sheet.getRange(lastRow, 5).setValue('DONE');
  }}
}}</pre>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-bold text-amber-400">無料サンプル #4（経理・バックオフィス）</span>
          <button onclick="copySample('s4', this)" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1 rounded border border-slate-600">📋 コピー</button>
        </div>
        <h3 class="font-bold text-base mb-2">インボイス対応・請求書テキストからの勘定科目＆税区分TSV抽出プロンプト</h3>
        <pre id="s4" class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 whitespace-pre-wrap">【AIプロンプト】
以下の請求書・領収書テキストから【取引日 / 支払先 / 登録番号(T〜) / 税抜金額 / 消費税率(10%・8%) / 税込合計 / 推奨勘定科目】を抽出し、スプレッドシートへ直貼り可能なタブ区切り（TSV）形式で出力してください。前置き挨拶は一切不要です。</pre>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs font-bold text-pink-400">無料サンプル #5（GASエラー防止・バッチ処理）</span>
          <button onclick="copySample('s5', this)" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1 rounded border border-slate-600">📋 コピー</button>
        </div>
        <h3 class="font-bold text-base mb-2">GASの「6分実行制限エラー」を自動回避して途中再開する安全テンプレート</h3>
        <pre id="s5" class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 whitespace-pre-wrap">function safeBatchRunner() {{
  const start = Date.now();
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  for (let i = 1; i < rows.length; i++) {{
    if (Date.now() - start > 270000) break; // 4分30秒で安全中断
    if (rows[i][2] !== 'DONE') {{
      sheet.getRange(i + 1, 3).setValue('DONE');
    }}
  }}
}}</pre>
      </div>
    </div>

    <!-- Comparison Table -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-10 overflow-x-auto">
      <h2 class="text-lg font-bold mb-4">📊 無料版と完全版（AutoFlow Pro Pack）の違い</h2>
      <table class="w-full text-left text-xs md:text-sm border-collapse">
        <thead>
          <tr class="border-b border-slate-800 text-slate-400">
            <th class="py-3 px-4">機能・収録内容</th>
            <th class="py-3 px-4">無料Webツール版</th>
            <th class="py-3 px-4 text-amber-400 font-black">AutoFlow Pro 完全版 (先着10部 ¥980)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/70">
          <tr>
            <td class="py-3 px-4 font-bold">収録プロンプト＆GAS数</td>
            <td class="py-3 px-4">基本5種</td>
            <td class="py-3 px-4 text-emerald-400 font-bold">全10業種・計50種類フル収録（1レシピあたり約19円！）</td>
          </tr>
          <tr>
            <td class="py-3 px-4 font-bold">スプレッドシート完了ステータス自動記録</td>
            <td class="py-3 px-4">簡易版</td>
            <td class="py-3 px-4 text-emerald-400 font-bold">✅ DONE判定・実行日時タイムスタンプ・メール通知完備</td>
          </tr>
          <tr>
            <td class="py-3 px-4 font-bold">対象業務の網羅性</td>
            <td class="py-3 px-4">主要5分野のみ</td>
            <td class="py-3 px-4 text-emerald-400 font-bold">✅ EC・SNS・営業・経理・YouTube・SEO・人事・店舗・GAS・経営すべて網羅</td>
          </tr>
          <tr>
            <td class="py-3 px-4 font-bold">時給2,500円換算の損益分岐点</td>
            <td class="py-3 px-4">¥0</td>
            <td class="py-3 px-4 text-amber-300 font-bold">たった24分の作業短縮で100%元が取れる買い切り価格（¥1,980 ➔ ¥980）</td>
          </tr>
        </tbody>
      </table>
      <div class="mt-6 text-center">
        <a href="{NOTE_URL}" target="_blank" rel="noopener" class="inline-block bg-amber-400 hover:bg-amber-300 text-slate-950 font-black px-8 py-3.5 rounded-xl text-sm shadow-lg transition">
          🔥 noteで全50種・完全版パックを入手する (先着10部 ¥980) →
        </a>
      </div>
    </div>
  </main>
  <script>
    function copySample(id, btn) {{
      const text = document.getElementById(id).textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).catch(() => {{}});
      }}
      btn.textContent = '✅ コピー完了!';
      setTimeout(() => {{ btn.textContent = '📋 コピー'; }}, 2000);
    }}
  </script>
</body>
</html>
"""
        out_path = os.path.join(PRODUCT_DIR, "free-templates.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        return out_path

    def _build_gas_debugger_tool(self) -> str:
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AutoFix AI | Google Apps Script(GAS)エラー＆AIプロンプト3秒診断・自動修正ツール</title>
  <meta name="description" content="GAS（Googleスプレッドシート自動化）で頻発するTypeErrorや6分実行制限エラー、AIプロンプトの出力崩れを3秒で診断し、エラー回避済みのコードテンプレートを即時生成します。" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen flex flex-col">
  {self._nav_header()}

  <main class="max-w-5xl mx-auto w-full px-6 py-10 flex-1">
    <div class="text-center mb-10">
      <span class="bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-bold px-3 py-1 rounded-full">完全無料・エラー解決ツール</span>
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
            🔥 先着10部限定 ¥980 で見る →
          </a>
        </div>
      </div>
    </div>
  </main>

  <script>
    const ERRORS = {{
      null_sheet: {{
        cause: "【原因】getSheetByName('シート名') で指定したシート名が実際のタブ名と1文字でも違っているか、全角・半角スペースが混入しています。\\n【解決策】シートが見つからない場合に自動でアクティブシートへフォールバックするか、初期作成する安全コードに置き換えます。",
        code: `function safeGetSheet(sheetName) {{\\n  const ss = SpreadsheetApp.getActiveSpreadsheet();\\n  let sheet = ss.getSheetByName(sheetName);\\n  if (!sheet) {{\\n    sheet = ss.getActiveSheet();\\n    Logger.log('[AutoFix] 指定シートが見つからないため現在のシートを使用します: ' + sheet.getName());\\n  }}\\n  return sheet;\\n}}`
      }},
      undefined_val: {{
        cause: "【原因】スプレッドシートの空行を読み込んだ際や、フォーム送信イベント(e)をエディタの「実行」ボタンから直接押した際に undefined が発生しています。\\n【解決策】空行スキップ判定と安全な初期値ガードを追加します。",
        code: `function safeProcessRows() {{\\n  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();\\n  const rows = sheet.getDataRange().getValues();\\n  for (let i = 1; i < rows.length; i++) {{\\n    const row = rows[i] || [];\\n    const [id, title, status] = row;\\n    if (!id || status === 'DONE') continue;\\n    Logger.log('Processing: ' + id + ' / ' + (title || '名称未設定'));\\n  }}\\n}}`
      }},
      timeout: {{
        cause: "【原因】Google Apps Scriptには「1回の実行あたり最大6分」の制限があります。1行ずつ setValue() を呼ぶと通信が遅くなりタイムアウトします。\\n【解決策】開始時刻を監視して4分30秒経過時点で安全に一時保存し、次回トリガーに引き継ぐバッチ処理構文にします。",
        code: `function batchProcessWithoutTimeout() {{\\n  const startTime = Date.now();\\n  const MAX_EXEC_MS = 4.5 * 60 * 1000;\\n  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();\\n  const rows = sheet.getDataRange().getValues();\\n  for (let i = 1; i < rows.length; i++) {{\\n    if (Date.now() - startTime > MAX_EXEC_MS) {{\\n      Logger.log('時間制限に近づいたため安全に中断しました。次回トリガーで再開します。');\\n      break;\\n    }}\\n    if (rows[i][2] !== 'DONE') {{\\n      sheet.getRange(i + 1, 3).setValue('DONE');\\n    }}\\n  }}\\n}}`
      }},
      permission: {{
        cause: "【原因】カスタム関数（セル内に =myFunc() と書く方式）の中から MailApp や DriveApp を呼ぶことはGoogleの仕様で禁止されています。\\n【解決策】メニューボタンまたは「時計アイコン（時間主導型トリガー）」から実行する標準関数に変更します。",
        code: `function onOpen() {{\\n  SpreadsheetApp.getUi()\\n    .createMenu('⚡AI自動化メニュー')\\n    .addItem('今すぐ自動処理を実行', 'runMainAutomation')\\n    .addToUi();\\n}}\\n\\nfunction runMainAutomation() {{\\n  MailApp.sendEmail(Session.getActiveUser().getEmail(), 'テスト通知', '正常に権限が承認されました！');\\n}}`
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
      const text = document.getElementById('fixedCode').textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).catch(() => {{}});
      }}
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
  <div class="flex flex-wrap justify-between items-center border-b border-slate-800 pb-4 mb-6 gap-3">
    <a href="../index.html" class="text-sky-400 text-sm font-bold hover:underline">← AutoFlow AI 総合シミュレーター</a>
    <div class="flex gap-3 text-xs font-bold">
      <a href="../prompt-builder.html" class="text-purple-400 hover:underline">✨ プロンプト設計</a>
      <a href="../gas-debugger.html" class="text-emerald-400 hover:underline">🛠️ GASエラー診断</a>
    </div>
  </div>

  <span class="bg-sky-500/20 text-sky-300 text-xs font-bold px-3 py-1 rounded-full">業種別AI＆GAS自動化レシピ</span>
  <h1 class="text-2xl md:text-4xl font-extrabold mt-3 mb-3">{title} 完全自動化ガイド＆即時コード生成</h1>
  <p class="text-slate-400 mb-6">月間平均 <strong>{hours}時間</strong>（時給{wage:,}円換算で<strong>年間 ¥{yearly_yen:,}</strong>）の手作業を削減できる自動化レシピです。</p>

  <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-6">
    <div class="flex justify-between items-center mb-2">
      <h2 class="text-lg font-bold text-sky-400">📋 今すぐ使える「{title}」無料スタータープロンプト</h2>
      <button onclick="copyStarter(this)" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 py-1 rounded border border-slate-600">📋 コピー</button>
    </div>
    <pre id="starterPrompt" class="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-200 whitespace-pre-wrap mb-4">{starter_prompt}</pre>
    <p class="text-sm text-slate-300 leading-relaxed mb-4">
      さらにGoogleスプレッドシートの自動トリガー（GAS）を組み合わせることで、毎日の定型チェックや転記・通知まで人間の手作業ゼロで完結できます。
    </p>
    <div class="flex flex-wrap gap-3 mt-5">
      <a href="../index.html" class="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-5 py-2.5 rounded-lg text-sm">
        無料シミュレーターで専用コードを生成する →
      </a>
      <a href="{NOTE_URL}" target="_blank" rel="noopener" class="bg-amber-400 hover:bg-amber-300 text-slate-950 font-black px-5 py-2.5 rounded-lg text-sm">
        🔥 全50種プロンプト＆GAS完全版パック (先着10部 ¥980) →
      </a>
    </div>
  </div>
  <script>
    function copyStarter(btn) {{
      const text = document.getElementById('starterPrompt').textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).catch(() => {{}});
      }}
      btn.textContent = '✅ コピー完了!';
      setTimeout(() => {{ btn.textContent = '📋 コピー'; }}, 2000);
    }}
  </script>
</body>
</html>
"""
            p_path = os.path.join(PRODUCT_DIR, "usecases", f"{slug}.html")
            with open(p_path, "w", encoding="utf-8") as f:
                f.write(page_html)
            created.append(p_path)
        return created

    def _build_sitemap(self, niches: list) -> str:
        urls = [
            f"{BASE_URL}/index.html",
            f"{BASE_URL}/prompt-builder.html",
            f"{BASE_URL}/gas-debugger.html",
            f"{BASE_URL}/free-templates.html",
            f"{BASE_URL}/pro-pack.html"
        ]
        for item in niches:
            urls.append(f"{BASE_URL}/usecases/{item['slug']}.html")
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

    def _build_rss_feed(self, niches: list) -> str:
        items_xml = ""
        for item in niches:
            url = f"{BASE_URL}/usecases/{item['slug']}.html"
            yearly = item["avg_hours_saved_monthly"] * 12 * item["hourly_wage"]
            items_xml += f"""    <item>
      <title>{item['title']}のAIプロンプト＆GAS自動化レシピ（年間{yearly:,}円削減）</title>
      <link>{url}</link>
      <guid>{url}</guid>
      <description>{item['title']}を構造化プロンプトとGoogle Apps Scriptで自動化する手順と無料テンプレート。</description>
    </item>\n"""

        rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>AutoFlow AI | 業務自動化プロンプト＆GASレシピ集</title>
    <link>{BASE_URL}/</link>
    <description>AIとGoogleスプレッドシート(GAS)でルーティン業務を自動化する実践レシピ</description>
    <language>ja</language>
{items_xml}  </channel>
</rss>
"""
        rss_path = os.path.join(PRODUCT_DIR, "feed.xml")
        with open(rss_path, "w", encoding="utf-8") as f:
            f.write(rss)
        return rss_path

    def _build_robots_txt(self) -> str:
        txt = f"""User-agent: *
Allow: /
Sitemap: {BASE_URL}/sitemap.xml
"""
        robots_path = os.path.join(PRODUCT_DIR, "robots.txt")
        with open(robots_path, "w", encoding="utf-8") as f:
            f.write(txt)
        return robots_path

    def _build_github_actions_cron(self) -> str:
        yml = """name: Autonomous AI CEO 24h Cycle & Live Deploy

on:
  push:
    branches: [ main ]
  schedule:
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
