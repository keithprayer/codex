"""Pure calculations. Missing measurements are None, never zero."""
from datetime import datetime, timedelta, timezone
import hashlib
import math
import statistics
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


def parse_time(value):
    if not value or not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result.astimezone(timezone.utc) if result.tzinfo else None
    except ValueError:
        return None


def iso(value):
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def windows(cutoff):
    return {"cutoff": iso(cutoff), "start24h": iso(cutoff - timedelta(days=1)),
            "start7d": iso(cutoff - timedelta(days=7)), "end7d": iso(cutoff + timedelta(days=7))}


def within(value, start, end):
    parsed = parse_time(value)
    return parsed is not None and start < parsed <= end


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def canonical_url(url):
    p = urlsplit(url)
    if p.scheme != "https" or not p.hostname:
        raise ValueError("Source URL must use HTTPS")
    query = [(k, v) for k, v in parse_qsl(p.query) if not k.startswith("utm_")]
    return urlunsplit((p.scheme, p.netloc.lower(), p.path.rstrip("/"), urlencode(query), ""))


def fingerprint(value):
    return hashlib.sha256(value.encode()).hexdigest()[:20]


def dedupe_events(events):
    result = {}
    for event in events:
        key = (event["projectId"], event.get("dedupeKey") or canonical_url(event["url"]))
        if key not in result:
            result[key] = {**event, "sources": [event["url"]]}
        else:
            result[key]["sources"] = sorted(set(result[key]["sources"] + [event["url"]]))
    return list(result.values())


def nearest(points, target, tolerance=900):
    valid = [(float(t), float(v)) for t, v in points if finite(t) and finite(v) and v > 0
             and t <= target.timestamp() * 1000]
    if not valid:
        return None
    t, value = min(valid, key=lambda p: abs(p[0] - target.timestamp() * 1000))
    if target.timestamp() - t / 1000 > tolerance:
        return None
    return {"value": value, "time": iso(datetime.fromtimestamp(t / 1000, timezone.utc))}


def aligned_returns(asset_points, btc_points, cutoff, days, tolerance=900, max_skew=60):
    targets = [cutoff - timedelta(days=days), cutoff]
    asset = [nearest(asset_points, t, tolerance) for t in targets]
    btc = [nearest(btc_points, t, tolerance) for t in targets]
    if not all(asset + btc):
        return {"usd": None, "relativeBtc": None, "reason": "缺少窗口端点，或样本距目标超过容差", "endpoints": None}
    if any(abs((parse_time(a["time"]) - parse_time(b["time"])).total_seconds()) > max_skew
           for a, b in zip(asset, btc)):
        return {"usd": None, "relativeBtc": None, "reason": "资产与 BTC 样本时间不对齐", "endpoints": {"asset": asset, "btc": btc}}
    ratio = asset[1]["value"] / asset[0]["value"]
    btc_ratio = btc[1]["value"] / btc[0]["value"]
    return {"usd": (ratio - 1) * 100, "relativeBtc": (ratio / btc_ratio - 1) * 100,
            "reason": None, "endpoints": {"asset": asset, "btc": btc}}


def orderbook_metrics(bids, asks, amount_usd):
    """USD quote books only. Sell a base amount worth amount_usd at mid."""
    if not finite(amount_usd) or amount_usd <= 0:
        raise ValueError("Positive trade size required")
    def clean(levels, reverse):
        rows = [(float(x[0]), float(x[1])) for x in levels]
        if any(not finite(p) or not finite(q) or p <= 0 or q <= 0 for p, q in rows):
            raise ValueError("Invalid orderbook level")
        return sorted(rows, reverse=reverse)
    bids, asks = clean(bids, True), clean(asks, False)
    if not bids or not asks or bids[0][0] >= asks[0][0]:
        raise ValueError("Empty or crossed orderbook")
    mid = (bids[0][0] + asks[0][0]) / 2
    budget, bought = amount_usd, 0.0
    for p, q in asks:
        spend = min(budget, p * q)
        bought += spend / p
        budget -= spend
        if budget <= 1e-8:
            break
    remaining, received = amount_usd / mid, 0.0
    for p, q in bids:
        size = min(remaining, q)
        received += size * p
        remaining -= size
        if remaining <= 1e-8:
            break
    return {"midUsd": mid, "spreadPct": (asks[0][0] - bids[0][0]) / mid * 100,
            "bidDepth2PctUsd": sum(p*q for p,q in bids if p >= mid * .98),
            "askDepth2PctUsd": sum(p*q for p,q in asks if p <= mid * 1.02),
            "buySlippagePct": (amount_usd / bought / mid - 1) * 100 if budget <= 1e-8 else None,
            "sellSlippagePct": (1 - received / amount_usd) * 100 if remaining <= 1e-8 else None,
            "tradeSizeUsd": amount_usd, "includesFees": False,
            "reason": "盘口不足以完全成交" if budget > 1e-8 or remaining > 1e-8 else None}


def group_feedback(items, cutoff):
    groups = {}
    seen_urls = set()
    for item in items:
        original = (item["projectId"], canonical_url(item["url"]))
        if original in seen_urls:
            continue
        seen_urls.add(original)
        key = (item["projectId"], item.get("problemKey") or item["url"])
        group = groups.setdefault(key, {"projectId": key[0], "problemKey": key[1], "title": item["title"],
                                       "reports": [], "independent24h": 0, "independent7d": 0})
        if not any(r["url"] == item["url"] for r in group["reports"]):
            group["reports"].append(item)
    for group in groups.values():
        for days, name in [(1, "independent24h"), (7, "independent7d")]:
            authors = {(r["platform"], r["author"]) for r in group["reports"]
                       if r.get("author") and not r.get("isBot")
                       and within(r.get("publishedAt"), cutoff - timedelta(days=days), cutoff)}
            group[name] = len(authors)
        group["sampleNote"] = "按平台账号去重，跨平台身份未核验；样本不代表所有用户"
    return list(groups.values())


def build_alerts(data, settings):
    cutoff = parse_time(data["window"]["cutoff"])
    alerts = []
    def add(level, project, title, reason, url, at, state="待核查"):
        alerts.append({"id": fingerprint(project + title), "level": level, "projectId": project,
                       "title": title, "reason": reason, "url": url, "at": at, "state": state})
    for s in data["sources"]:
        if s["status"] in ("error", "partial", "not_configured"):
            add("P2", s["projectId"], "来源覆盖不完整", s.get("error") or s["status"], s["url"], s.get("checkedAt"))
    for m in data["markets"]:
        source_time = parse_time(m.get("quotedAt"))
        if not source_time or source_time > cutoff or (cutoff - source_time).total_seconds() > settings["staleMinutes"] * 60:
            add("P2", m["projectId"], m["symbol"] + " 报价时间缺失或过期", "不能确认当前价格及阈值", m["url"], m.get("quotedAt"))
            continue
        r = m.get("returns", {}).get("24h", {}).get("usd")
        if finite(r) and abs(r) > settings["priceChangePct"]:
            add("P1", m["projectId"], m["symbol"] + " 24h 价格波动", f"{r:+.2f}%，阈值 {settings['priceChangePct']}%", m["url"], m["quotedAt"])
        # Seven completed daily volumes must have been supplied and verified.
        base = m.get("previous7CompleteDailyVolumes", [])
        volume = m.get("volume24hUsd")
        if len(base) == 7 and all(finite(x) and x >= 0 for x in base) and finite(volume):
            median = statistics.median(base)
            if median > 0 and volume > median * settings["volumeMultiple"]:
                add("P1", m["projectId"], m["symbol"] + " 放量", "超过过去 7 个完整日成交额中位数阈值", m["url"], m["quotedAt"])
        book, old_book = m.get("orderbook") or {}, m.get("orderbook24hAgo") or {}
        t, old_t = parse_time(book.get("observedAt")), parse_time(old_book.get("observedAt"))
        if t and old_t and abs((t-old_t).total_seconds() - 86400) <= 900 and book.get("venue") == old_book.get("venue") and book.get("pair") == old_book.get("pair") and book.get("depthComplete") and old_book.get("depthComplete"):
            for side in ("bidDepth2PctUsd", "askDepth2PctUsd"):
                current, old = book.get(side), old_book.get(side)
                if finite(current) and finite(old) and old > 0 and (1-current/old)*100 > settings["depthDropPct"]:
                    add("P1", m["projectId"], m["symbol"] + " 盘口深度下降", f"{side} 相对 24h 前下降超过 {settings['depthDropPct']}%", book["url"], book["observedAt"])
        peg = m.get("pegUsd")
        samples = m.get("pegSamples", [])[-2:]
        times = [parse_time(x.get("time")) for x in samples]
        if finite(peg) and peg > 0 and len(samples) == 2 and all(times) and times[0] < times[1] <= cutoff and (cutoff-times[0]).total_seconds() <= settings["staleMinutes"]*60:
            if all(finite(x.get("usd")) and abs(x["usd"]/peg-1)*100 > settings["depegPct"] for x in samples):
                add("P1", m["projectId"], m["symbol"] + " 连续两次偏离锚定值", f"超过 {settings['depegPct']}%；价格偏离原因待核查", m["url"], m["quotedAt"])
    for group in data["feedbackGroups"]:
        severe = any(r.get("severity") == "severe" and r.get("reproduction") == "independently_reproduced" for r in group["reports"])
        if group["independent24h"] >= settings["feedbackSamples"] or severe:
            r = group["reports"][0]
            add("P1", group["projectId"], group["title"], f"24h 独立账号 {group['independent24h']}；严重独立复现 {severe}", r["url"], r.get("publishedAt"))
    for e in data["events"]:
        if e.get("riskLevel") == "P0" and e.get("evidence") == "confirmed":
            add("P0", e["projectId"], e["title"], "经人工核实的严重事件", e["url"], e.get("publishedAt"), "已确认")
        unlock = e.get("unlockPctCirculating")
        if e.get("evidence") in ("confirmed", "statement") and finite(unlock) and unlock > settings["unlockPct"] and within(e.get("effectiveAt"), cutoff, cutoff + timedelta(days=7)):
            add("P1", e["projectId"], e["title"], f"计划解锁占流通量 {unlock}%（需核查实际执行）", e["url"], e["effectiveAt"])
    return sorted(alerts, key=lambda x: (x["level"], x["projectId"], x["title"]))


def corrections(previous, events, cutoff):
    old = {e["id"]: e for e in previous.get("events", [])}
    changes = list(previous.get("corrections", []))
    for e in events:
        if e["id"] in old:
            fields = [k for k in ("title", "status", "evidence", "effectiveAt", "summary") if old[e["id"]].get(k) != e.get(k)]
            if fields:
                changes.append({"eventId": e["id"], "at": iso(cutoff), "fields": fields,
                                "before": {k: old[e["id"]].get(k) for k in fields},
                                "after": {k: e.get(k) for k in fields}, "url": e["url"]})
    return changes[-200:]
