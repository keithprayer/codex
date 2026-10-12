"""Reject ambiguous or malformed configuration before making network requests."""
import re
from .core import canonical_url, finite, parse_time


def validate_config(config):
    if config.get("schemaVersion") != 1:
        raise ValueError("Unsupported configuration schema")
    ids, asset_ids = set(), set()
    for key in ("tradeSizeUsd", "staleMinutes", "priceChangePct", "volumeMultiple", "depthDropPct", "feedbackSamples", "unlockPct", "depegPct", "historyToleranceSeconds", "crossAssetSkewSeconds"):
        if not finite(config.get("settings", {}).get(key)) or config["settings"][key] <= 0:
            raise ValueError(f"Invalid setting: {key}")
    for p in config["projects"]:
        if not re.fullmatch(r"[a-z0-9-]+", p["id"]) or p["id"] in ids:
            raise ValueError("Invalid or duplicated project ID")
        ids.add(p["id"])
        canonical_url(p["officialUrl"])
        if not p.get("name") or not p.get("network") or not p.get("protocol") or not p.get("ecosystems"):
            raise ValueError("Project identity is incomplete")
        for repo in p.get("repos", []):
            if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
                raise ValueError("Invalid GitHub repository")
        for url in p.get("feeds", []):
            canonical_url(url)
        for a in p.get("assets", []):
            if not a.get("id") or a["id"] in asset_ids:
                raise ValueError("Duplicated asset ID")
            asset_ids.add(a["id"])
            if a.get("marketEnabled"):
                if a.get("identityStatus") != "verified" or not a.get("uniqueId") or not a.get("network") or not a.get("standard") or not a.get("identitySource"):
                    raise ValueError(f"Market requires verified asset identity: {a['id']}")
                canonical_url(a["identitySource"])
                if not re.fullmatch(r"[a-z0-9-]+", a.get("coinGeckoId", "")):
                    raise ValueError("Invalid CoinGecko ID")
                if "CRC20" in p["ecosystems"] and (p.get("identityStatus") != "verified" or "待核实" in p["protocol"]):
                    raise ValueError("CRC20 requires a verified full protocol name and network")
                if a.get("krakenPair") and not re.fullmatch(r"[A-Z0-9]+USD", a["krakenPair"]):
                    raise ValueError("Orderbook adapter supports explicitly configured USD pairs only")


def validate_curated(curated, config):
    ids = {p["id"] for p in config["projects"]}
    seen = set()
    for kind in ("events", "feedback", "metrics"):
        for r in curated.get(kind, []):
            if r.get("projectId") not in ids:
                raise ValueError("Unknown project in curated record")
            canonical_url(r["url"])
            if not r.get("id") or r["id"] in seen:
                raise ValueError("Each curated record needs a unique ID")
            seen.add(r["id"])
            for key in ("publishedAt", "effectiveAt", "updatedAt", "observedAt"):
                if r.get(key) and not parse_time(r[key]):
                    raise ValueError(f"{key} requires an ISO timestamp with timezone; unknown time must be null")
            if kind == "events":
                if not r.get("title") or r.get("evidence") not in ("confirmed", "statement", "user_report", "inference"):
                    raise ValueError("Event requires title and evidence label")
                if r.get("status") not in ("planned", "published", "completed", "open", "resolved", "unknown"):
                    raise ValueError("Invalid event status")
            if kind == "feedback" and (not r.get("author") or not r.get("platform") or not r.get("title")):
                raise ValueError("Feedback requires an original author, platform and title")
            if kind == "metrics" and (not r.get("name") or not r.get("scope") or not r.get("observedAt")):
                raise ValueError("Metric requires name, observation time and visibility scope")
