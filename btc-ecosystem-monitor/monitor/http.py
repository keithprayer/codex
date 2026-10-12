"""Bounded HTTPS reads; tokens are scoped to the intended API origin."""
import json
import os
import time
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Redirect refused: configure the final official source URL")


class Client:
    def __init__(self):
        self.opener = build_opener(NoRedirect)

    def get(self, url, as_json=True):
        host = urlsplit(url).hostname
        if urlsplit(url).scheme != "https":
            raise ValueError("HTTPS required")
        headers = {"User-Agent": "btc-ecosystem-monitor/1.0", "Accept": "application/json" if as_json else "application/rss+xml,application/atom+xml,application/xml,text/xml"}
        if host == "api.github.com" and os.getenv("GITHUB_TOKEN"):
            headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
        if host == "api.coingecko.com" and os.getenv("COINGECKO_API_KEY"):
            headers["x-cg-demo-api-key"] = os.environ["COINGECKO_API_KEY"]
        for attempt in range(3):
            try:
                with self.opener.open(Request(url, headers=headers), timeout=20) as response:
                    body = response.read(5_000_001)
                    if len(body) > 5_000_000:
                        raise ValueError("Response exceeds 5 MB")
                    return json.loads(body) if as_json else body
            except HTTPError as e:
                if e.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    raise ValueError(f"HTTP {e.code}") from None
                time.sleep(min(2 ** attempt, 4))
            except (URLError, TimeoutError) as e:
                raise ValueError("Network request failed or timed out") from e
