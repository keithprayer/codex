from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from .core import iso, parse_time, fingerprint, within, aligned_returns, orderbook_metrics, finite


def github_releases(client, repo, project_id, cutoff):
    rows = client.get(f"https://api.github.com/repos/{repo}/releases?per_page=100")
    if not isinstance(rows, list):
        raise ValueError("Unexpected release response")
    events = []
    for r in rows:
        if r.get("draft") or not within(r.get("published_at"), cutoff - timedelta(days=7), cutoff):
            continue
        events.append({"id": f"gh-release-{r['id']}", "projectId": project_id, "type": "release",
                       "title": f"{repo}: {r.get('name') or r['tag_name']}", "summary": (r.get("body") or "")[:4000],
                       "url": r["html_url"], "publishedAt": r["published_at"], "updatedAt": r.get("updated_at"),
                       "effectiveAt": None, "status": "published", "evidence": "statement",
                       "prerelease": r.get("prerelease", False), "note": "软件已发布；不代表网络升级已激活"})
    return events, len(rows) < 100


def github_feedback(client, repo, project_id, cutoff):
    records, complete = [], False
    since = iso(cutoff - timedelta(days=7))
    for page in range(1, 11):
        rows = client.get(f"https://api.github.com/repos/{repo}/issues?" + urlencode({"state": "all", "since": since, "sort": "updated", "direction": "desc", "per_page": 100, "page": page}))
        if not isinstance(rows, list):
            raise ValueError("Unexpected issues response")
        for r in rows:
            if "pull_request" in r or not within(r.get("updated_at"), cutoff - timedelta(days=7), cutoff):
                continue
            user = r.get("user") or {}
            records.append({"id": f"gh-issue-{r['id']}", "projectId": project_id,
                            "title": r["title"], "summary": (r.get("body") or "")[:3000], "url": r["html_url"],
                            "problemKey": f"{repo}#{r['number']}", "platform": "GitHub", "author": user.get("login"),
                            "isBot": user.get("type") == "Bot", "publishedAt": r["created_at"], "updatedAt": r["updated_at"],
                            "status": r["state"], "reproduction": "not_verified", "teamResponse": "未自动核查评论；Issue 关闭不等于独立验证修复",
                            "evidence": "user_report"})
        if len(rows) < 100:
            complete = True
            break
    return records, complete


def feed_events(client, url, project_id, cutoff):
    body = client.get(url, as_json=False)
    if b"<!DOCTYPE" in body.upper() or b"<!ENTITY" in body.upper():
        raise ValueError("XML entities are not accepted")
    root = ET.fromstring(body)
    events = []
    items = root.findall(".//item") or root.findall("{http://www.w3.org/2005/Atom}entry")
    if not items:
        raise ValueError("No parseable RSS/Atom entries; source coverage unknown")
    dates = []
    for item in items:
        def val(name):
            return item.findtext(name) or item.findtext("{http://www.w3.org/2005/Atom}" + name)
        raw_date = val("pubDate") or val("published") or val("updated")
        date = parse_time(raw_date)
        if not date and raw_date:
            try:
                date = parsedate_to_datetime(raw_date)
                if not date.tzinfo:
                    date = None
            except (ValueError, TypeError):
                pass
        if date:
            dates.append(date)
        link = val("link")
        if not link:
            node = item.find("{http://www.w3.org/2005/Atom}link")
            link = node.get("href") if node is not None else None
        if not link or not date or not cutoff - timedelta(days=7) < date <= cutoff:
            continue
        events.append({"id": "rss-" + fingerprint(link), "projectId": project_id, "type": "announcement",
                       "title": val("title") or "无标题公告", "summary": "请打开官方原文核查具体声明、计划与生效时间。",
                       "url": link, "publishedAt": iso(date), "effectiveAt": None, "status": "published", "evidence": "statement"})
    # A truncated feed cannot prove a whole seven-day window was covered.
    complete = len(dates) == len(items) and min(dates) <= cutoff - timedelta(days=7)
    return events, complete


def market_rows(client, assets, cutoff, settings):
    ids = sorted(set(["bitcoin"] + [a["coinGeckoId"] for _, a in assets]))
    endpoint = "https://api.coingecko.com/api/v3/coins/markets?" + urlencode({"vs_currency": "usd", "ids": ",".join(ids), "sparkline": "false"})
    response = client.get(endpoint)
    if not isinstance(response, list):
        raise ValueError("Unexpected market response")
    raw = {r["id"]: r for r in response}
    btc = raw.get("bitcoin", {})
    series, errors = {}, {}
    for coin in ids:
        try:
            result = client.get(f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=8")
            if not isinstance(result.get("prices"), list):
                raise ValueError("Missing price history")
            series[coin] = result["prices"]
        except Exception as e:
            series[coin], errors[coin] = [], str(e)
    markets = []
    for project, asset in assets:
        r = raw.get(asset["coinGeckoId"], {})
        price, btc_price = r.get("current_price"), btc.get("current_price")
        t, bt = parse_time(r.get("last_updated")), parse_time(btc.get("last_updated"))
        if not finite(price) or price <= 0:
            price = None
        synced = t and bt and abs((t - bt).total_seconds()) <= settings["crossAssetSkewSeconds"] and t <= cutoff and bt <= cutoff
        sats = price / btc_price * 1e8 if price and finite(btc_price) and btc_price > 0 and synced else None
        returns = {label: aligned_returns(series[asset["coinGeckoId"]], series["bitcoin"], cutoff, days,
                   settings["historyToleranceSeconds"], settings["crossAssetSkewSeconds"]) for label, days in [("24h", 1), ("7d", 7)]}
        if t and t > cutoff:
            price, sats = None, None
        markets.append({"assetId": asset["id"], "projectId": project["id"], "symbol": asset["symbol"], "network": asset["network"],
                        "usd": price, "sats": sats, "quotedAt": r.get("last_updated"), "btcQuotedAt": btc.get("last_updated"),
                        "collectedAt": iso(datetime.now(timezone.utc)), "originalQuoteCurrency": "USD", "provider": "CoinGecko aggregated spot",
                        "url": "https://www.coingecko.com/en/coins/" + asset["coinGeckoId"], "apiUrl": endpoint,
                        "volume24hUsd": r.get("total_volume") if price else None, "volumeWindow": "provider rolling 24h at quotedAt",
                        "returns": returns, "orderbook": None,
                        "history": [[x, y] for x, y in series[asset["coinGeckoId"]] if x <= cutoff.timestamp()*1000][-240:],
                        "reason": errors.get(asset["coinGeckoId"]) or errors.get("bitcoin") or ("报价缺失或晚于报告截止" if price is None else None) or next((r["reason"] for r in returns.values() if r["reason"]), None),
                        "marketScope": "聚合现货；交易所充提网络未逐一核对，不代表原生链成交量"})
    return markets


def kraken_book(client, pair, amount, cutoff):
    url = "https://api.kraken.com/0/public/Depth?" + urlencode({"pair": pair, "count": 500})
    raw = client.get(url)
    if raw.get("error"):
        raise ValueError("Kraken: " + ", ".join(raw["error"]))
    book = next(iter(raw["result"].values()))
    metrics = orderbook_metrics(book["bids"], book["asks"], amount)
    # Kraken per-level timestamps are last-change times, not snapshot times.
    metrics.update({"url": url, "pair": pair, "quoteCurrency": "USD", "venue": "Kraken", "observedAt": iso(cutoff),
                    "timestampBasis": "request retrieval time, not exchange snapshot timestamp", "depthScope": "最多 500 档；不足 ±2% 时为截断下界"})
    metrics["depthComplete"] = float(book["bids"][-1][0]) <= metrics["midUsd"]*.98 and float(book["asks"][-1][0]) >= metrics["midUsd"]*1.02
    return metrics
