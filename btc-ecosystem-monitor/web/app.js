import {
  labels,
  esc,
  link,
  format,
  percent,
  time,
  inWindow,
  filterProjects,
  readStored,
  chartPath,
  validateConfig,
  download,
} from "./lib.js";
const $ = (s) => document.querySelector(s);
const names = {
  overview: "监控总览",
  projects: "项目与资产",
  news: "公告与进展",
  feedback: "用户反馈",
  markets: "行情与流动性",
  reports: "每日简报",
  settings: "来源与设置",
};
let data,
  config,
  markdown = "",
  archive = [];
let favorites = readStored(localStorage, "btc-observatory:favorites", []);
if (!Array.isArray(favorites)) favorites = [];
let draft = readStored(localStorage, "btc-observatory:config", null);
let journal = readStored(localStorage, "btc-observatory:journal", {
  schemaVersion: 1,
  events: [],
  feedback: [],
  metrics: [],
});
if (
  !journal ||
  !["events", "feedback", "metrics"].every((k) => Array.isArray(journal[k]))
)
  journal = { schemaVersion: 1, events: [], feedback: [], metrics: [] };
let filters = { query: "", ecosystem: "all", starred: false };
const badge = (v, tone = "") =>
  `<span class="chip ${tone}">${esc(labels[v] || v)}</span>`;
const projectName = (id) => data.projects.find((p) => p.id === id)?.name || id;
const empty = (title, body, symbol = "◌") =>
  `<div class="empty"><div class="empty-symbol">${symbol}</div><strong>${esc(title)}</strong><p>${esc(body)}</p></div>`;
const panel = (title, body, extra = "") =>
  `<section class="panel"><div class="panel-head"><h2>${esc(title)}</h2>${extra}</div>${body}</section>`;
const heading = (title, desc, actions = "") =>
  `<div class="page-heading"><div class="eyebrow">BITCOIN ECOSYSTEM INTELLIGENCE</div></div><div class="page-heading"><div><h1>${esc(title)}</h1><p>${esc(desc)}</p></div><div class="heading-actions">${actions}</div></div>`;
const reportButton =
  '<button class="button primary" data-action="download-report">↓ 导出每日简报</button>';
function notify(message) {
  $("#toast").textContent = message;
  $("#toast").classList.add("show");
  setTimeout(() => $("#toast").classList.remove("show"), 4000);
}
function persist(key, value) {
  try {
    localStorage.setItem("btc-observatory:" + key, JSON.stringify(value));
    return true;
  } catch {
    notify("浏览器存储不可用，请直接导出文件保存");
    return false;
  }
}
function notice() {
  if (data.mode === "uncollected")
    return '<div class="notice"><span>◷</span><span><strong>等待首次采集</strong> · 项目清单已准备好。请在 GitHub Actions 运行 BTC Monitor；当前 N/A 和空列表不表示没有事件。</span></div>';
  const age = (Date.now() - Date.parse(data.window.cutoff)) / 3600000;
  return age > 24
    ? `<div class="notice"><span>◷</span><span>快照距今 ${format(age, 1)} 小时，已超过每日更新周期。重新读取只加载现有文件；在线采集需运行 GitHub Actions。</span></div>`
    : "";
}
function projectTable(projects) {
  return projects.length
    ? `<div class="table-wrap"><table><thead><tr><th>项目 / 资产</th><th>生态</th><th>身份</th><th>来源覆盖</th><th>关注</th></tr></thead><tbody>${projects
        .map((p) => {
          const sources = data.sources.filter((s) => s.projectId === p.id),
            ok = sources.filter((s) => s.status === "ok").length;
          return `<tr><td><button class="project-name text-button" data-project="${esc(p.id)}"><span class="project-icon">${esc(p.name.slice(0, 2).toUpperCase())}</span><span><strong>${esc(p.name)}</strong><small>${esc(p.assets.map((a) => a.symbol).join(" · ") || "协议 / 产品 · 无选定代币")}</small></span></button></td><td><div class="chips">${p.ecosystems.map((e) => badge(e)).join("")}</div></td><td>${badge(p.identityStatus, p.identityStatus === "verified" ? "green" : "")}</td><td><span class="mono">${ok} / ${sources.length}</span><small class="muted"> 成功</small></td><td><button class="favorite ${favorites.includes(p.id) ? "selected" : ""}" data-favorite="${esc(p.id)}" aria-label="${favorites.includes(p.id) ? "取消关注" : "关注"} ${esc(p.name)}" aria-pressed="${favorites.includes(p.id)}">${favorites.includes(p.id) ? "★" : "☆"}</button></td></tr>`;
        })
        .join("")}</tbody></table></div>`
    : empty("没有匹配项目", "试试其他生态、名称或关注筛选。");
}
function eventCard(e) {
  return `<article class="event-card"><div class="event-top">${badge(e.evidence, e.evidence === "confirmed" ? "green" : "blue")}${badge(e.status)}<span>${esc(projectName(e.projectId))}</span></div><h3>${esc(e.title)}</h3><p>${esc((e.summary || "").slice(0, 420))}${(e.summary || "").length > 420 ? "…" : ""}</p><div class="event-meta"><span>公布 ${time(e.publishedAt)}</span><span>生效 ${time(e.effectiveAt)}</span>${link(e.url)}</div></article>`;
}
function sourcePanel() {
  const total = data.sources.length,
    ok = data.sources.filter((s) => s.status === "ok").length;
  return panel(
    "数据覆盖",
    `<div class="panel-body"><div class="source-row"><strong>成功核查的来源</strong><span class="mono">${ok} / ${total}</span></div><div class="progress-track"><progress max="${total || 1}" value="${ok}" aria-label="成功来源覆盖"></progress></div><p class="section-note">失败、未配置与部分覆盖均保留。<br>成功来源不等于完整项目核查。</p>${[
      ["ok", "已核查"],
      ["partial", "部分覆盖"],
      ["error", "采集失败"],
      ["not_checked", "尚未采集"],
      ["not_configured", "未配置"],
    ]
      .map(
        ([status, label]) =>
          `<div class="source-row"><span>${label}</span><strong class="mono">${data.sources.filter((s) => s.status === status).length}</strong></div>`,
      )
      .join("")}</div>`,
    `<a href="#settings">查看来源 ↗</a>`,
  );
}
function overview() {
  const news = data.events.filter((e) =>
    inWindow(e.publishedAt, data.window.cutoff, 1),
  );
  const severe = data.alerts.filter((a) => a.level !== "P2");
  const tokens = data.projects.reduce((n, p) => n + p.assets.length, 0);
  const upcoming = data.events.filter(
    (e) =>
      Date.parse(e.effectiveAt) > Date.parse(data.window.cutoff) &&
      Date.parse(e.effectiveAt) <= Date.parse(data.window.end7d),
  );
  return (
    heading(
      "BTC 生态，一站观察",
      "聚合项目进展、原始反馈与市场数据，让每个判断有据可查。",
      reportButton,
    ) +
    notice() +
    `<div class="stats"><div class="stat"><div class="stat-label">监控项目<span>▦</span></div><div class="stat-value">${data.projects.length}<small>项目组</small></div><div class="stat-foot">${new Set(data.projects.flatMap((p) => p.ecosystems)).size} 个生态 · ${tokens} 个观察资产</div></div><div class="stat"><div class="stat-label">24h 新增公告<span>≋</span></div><div class="stat-value">${data.mode === "uncollected" ? "—" : news.length}<small>条</small></div><div class="stat-foot">仅统计有精确时间的已采集记录</div></div><div class="stat"><div class="stat-label">需要关注<span>◉</span></div><div class="stat-value">${severe.length}<small>P0 / P1</small></div><div class="stat-foot">另有 ${data.alerts.filter((a) => a.level === "P2").length} 条数据质量待核查</div></div><div class="stat"><div class="stat-label">已核查项目<span>✓</span></div><div class="stat-value">${data.coverage.checkedProjects}<small>/ ${data.projects.length}</small></div><div class="stat-foot">至少一个来源成功 · 非完整覆盖</div></div></div><div class="grid-main"><div>${panel("项目观察清单", projectTable(data.projects), '<a href="#projects">全部项目 →</a>')}${panel(
      "最新进展 · 过去 7 日",
      data.events
        .filter((e) => inWindow(e.publishedAt, data.window.cutoff, 7))
        .slice(0, 5)
        .map(eventCard)
        .join("") ||
        empty(
          "暂无可列示的公告",
          "完成采集后显示发布版本与公告；公告发布时间与生效时间分别记录。",
          "≋",
        ),
      '<a href="#news">全部进展 →</a>',
    )}${panel("未来 7 日", upcoming.slice(0, 4).map(eventCard).join("") || empty("尚未核实未来重要日期", "人工核查活动、解锁或升级后，记录生效时间即可进入此日历。", "◷"))}</div><div class="aside-panels">${sourcePanel()}${panel("本期监控窗口", `<div class="panel-body"><div class="source-row"><div><strong>报告截止</strong><small>${time(data.window.cutoff)}</small></div></div><div class="source-row"><div><strong>过去 24 小时起点</strong><small>${time(data.window.start24h)}</small></div></div><div class="source-row"><div><strong>过去 7 日起点</strong><small>${time(data.window.start7d)}</small></div></div><p class="section-note">所有窗口为 (起点, 截止]。仅日期没有时分的记录不纳入精确窗口。</p></div>`)}${panel("证据标记", `<div class="panel-body"><div class="evidence-key"><i class="dot"></i>已确认事实 · 经人工核查的记录</div><div class="evidence-key"><i class="dot blue"></i>项目方声明 · 官方公告与发布</div><div class="evidence-key"><i class="dot orange"></i>用户报告 · 原始反馈与样本</div><div class="evidence-key"><i class="dot gray"></i>分析推断 · 与事实分别记录</div></div>`)}</div></div>`
  );
}
function projectsPage() {
  const ecos = [...new Set(data.projects.flatMap((p) => p.ecosystems))];
  return (
    heading(
      "项目与资产",
      "项目按多生态标签管理；同一项目的不同资产独立核验、独立报价。",
      '<a class="button" href="#settings">编辑项目配置</a>',
    ) +
    notice() +
    `<div class="toolbar"><input class="search" id="project-search" type="search" placeholder="搜索项目、代币或网络…" aria-label="搜索项目" value="${esc(filters.query)}"><select class="filter-select" id="ecosystem-filter" aria-label="筛选生态"><option value="all">全部生态</option>${ecos.map((e) => `<option ${e === filters.ecosystem ? "selected" : ""}>${esc(e)}</option>`).join("")}</select><div class="toggle-group"><button data-star-filter="all" class="${!filters.starred ? "active" : ""}">全部项目</button><button data-star-filter="starred" class="${filters.starred ? "active" : ""}">我的关注</button></div></div><section class="panel" id="project-results">${projectTable(filterProjects(data.projects, { ...filters, favorites }))}</section><p class="section-note">关注列表保存在当前浏览器。共享项目清单与采集设置由仓库 config.json 管理。</p>`
  );
}
function newsPage() {
  return (
    heading(
      "公告与进展",
      "原始来源可追溯。重复链接合并，计划、发布和执行分开记录。",
      '<a class="button" href="#settings">＋ 记录人工核查</a>',
    ) +
    notice() +
    `<div class="toolbar"><select class="filter-select" id="news-window" aria-label="公告时间范围"><option value="7">过去 7 日</option><option value="1">过去 24 小时</option><option value="all">全部已采集记录</option></select><span class="section-note">软件发布不代表协议激活或功能已部署</span></div><section class="panel" id="news-results">${newsList("7")}</section>`
  );
}
function newsList(window) {
  const rows = data.events
    .filter(
      (e) =>
        window === "all" ||
        inWindow(e.publishedAt, data.window.cutoff, Number(window)),
    )
    .sort(
      (a, b) =>
        (Date.parse(b.publishedAt) || 0) - (Date.parse(a.publishedAt) || 0),
    );
  return (
    rows.map(eventCard).join("") ||
    empty(
      "此窗口没有可列示记录",
      "请在来源与设置查看核查状态；采集失败不代表没有新增公告。",
      "≋",
    )
  );
}
function feedbackPage() {
  return (
    heading(
      "用户反馈",
      "按问题合并原始报告，以独立账号计数；机器人与重复转述不计入。",
    ) +
    notice() +
    `<div class="notice info">少量样本不能代表全部用户。自动采集 GitHub Issue 不自动判断真实性、严重性或修复成功；评论回应和跨问题合并由人工核查。</div>` +
    panel(
      "问题与独立样本",
      data.feedbackGroups
        .map(
          (g) =>
            `<article class="event-card"><div class="event-top">${badge("user_report", "orange")}<span>${esc(projectName(g.projectId))}</span><span class="feedback-count">24h ${g.independent24h} / 7d ${g.independent7d} 独立账号</span></div><h3>${esc(g.title)}</h3>${g.reports.map((r) => `<p>${esc(r.author || "未知账号")} · ${esc(r.platform)} ${r.isBot ? "（机器人，不计样本）" : ""}<br>${esc((r.summary || "").slice(0, 240))}</p><div class="event-meta">${link(r.url)}<span>报告 ${time(r.publishedAt)}</span><span>更新 ${time(r.updatedAt)}</span>${badge(r.status || "unknown")}${badge(r.reproduction || "not_verified")}</div><p>团队回应：${esc(r.teamResponse || "未核查")}</p>`).join("")}</article>`,
        )
        .join("") ||
        empty(
          "尚未取得可列示的原始反馈",
          "运行采集器读取公开 Issue，或在人工核查记录中补充可访问的原始帖子。",
        ),
    )
  );
}
function marketCard(p, a) {
  const m = data.markets.find((m) => m.assetId === a.id);
  const path = chartPath(m?.history || []);
  return `<article class="market-card"><div class="event-top"><h3>${esc(a.symbol)}</h3>${badge(a.standard)}</div><p class="section-note">${esc(a.network)}</p><div class="market-price mono">${m?.usd != null ? "$" + format(m.usd, 8) : "N/A"}</div><small class="muted mono">${format(m?.sats, 4)} sats</small>${path ? `<svg viewBox="0 0 240 55" class="sparkline" role="img" aria-label="${esc(a.symbol)} 采集到的价格历史"><path d="${path}"/></svg>` : '<div class="no-chart">尚无可用价格序列</div>'}<div class="market-meta"><span>24h</span><strong class="${(m?.returns?.["24h"]?.usd || 0) >= 0 ? "positive" : "negative"}">${percent(m?.returns?.["24h"]?.usd)}</strong><span>7d</span><strong>${percent(m?.returns?.["7d"]?.usd)}</strong></div><div class="market-meta"><span>相对 BTC · 24h</span><strong>${percent(m?.returns?.["24h"]?.relativeBtc)}</strong></div><div class="market-meta"><span>相对 BTC · 7d</span><strong>${percent(m?.returns?.["7d"]?.relativeBtc)}</strong></div><p class="section-note">${m ? time(m.quotedAt) : a.marketEnabled ? "等待首次采集" : "资产身份或市场映射待核验"}<br>${m ? link(m.url, "行情来源 ↗") : link(a.identitySource || p.officialUrl, "身份参考 ↗")}</p><button class="button small" data-project="${esc(p.id)}">查看资产与数据口径</button></article>`;
}
function marketsPage() {
  return (
    heading(
      "行情与流动性",
      "USD 与 sats 双重计价；只有可对齐的端点才计算收益。",
    ) +
    notice() +
    `<div class="market-grid">${data.projects.flatMap((p) => p.assets.map((a) => marketCard(p, a))).join("")}</div>` +
    panel(
      `盘口与成交额 · ${format(data.settings.tradeSizeUsd, 0)} USD 名义交易`,
      `<div class="table-wrap"><table><thead><tr><th>资产 / 场所</th><th>24h 成交额 USD</th><th>价差</th><th>买盘 −2%</th><th>卖盘 +2%</th><th>买入滑点</th><th>卖出滑点</th><th>盘口读取 UTC</th></tr></thead><tbody>${
        data.markets
          .map((m) => {
            const b = m.orderbook || {};
            return `<tr><td>${esc(m.symbol)}<br><small class="muted">${esc(b.venue || "盘口未配置")} ${esc(b.pair || "")}</small></td><td class="mono">${format(m.volume24hUsd, 0)}</td><td>${percent(b.spreadPct)}</td><td>${format(b.bidDepth2PctUsd, 0)}</td><td>${format(b.askDepth2PctUsd, 0)}</td><td>${percent(b.buySlippagePct)}</td><td>${percent(b.sellSlippagePct)}</td><td>${time(b.observedAt)}</td></tr>`;
          })
          .join("") ||
        '<tr><td colspan="8">N/A · 等待行情采集与经核实的 USD 盘口配置</td></tr>'
      }</tbody></table></div>`,
    ) +
    `<p class="section-note">成交额为提供方报价时刻的滚动 24h，未必等于本期截止窗口。盘口滑点逐档计算、不含手续费；交易深度不足则 N/A。±2% 深度可能受返回档数截断，不用于推断完整成交能力。未配置代币的协议项目价格为“不适用”。</p>`
  );
}
function reportsPage() {
  return (
    heading(
      "每日简报",
      "保留核查窗口、引用、缺失字段和更正记录，可直接下载 Markdown。",
      reportButton,
    ) +
    notice() +
    panel(
      "本期简报",
      `<pre class="report-preview">${esc(markdown || "简报文件不可用，请重新采集。")}</pre>`,
      '<button class="button small" data-action="download-json">↓ 原始快照 JSON</button>',
    ) +
    panel(
      "历史快照",
      archive.length
        ? `<div class="panel-body">${archive.map((a) => `<div class="source-row"><span>${esc(a.time)}</span><a href="./data/${esc(a.markdown)}" download>Markdown ↓</a></div>`).join("")}</div>`
        : empty(
            "尚无历史快照",
            "每次在线采集会保留一份独立记录，最多保存最近 90 期。",
          ),
    ) +
    panel(
      "关键事实变化与更正",
      data.corrections.length
        ? data.corrections
            .map(
              (c) =>
                `<div class="event-card"><h3>${esc(c.eventId)}</h3><p>${esc(JSON.stringify(c.before))} → ${esc(JSON.stringify(c.after))}</p><div class="event-meta">${time(c.at)} ${link(c.url)}</div></div>`,
            )
            .join("")
        : empty(
            "无已记录更正",
            "后续采集会比较同一事件的标题、状态、证据标签、生效时间与摘要。",
          ),
    )
  );
}
function sourceTable() {
  return `<div class="table-wrap"><table><thead><tr><th>来源</th><th>类别</th><th>状态</th><th>核查时间</th><th>缺口说明</th></tr></thead><tbody>${data.sources.map((s) => `<tr><td class="wordbreak">${link(s.url, s.name)}</td><td>${esc(s.kind)}</td><td>${badge(s.status, s.status === "ok" ? "green" : s.status === "error" ? "red" : "")}</td><td>${time(s.checkedAt)}</td><td class="wordbreak">${esc(s.error || "—")}</td></tr>`).join("")}</tbody></table></div>`;
}
function settingsPage() {
  const cfg = draft || config;
  return (
    heading(
      "来源与设置",
      "仓库配置决定下一次采集范围；本地草稿可导出后提交 GitHub。",
    ) +
    `<div class="notice info">配置与人工记录仅保存在当前浏览器。导出文件并提交仓库后，采集器才会使用它们。API 密钥只设置在 GitHub Actions Secrets，不能填写在此页。</div>` +
    panel("来源健康与覆盖", sourceTable()) +
    `<div class="settings-grid"><div>${panel("项目清单与监控参数", `<div class="panel-body"><label class="field" for="config-editor">config.json ${draft ? "· 有本地草稿" : "· 仓库版本"}<small>新增项目使用独立 id；同一项目多生态用 ecosystems 数组；不同资产放在 assets 中。</small></label><textarea class="code-editor" id="config-editor" spellcheck="false" aria-label="项目与监控配置 JSON">${esc(JSON.stringify(cfg, null, 2))}</textarea><div class="action-row"><button class="button primary" data-action="save-config">保存草稿</button><button class="button" data-action="export-config">导出 config.json</button><button class="button subtle" data-action="reset-config">恢复仓库版本</button></div><p class="section-note">启用行情须设置 identityStatus: verified，填写网络、协议标准、唯一标识、身份来源及 CoinGecko ID。</p></div>`)}${panel(
      "本期预警阈值",
      `<div class="panel-body"><div class="thresholds">${[
        ["24h 绝对收益", data.settings.priceChangePct + "%"],
        ["成交额 / 7 日中位数", data.settings.volumeMultiple + "×"],
        ["24h 深度下降", data.settings.depthDropPct + "%"],
        ["同问题独立样本", data.settings.feedbackSamples + " 个 / 24h"],
        ["7 日解锁 / 流通量", data.settings.unlockPct + "%"],
        ["报价时效", data.settings.staleMinutes + " 分钟"],
      ]
        .map(
          ([k, v]) => `<div class="threshold">${k}<strong>${v}</strong></div>`,
        )
        .join(
          "",
        )}</div><p class="section-note">价格不单独解释事件原因；缺失历史基线时，成交额与深度阈值不作判定。</p></div>`,
    )}</div><div>${panel("人工核查记录", `<form class="panel-body" id="evidence-form"><label class="field">记录类型<select name="recordKind"><option value="event">公告 / 进展 / 重要日期</option><option value="feedback">原始用户反馈</option></select></label><label class="field">项目<select name="projectId">${data.projects.map((p) => `<option value="${esc(p.id)}">${esc(p.name)}</option>`).join("")}</select></label><label class="field">标题<input name="title" required maxlength="200" placeholder="例如：官方发布新版本"></label><label class="field">原始链接<input name="url" type="url" required placeholder="https://…"></label><div class="detail-grid"><label class="field">证据类型<select name="evidence"><option value="statement">项目方声明</option><option value="confirmed">已确认事实</option><option value="user_report">用户报告</option><option value="inference">分析推断</option></select></label><label class="field">执行状态<select name="status"><option value="planned">计划</option><option value="published">已发布</option><option value="completed">已完成</option><option value="open">开放</option><option value="resolved">已解决</option><option value="unknown">待核查</option></select></label></div><div id="feedback-fields" hidden><label class="field">原始报告账号<input name="author" maxlength="100"></label><label class="field">平台<select name="platform"><option>GitHub</option><option>Reddit</option><option>X</option><option>Forum</option><option>Telegram</option><option>Discord</option></select></label><label class="field">问题合并标识<input name="problemKey" placeholder="同一问题使用相同标识"></label><label class="field">复现状态<select name="reproduction"><option value="not_verified">未独立复现</option><option value="reporter_reproduced">报告者提供复现</option><option value="independently_reproduced">已独立复现</option></select></label><label class="field">团队回应与解决说明<textarea name="teamResponse" maxlength="2000"></textarea></label></div><label class="field">公布时间（UTC）<input name="publishedAt" type="datetime-local"><small>只有日期或时间未核实请留空，在摘要说明；不纳入精确窗口。</small></label><label class="field">生效时间（UTC，可选）<input name="effectiveAt" type="datetime-local"></label><label class="field">摘要与核查说明<textarea name="summary" maxlength="4000" required placeholder="写明原始日期、是否复现、计划或实际执行，以及可见范围。"></textarea></label><button class="button primary" type="submit">＋ 保存核查草稿</button><p class="section-note">当前浏览器已有 ${journal.events.length} 条公告草稿、${journal.feedback.length} 条反馈草稿。原始账号按问题去重；草稿导出后需合并到仓库。</p><button class="button" type="button" data-action="export-journal">↓ 导出 curated.json</button><p class="section-note">提交时请合并已有 curated.json，保留相同事件 ID，才能生成更正记录。</p></form>`)}</div></div>` +
    panel(
      "待核查事件",
      data.alerts
        .map(
          (a) =>
            `<div class="event-card"><div class="event-top">${badge(a.level, a.level === "P0" ? "red" : "orange")}<span>${esc(projectName(a.projectId))}</span></div><h3>${esc(a.title)}</h3><p>${esc(a.reason)}</p><div class="event-meta">${time(a.at)} ${link(a.url)}</div></div>`,
        )
        .join("") ||
        empty(
          "没有已触发的规则",
          "请同时检查数据覆盖；缺失数据不等于风险为零。",
        ),
    )
  );
}
function showProject(id) {
  const p = data.projects.find((p) => p.id === id);
  if (!p) return;
  $("#detail-content").innerHTML =
    `<div class="eyebrow">PROJECT / ASSET IDENTITY</div><h2>${esc(p.name)}</h2><div class="chips">${p.ecosystems.map((e) => badge(e, "orange")).join("")}${badge(p.identityStatus)}</div><div class="detail-grid"><div class="detail-cell"><span>协议全名</span>${esc(p.protocol)}</div><div class="detail-cell"><span>网络</span>${esc(p.network)}</div></div><p>${esc(p.visibility)}</p>${link(p.officialUrl, "配置的项目入口 ↗")}<h3>资产身份与行情口径</h3>${
      p.assets
        .map((a) => {
          const m = data.markets.find((m) => m.assetId === a.id);
          return `<div class="detail-asset"><strong>${esc(a.symbol)} · ${esc(a.network)}</strong> ${badge(a.identityStatus)}<code>${esc(a.uniqueId || "唯一标识 N/A")}</code>${a.identitySource ? link(a.identitySource, "身份参考 ↗") : ""}<p>${esc(m?.reason || (!a.marketEnabled ? "行情未启用，等待身份与市场映射复核。" : "现货聚合数据；实际端点详见原始快照。"))}</p>${m ? `<p>报价 ${time(m.quotedAt)}；原始币种 ${esc(m.originalQuoteCurrency)}<br>24h 端点：${time(m.returns?.["24h"]?.endpoints?.asset?.[0]?.time)} → ${time(m.returns?.["24h"]?.endpoints?.asset?.[1]?.time)}<br>7d 端点：${time(m.returns?.["7d"]?.endpoints?.asset?.[0]?.time)} → ${time(m.returns?.["7d"]?.endpoints?.asset?.[1]?.time)}<br>${esc(m.returns?.["24h"]?.reason || "")} ${esc(m.returns?.["7d"]?.reason || "")}</p>` : ""}</div>`;
        })
        .join("") || "<p>未选择代币，价格不适用。继续跟踪产品与基础设施。</p>"
    }<h3>专属监控指标</h3><ul class="detail-list">${p.metrics.map((m) => `<li>${esc(m)}</li>`).join("")}</ul><p>未接入指标源时为 N/A，不使用公开局部数据推断全网。</p>${data.metrics
      .filter((m) => m.projectId === id)
      .map(
        (m) =>
          `<p>${esc(m.name)}：${esc(m.value)} ${esc(m.unit || "")} · ${esc(m.scope)} · ${time(m.observedAt)} ${link(m.url)}</p>`,
      )
      .join("")}`;
  $("#detail-dialog").showModal();
}
function render() {
  if (!data) return;
  const route = location.hash.slice(1) || "overview";
  const page = names[route] ? route : "overview";
  $("#breadcrumb").textContent = names[page];
  document.title = names[page] + " · BTC Observatory";
  document.querySelectorAll("[data-nav]").forEach((a) => {
    a.classList.toggle("active", a.dataset.nav === page);
    if (a.dataset.nav === page) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  $("#nav-news").textContent = data.events.filter((e) =>
    inWindow(e.publishedAt, data.window.cutoff, 7),
  ).length;
  $("#main").innerHTML = {
    overview,
    projects: projectsPage,
    news: newsPage,
    feedback: feedbackPage,
    markets: marketsPage,
    reports: reportsPage,
    settings: settingsPage,
  }[page]();
}
async function load() {
  const btn = $("#refresh");
  btn.disabled = true;
  try {
    const [s, c, r, a] = await Promise.all([
      fetch("./data/snapshot.json", { cache: "no-store" }),
      fetch("./data/config.json", { cache: "no-store" }),
      fetch("./data/daily.md", { cache: "no-store" }),
      fetch("./data/archive-index.json", { cache: "no-store" }),
    ]);
    if (!s.ok || !c.ok) throw Error("快照或配置文件不可用");
    data = await s.json();
    config = await c.json();
    if (data.schemaVersion !== 1) throw Error("快照版本不受支持");
    validateConfig(config);
    markdown = r.ok ? await r.text() : "";
    archive = a.ok ? await a.json() : [];
    if (!Array.isArray(archive)) archive = [];
    render();
  } catch (e) {
    $("#main").innerHTML =
      heading(
        "数据暂时不可用",
        "静态文件加载失败；请检查部署目录或稍后重新读取。",
      ) + empty("无法加载监控快照", e.message);
    notify("加载失败：" + e.message);
  } finally {
    btn.disabled = false;
  }
}
$("#refresh").addEventListener("click", load);
window.addEventListener("hashchange", () => {
  render();
  window.scrollTo(0, 0);
});
$(".dialog-close").addEventListener("click", () => $("#detail-dialog").close());
$("#detail-dialog").addEventListener("click", (e) => {
  if (e.target === $("#detail-dialog")) $("#detail-dialog").close();
});
document.addEventListener("input", (e) => {
  if (e.target.id === "project-search") {
    filters.query = e.target.value;
    $("#project-results").innerHTML = projectTable(
      filterProjects(data.projects, { ...filters, favorites }),
    );
  }
});
document.addEventListener("change", (e) => {
  if (e.target.name === "recordKind") {
    $("#feedback-fields").hidden = e.target.value !== "feedback";
  }
  if (e.target.id === "ecosystem-filter") {
    filters.ecosystem = e.target.value;
    $("#project-results").innerHTML = projectTable(
      filterProjects(data.projects, { ...filters, favorites }),
    );
  }
  if (e.target.id === "news-window")
    $("#news-results").innerHTML = newsList(e.target.value);
});
document.addEventListener("click", (e) => {
  const el = e.target.closest("button");
  if (!el) return;
  if (el.dataset.project) showProject(el.dataset.project);
  if (el.dataset.favorite) {
    const id = el.dataset.favorite;
    favorites = favorites.includes(id)
      ? favorites.filter((x) => x !== id)
      : [...favorites, id];
    persist("favorites", favorites);
    render();
  }
  if (el.dataset.starFilter) {
    filters.starred = el.dataset.starFilter === "starred";
    render();
  }
  try {
    switch (el.dataset.action) {
      case "download-report":
        download(
          `btc-daily-${data.window.cutoff.slice(0, 10)}.md`,
          markdown,
          "text/markdown",
        );
        break;
      case "download-json":
        download("snapshot.json", JSON.stringify(data, null, 2));
        break;
      case "save-config":
        draft = validateConfig(JSON.parse($("#config-editor").value));
        persist("config", draft);
        notify("草稿已保存；导出并提交仓库后生效");
        break;
      case "export-config":
        draft = validateConfig(JSON.parse($("#config-editor").value));
        download("config.json", JSON.stringify(draft, null, 2) + "\n");
        break;
      case "reset-config":
        draft = null;
        localStorage.removeItem("btc-observatory:config");
        render();
        notify("已恢复仓库配置");
        break;
      case "export-journal":
        download("curated.json", JSON.stringify(journal, null, 2) + "\n");
        break;
    }
  } catch (err) {
    notify(err.message);
  }
});
document.addEventListener("submit", (e) => {
  if (e.target.id !== "evidence-form") return;
  e.preventDefault();
  const f = new FormData(e.target),
    url = String(f.get("url"));
  if (!url.startsWith("https://")) {
    notify("原始链接必须是 HTTPS");
    return;
  }
  const record = {
    id: "manual-" + crypto.randomUUID(),
    projectId: f.get("projectId"),
    title: f.get("title"),
    url,
    evidence: f.get("evidence"),
    status: f.get("status"),
    summary: f.get("summary"),
    type: "manual",
    publishedAt: f.get("publishedAt")
      ? new Date(f.get("publishedAt") + "Z").toISOString()
      : null,
    effectiveAt: f.get("effectiveAt")
      ? new Date(f.get("effectiveAt") + "Z").toISOString()
      : null,
  };
  if (f.get("recordKind") === "feedback") {
    if (!String(f.get("author") || "").trim()) {
      notify("原始反馈必须填写报告账号");
      return;
    }
    journal.feedback.push({
      ...record,
      evidence: "user_report",
      author: f.get("author"),
      platform: f.get("platform"),
      problemKey: f.get("problemKey") || url,
      reproduction: f.get("reproduction"),
      teamResponse: f.get("teamResponse") || "尚未取得团队回应",
      isBot: false,
      updatedAt: null,
    });
  } else {
    journal.events.push(record);
  }
  persist("journal", journal);
  render();
  notify("核查草稿已保存，请导出后合并到仓库");
});
load();
