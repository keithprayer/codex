export const labels = {
  confirmed: "已确认事实",
  statement: "项目方声明",
  user_report: "用户报告",
  inference: "分析推断",
  planned: "计划",
  published: "已发布",
  completed: "已完成",
  open: "开放",
  closed: "已关闭",
  resolved: "已解决",
  unknown: "待核查",
  verified: "已核实",
  protocol_only: "协议 / 产品",
  reference_only: "参考身份 · 待复核",
  review_required: "待复核",
  unverified: "未核实",
  ok: "核查成功",
  error: "采集失败",
  partial: "部分覆盖",
  not_checked: "尚未采集",
  not_configured: "未配置",
  not_verified: "未独立复现",
  independently_reproduced: "已独立复现",
};
export const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
export function safeUrl(value) {
  try {
    const u = new URL(value);
    return u.protocol === "https:" ? u.href : "#";
  } catch {
    return "#";
  }
}
export const link = (url, title = "原始来源 ↗") =>
  `<a href="${esc(safeUrl(url))}" target="_blank" rel="noopener noreferrer">${esc(title)}</a>`;
export const format = (v, digits = 2) =>
  typeof v === "number" && Number.isFinite(v)
    ? new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(
        v,
      )
    : "N/A";
export const percent = (v) =>
  typeof v === "number" && Number.isFinite(v)
    ? `${v > 0 ? "+" : ""}${v.toFixed(2)}%`
    : "N/A";
export const time = (value) =>
  value && Number.isFinite(Date.parse(value))
    ? new Date(value).toISOString().replace("T", " ").replace(".000Z", " UTC")
    : "时间 N/A";
export function inWindow(value, cutoff, days) {
  const v = Date.parse(value),
    end = Date.parse(cutoff);
  return Number.isFinite(v) && v > end - days * 86400000 && v <= end;
}
export function filterProjects(
  projects,
  { query = "", ecosystem = "all", starred = false, favorites = [] } = {},
) {
  return projects.filter(
    (p) =>
      (!query ||
        `${p.name} ${p.network} ${p.assets.map((a) => a.symbol).join(" ")}`
          .toLowerCase()
          .includes(query.toLowerCase())) &&
      (ecosystem === "all" || p.ecosystems.includes(ecosystem)) &&
      (!starred || favorites.includes(p.id)),
  );
}
export function readStored(storage, key, fallback) {
  try {
    const value = storage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
}
export function chartPath(points, width = 240, height = 55) {
  const valid = points.filter(
    (p) => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite),
  );
  if (valid.length < 2) return "";
  const ys = valid.map((p) => p[1]),
    lo = Math.min(...ys),
    range = Math.max(...ys) - lo || 1;
  return valid
    .map(
      (p, i) =>
        `${i ? "L" : "M"}${((i / (valid.length - 1)) * width).toFixed(1)},${(height - ((p[1] - lo) / range) * (height - 8) - 4).toFixed(1)}`,
    )
    .join(" ");
}
export function validateConfig(config) {
  if (
    config.schemaVersion !== 1 ||
    !Array.isArray(config.projects) ||
    !config.settings
  )
    throw Error("配置格式不正确");
  const ids = new Set(),
    assets = new Set();
  for (const p of config.projects) {
    if (
      !/^[a-z0-9-]+$/.test(p.id) ||
      ids.has(p.id) ||
      !p.name ||
      !p.network ||
      !p.protocol ||
      !Array.isArray(p.ecosystems) ||
      !Array.isArray(p.assets) ||
      safeUrl(p.officialUrl) === "#"
    )
      throw Error("项目身份不完整或 ID 重复");
    ids.add(p.id);
    for (const a of p.assets) {
      if (!a.id || assets.has(a.id)) throw Error("资产 ID 重复或缺失");
      assets.add(a.id);
      if (
        a.marketEnabled &&
        (a.identityStatus !== "verified" ||
          !a.uniqueId ||
          !a.network ||
          !a.standard ||
          !a.coinGeckoId ||
          safeUrl(a.identitySource) === "#")
      )
        throw Error(`${a.symbol} 启用行情前必须核实网络、唯一标识及来源`);
      if (
        a.marketEnabled &&
        p.ecosystems.includes("CRC20") &&
        (p.identityStatus !== "verified" || p.protocol.includes("待核实"))
      )
        throw Error("CRC20 必须核实协议全名与网络");
    }
  }
  for (const [key, v] of Object.entries(config.settings))
    if (typeof v !== "number" || !Number.isFinite(v) || v <= 0)
      throw Error(`设置 ${key} 必须是正数`);
  return config;
}
export function download(filename, content, type = "application/json") {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
