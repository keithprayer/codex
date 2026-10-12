"""Deterministic Markdown report; no generated claims or price attribution."""
from datetime import timedelta
from .core import parse_time, within


def safe(value):
    return str(value if value is not None else "N/A").replace("|", "\\|").replace("\n", " ").replace("\r", " ").replace("<", "&lt;").replace(">", "&gt;")


def number(value, suffix=""):
    return "N/A" if value is None else f"{value:,.4f}{suffix}"


def report(data):
    w = data["window"]
    cutoff = parse_time(w["cutoff"])
    names = {p["id"]: p["name"] for p in data["projects"]}
    lines = [f"# BTC 生态每日简报 · {w['cutoff'][:10]}", "", f"UTC 截止：{w['cutoff']}",
             f"24h 窗口：({w['start24h']}, {w['cutoff']}]", f"7d 窗口：({w['start7d']}, {w['cutoff']}]",
             f"未来 7 日：({w['cutoff']}, {w['end7d']}]", "",
             f"范围：{len(data['projects'])} 个项目组；至少一个来源成功核查 {data['coverage']['checkedProjects']} 个。",
             "自动来源覆盖不等于完整项目核查；社交平台、私有网络和人工审阅仍可能缺失。", "",
             "## 公告与单项目更新", ""]
    labels = {"confirmed": "已确认记录", "statement": "项目方声明", "user_report": "用户报告", "inference": "分析推断"}
    for p in data["projects"]:
        lines += [f"### {safe(p['name'])}", f"协议：{safe(p['protocol'])}；网络：{safe(p['network'])}；身份：{safe(p['identityStatus'])}。", f"可见范围：{safe(p['visibility'])}"]
        events = [e for e in data["events"] if e["projectId"] == p["id"] and within(e.get("publishedAt"), cutoff - timedelta(days=7), cutoff)]
        for e in events:
            lines.append(f"- 【{labels[e['evidence']]} / {safe(e['status'])}】{safe(e['title'])}；公布 {safe(e.get('publishedAt'))}；生效 {safe(e.get('effectiveAt'))}；[原文]({e['url']})。{safe(e.get('summary', ''))}")
        if not events:
            checked = [s for s in data["sources"] if s["projectId"] == p["id"] and s["kind"] in ("releases", "feed") and s["status"] == "ok"]
            if checked:
                lines.append("- 已成功核查的下列公告来源未发现窗口内新增（不覆盖其他来源）：" + "、".join(f"[{safe(s['name'])}]({s['url']}) @ {s['checkedAt']}" for s in checked))
            else:
                lines.append("- 公告来源覆盖不足，无法判断有无新增。")
        for m in [x for x in data["metrics"] if x["projectId"] == p["id"]]:
            lines.append(f"- 指标 {safe(m['name'])}：{safe(m.get('value'))} {safe(m.get('unit', ''))}；范围 {safe(m['scope'])}；观察 {m['observedAt']}；[来源]({m['url']})")
        lines.append("")
    lines += ["## 原始反馈（按问题合并）", "", "样本按平台账号去重；跨平台身份未经确认，不能代表全部用户。", ""]
    for g in data["feedbackGroups"]:
        lines.append(f"- **{safe(names[g['projectId']])} / {safe(g['title'])}**：24h {g['independent24h']}，7d {g['independent7d']} 个独立账号。")
        for r in g["reports"]:
            lines.append(f"  - [{safe(r.get('author'))} / {safe(r['platform'])}]({r['url']})：公布 {safe(r.get('publishedAt'))}；更新 {safe(r.get('updatedAt'))}；复现 {safe(r.get('reproduction', '未核查'))}；状态 {safe(r.get('status', 'unknown'))}；团队回应 {safe(r.get('teamResponse', 'N/A'))}。")
    if not data["feedbackGroups"]:
        lines.append("未取得可列示反馈；请检查来源状态，不能推断没有问题。")
    lines += ["", "## 行情", "", "| 资产 / 网络 | USD | sats | 24h | 7d | 相对 BTC 24h / 7d | 24h 成交额 USD | 报价时间 / 来源 |", "|---|---:|---:|---:|---:|---:|---:|---|"]
    markets = {m["assetId"]: m for m in data["markets"]}
    for p in data["projects"]:
        if not p["assets"]:
            lines.append(f"| {safe(p['name'])}（协议/产品） | 不适用 | 不适用 | 不适用 | 不适用 | 不适用 | 不适用 | 未选择代币 |")
        for a in p["assets"]:
            m = markets.get(a["id"], {})
            r1, r7 = m.get("returns", {}).get("24h", {}), m.get("returns", {}).get("7d", {})
            source = f"{safe(m.get('quotedAt'))} [来源]({m['url']})" if m else "身份待核验或尚未采集"
            lines.append(f"| {safe(a['symbol'])} / {safe(a['network'])} | {number(m.get('usd'))} | {number(m.get('sats'))} | {number(r1.get('usd'), '%')} | {number(r7.get('usd'), '%')} | {number(r1.get('relativeBtc'), '%')} / {number(r7.get('relativeBtc'), '%')} | {number(m.get('volume24hUsd'))} | {source} |")
    lines += ["", "收益只在历史端点符合时间容差且与 BTC 对齐时计算；实际端点、原始币种见 snapshot.json。成交额为报价时刻的提供方滚动窗口。", "",
              "| 资产 | 场所 / 币种 | 价差 | 买盘 −2% / 卖盘 +2% USD | 指定金额买 / 卖滑点 | 时刻 |", "|---|---|---:|---:|---:|---|"]
    for m in data["markets"]:
        b = m.get("orderbook") or {}
        lines.append(f"| {m['symbol']} | {safe(b.get('venue'))} / {safe(b.get('quoteCurrency'))} | {number(b.get('spreadPct'), '%')} | {number(b.get('bidDepth2PctUsd'))} / {number(b.get('askDepth2PctUsd'))} | {number(b.get('buySlippagePct'), '%')} / {number(b.get('sellSlippagePct'), '%')} | {safe(b.get('observedAt'))} |")
        if m.get("reason"):
            lines.append(f"\n{m['symbol']} 数据缺口：{safe(m['reason'])}\n")
    lines += ["", f"滑点名义金额 {data['settings']['tradeSizeUsd']} USD，不含手续费。未配置原始盘口或盘口不足时为 N/A。", "", "## 预警与待核查", ""]
    for a in data["alerts"]:
        lines.append(f"- {a['level']} / {a['state']}：{safe(names.get(a['projectId'], a['projectId']))} — {safe(a['title'])}；{safe(a['reason'])}；{safe(a.get('at'))}；[来源]({a['url']})")
    if not data["alerts"]:
        lines.append("当前可用数据未触发配置阈值；缺失字段不参与阈值判定，不能视为安全证明。")
    lines += ["", "## 未来 7 日", ""]
    future = [e for e in data["events"] if within(e.get("effectiveAt"), cutoff, cutoff + timedelta(days=7))]
    for e in sorted(future, key=lambda x: x["effectiveAt"]):
        lines.append(f"- {e['effectiveAt']}：{safe(e['title'])}（{e['status']}）；原公布 {safe(e.get('publishedAt'))}；[原文]({e['url']})")
    if not future:
        lines.append("未取得经过标时的未来事件。此处不代表未来没有解锁、升级或活动。")
    lines += ["", "## 来源覆盖与过期数据", "", "| 来源 | 类型 | 状态 | 核查 UTC | 缺口 |", "|---|---|---|---|---|"]
    for s in data["sources"]:
        lines.append(f"| [{safe(s['name'])}]({s['url']}) | {s['kind']} | {s['status']} | {safe(s.get('checkedAt'))} | {safe(s.get('error', ''))} |")
    lines += ["", "## 关键变化与更正", ""]
    for c in data["corrections"]:
        lines.append(f"- {c['at']} / {c['eventId']}：{safe(c['before'])} → {safe(c['after'])}；[来源]({c['url']})")
    if not data["corrections"]:
        lines.append("无已记录更正；首次采集仅建立基线。")
    return "\n".join(lines) + "\n"
