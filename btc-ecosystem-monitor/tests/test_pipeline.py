import copy
import json
from pathlib import Path
import unittest
from monitor.collect import collect
from monitor.core import parse_time
from monitor.providers import github_feedback, feed_events
from monitor.report import report
from monitor.validate import validate_config, validate_curated

ROOT=Path(__file__).resolve().parents[1]
T=parse_time("2026-10-12T06:00:00Z")
CONFIG=json.loads((ROOT/"config.json").read_text())


class FailClient:
    def get(self,*a,**kw):raise ValueError("HTTP 403")


class PipelineTests(unittest.TestCase):
    def test_offline_never_claims_success(self):
        data=collect(CONFIG,{}, {},FailClient(),T,True)
        self.assertEqual(data["coverage"]["checkedProjects"],0)
        self.assertEqual(data["mode"],"uncollected")
        self.assertNotIn("未发现窗口内新增",report(data))
        self.assertIn("公告来源覆盖不足",report(data))

    def test_failed_collection_is_not_no_news(self):
        data=collect(CONFIG,{}, {},FailClient(),T)
        self.assertGreater(data["coverage"]["failedSources"],0)
        self.assertNotIn("未发现窗口内新增",report(data))
        self.assertIn("HTTP 403",report(data))

    def test_identity_gate(self):
        config=copy.deepcopy(CONFIG)
        config["projects"][4]["assets"][0]["marketEnabled"]=True
        with self.assertRaises(ValueError):validate_config(config)
        validate_config(CONFIG)

    def test_duplicate_assets_rejected(self):
        config=copy.deepcopy(CONFIG)
        config["projects"][1]["assets"].append(copy.deepcopy(config["projects"][1]["assets"][0]))
        with self.assertRaises(ValueError):validate_config(config)

    def test_naive_dates_rejected(self):
        event={"id":"x","projectId":"rgb","url":"https://rgb.info/news","title":"news","publishedAt":"2026-10-12","evidence":"statement","status":"planned"}
        with self.assertRaises(ValueError):validate_curated({"events":[event]},CONFIG)
        event["publishedAt"]=None
        validate_curated({"events":[event]},CONFIG)

    def test_github_prs_excluded_and_old_created_times_preserved(self):
        class Client:
            def get(self,url):return [
                {"pull_request":{},"updated_at":"2026-10-11T00:00:00Z"},
                {"id":1,"number":1,"title":"issue","html_url":"https://github.com/a/b/issues/1","created_at":"2026-09-01T00:00:00Z","updated_at":"2026-10-11T00:00:00Z","state":"open","user":{"login":"alice"}}
            ]
        rows,complete=github_feedback(Client(),"a/b","rgb",T)
        self.assertTrue(complete)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["publishedAt"],"2026-09-01T00:00:00Z")

    def test_feed_truncation_and_unknown_dates(self):
        class Client:
            def get(self,*a,**kw):return b'<rss><channel><item><title>A</title><link>https://example.com/a</link><pubDate>Sun, 11 Oct 2026 08:00:00 +0000</pubDate></item></channel></rss>'
        rows,complete=feed_events(Client(),"https://example.com/feed","rgb",T)
        self.assertEqual(len(rows),1)
        self.assertFalse(complete)

    def test_all_protocols_have_explicit_visibility(self):
        covered=set()
        for p in CONFIG["projects"]:
            covered.update(p["ecosystems"])
            self.assertTrue(p["visibility"])
            self.assertTrue(p["metrics"])
        self.assertTrue({"RGB","Taproot Assets","Lightning","BRC20","CRC20","ARC20","CAT20","Runes"}<=covered)


if __name__=="__main__":unittest.main()

class MarketTests(unittest.TestCase):
    def test_market_timestamp_alignment_and_returns(self):
        from monitor.providers import market_rows
        from datetime import timedelta
        class Client:
            def get(self,url):
                if '/coins/markets?' in url:
                    return [
                        {'id':'bitcoin','current_price':100,'last_updated':'2026-10-12T06:00:00Z','total_volume':1000},
                        {'id':'blockstack','current_price':2,'last_updated':'2026-10-12T06:00:00Z','total_volume':500}
                    ]
                values=[1,1.5,2] if '/blockstack/' in url else [80,90,100]
                return {'prices':[[(T-timedelta(days=d)).timestamp()*1000,v] for d,v in zip([7,1,0],values)]}
        p=CONFIG['projects'][-1]
        row=market_rows(Client(),[(p,p['assets'][0])],T,CONFIG['settings'])[0]
        self.assertEqual(row['sats'],2_000_000)
        self.assertAlmostEqual(row['returns']['7d']['usd'],100)
        self.assertAlmostEqual(row['returns']['7d']['relativeBtc'],60)
        self.assertIsNone(row['reason'])
