"""Run: python -m monitor.collect [--offline] [--cutoff ISO_TIME]."""
import argparse
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from .core import iso, windows, dedupe_events, group_feedback, corrections, build_alerts, fingerprint, parse_time
from .http import Client
from .providers import github_releases, github_feedback, feed_events, market_rows, kraken_book
from .report import report
from .validate import validate_config, validate_curated


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)


def collect(config, curated, previous, client, cutoff, offline=False, archives=None):
    validate_config(config)
    validate_curated(curated, config)
    sources, events, feedback, markets = [], list(curated.get("events", [])), list(curated.get("feedback", [])), []
    def run(project, kind, name, url, fn):
        source = {"id": fingerprint(project + kind + url), "projectId": project, "kind": kind, "name": name,
                  "url": url, "checkedAt": None, "status": "not_checked", "error": None}
        sources.append(source)
        if offline:
            source["error"] = "尚未运行在线采集；此空状态不是无事件"
            return []
        source["checkedAt"] = iso(datetime.now(timezone.utc))
        try:
            records, complete = fn()
            source.update(status="ok" if complete else "partial", count=len(records), completedAt=iso(datetime.now(timezone.utc)), error=None if complete else "分页/订阅源长度不足以证明完整窗口覆盖")
            return records
        except Exception as exc:
            source.update(status="error", error=str(exc)[:220])
            return []
    for p in config["projects"]:
        for repo in p.get("repos", []):
            events += run(p["id"], "releases", repo + " releases", f"https://github.com/{repo}/releases", lambda: github_releases(client, repo, p["id"], cutoff))
            feedback += run(p["id"], "feedback", repo + " issues", f"https://github.com/{repo}/issues", lambda: github_feedback(client, repo, p["id"], cutoff))
        for url in p.get("feeds", []):
            events += run(p["id"], "feed", p["name"] + " RSS", url, lambda: feed_events(client, url, p["id"], cutoff))
        if not p.get("repos") and not p.get("feeds"):
            sources.append({"id": p["id"] + "-manual", "projectId": p["id"], "name": p["name"] + " 官方网站", "kind": "manual",
                            "url": p["officialUrl"], "checkedAt": None, "status": "not_configured", "error": "未配置可自动采集源；需人工核查公告与反馈"})
    assets = [(p, a) for p in config["projects"] for a in p["assets"] if a.get("marketEnabled")]
    if assets:
        # One aggregated request; separate provenance/status per project.
        market_source = {"id": "markets", "projectId": assets[0][0]["id"], "kind": "market", "name": "CoinGecko spot + history", "url": "https://www.coingecko.com/", "checkedAt": None, "status": "not_checked", "error": "尚未采集"}
        sources.append(market_source)
        if not offline:
            market_source["checkedAt"] = iso(datetime.now(timezone.utc))
            try:
                markets = market_rows(client, assets, cutoff, config["settings"])
                market_source.update(status="ok", error=None)
            except Exception as exc:
                market_source.update(status="error", error=str(exc)[:220])
        for p, a in assets:
            row = next((m for m in markets if m["assetId"] == a["id"]), None)
            status = dict(market_source, id="market-" + a["id"], projectId=p["id"], name=a["symbol"] + " 行情",
                          url="https://www.coingecko.com/en/coins/" + a["coinGeckoId"])
            if row and (row.get("usd") is None or row.get("reason")):
                status.update(status="partial", error=row.get("reason") or "报价缺失")
            sources.append(status)
            if row and a.get("krakenPair"):
                books = run(p["id"], "orderbook", a["krakenPair"] + " Kraken", "https://www.kraken.com/", lambda: ([kraken_book(client, a["krakenPair"], config["settings"]["tradeSizeUsd"], datetime.now(timezone.utc))], True))
                row["orderbook"] = books[0] if books else None
        sources.remove(market_source)
    history = list(archives or []) + ([previous] if previous else [])
    for m in markets:
        asset = next(a for p, a in assets if a["id"] == m["assetId"])
        old_rows = [old for snap in history for old in snap.get("markets", []) if old["assetId"] == m["assetId"] and old.get("provider") == m["provider"]]
        books = [old["orderbook"] for old in old_rows if old.get("orderbook") and parse_time(old["orderbook"].get("observedAt"))]
        target = cutoff.timestamp() - 86400
        if books:
            m["orderbook24hAgo"] = min(books, key=lambda b: abs(parse_time(b["observedAt"]).timestamp() - target))
        if asset.get("pegUsd") and asset.get("pegSource"):
            m["pegUsd"] = asset["pegUsd"]
            samples = {old.get("quotedAt"): {"time": old.get("quotedAt"), "usd": old.get("usd")} for old in old_rows + [m] if parse_time(old.get("quotedAt"))}
            m["pegSamples"] = [samples[key] for key in sorted(samples)][-2:]
    for source in sources:
        old = next((s for s in previous.get("sources", []) if s["id"] == source["id"]), {})
        source["consecutiveFailures"] = old.get("consecutiveFailures", 0) + 1 if source["status"] == "error" else 0
    events = dedupe_events(events)
    data = {"schemaVersion": 1, "mode": "uncollected" if offline else "collected", "generatedAt": iso(datetime.now(timezone.utc)),
            "window": windows(cutoff), "settings": config["settings"], "projects": config["projects"],
            "events": events, "feedbackGroups": group_feedback(feedback, cutoff), "markets": markets,
            "metrics": curated.get("metrics", []), "sources": sources,
            "corrections": corrections(previous, events, cutoff)}
    data["coverage"] = {"totalProjects": len(config["projects"]), "checkedProjects": len({s["projectId"] for s in sources if s["status"] == "ok"}),
                        "successfulSources": sum(s["status"] == "ok" for s in sources), "failedSources": sum(s["status"] == "error" for s in sources),
                        "completeProjects": None, "note": "成功核查来源数量不代表完整项目覆盖；未配置平台与私有数据不在覆盖范围。"}
    data["alerts"] = build_alerts(data, config["settings"])
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Generate honest empty state without network requests")
    parser.add_argument("--cutoff", help="ISO UTC cutoff; defaults to start of this run")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    cutoff = parse_time(args.cutoff) if args.cutoff else datetime.now(timezone.utc)
    if not cutoff:
        parser.error("--cutoff requires a timezone-aware ISO timestamp")
    root = args.root
    config, curated = read_json(root / "config.json"), read_json(root / "curated.json", {})
    path = root / "web/data/snapshot.json"
    previous = read_json(path, {})
    archives = [read_json(p) for p in sorted((root / "web/data/archive").glob("*.json"))[-90:]]
    data = collect(config, curated, previous, Client(), cutoff, args.offline, archives)
    encoded = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    atomic_write(path, encoded)
    atomic_write(root / "web/data/config.json", json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    markdown = report(data)
    atomic_write(root / "web/data/daily.md", markdown)
    # Keep the latest successful evidence/history even if the next run fails.
    # UTC timestamp filenames avoid same-day overwrites; archives remain explicit.
    if not args.offline:
        stamp = cutoff.strftime("%Y-%m-%dT%H%M%SZ")
        atomic_write(root / "web/data/archive" / (stamp + ".json"), encoded)
        atomic_write(root / "web/data/archive" / (stamp + ".md"), markdown)
        files = sorted((root / "web/data/archive").glob("*.json"), reverse=True)
        atomic_write(root / "web/data/archive-index.json", json.dumps([{"time": p.stem, "json": "archive/" + p.name, "markdown": "archive/" + p.with_suffix(".md").name} for p in files[:90]], indent=2))
        for expired in files[90:]:
            expired.unlink()
            expired.with_suffix(".md").unlink(missing_ok=True)
    print(json.dumps({"mode": data["mode"], "coverage": data["coverage"], "events": len(data["events"]), "markets": len(data["markets"])}))


if __name__ == "__main__":
    main()
