import unittest
from datetime import timedelta
from monitor.core import *

T = parse_time("2026-10-12T06:00:00Z")


class CoreTests(unittest.TestCase):
    def test_utc_and_boundaries(self):
        self.assertEqual(iso(parse_time("2026-10-12T14:00:00+08:00")), iso(T))
        self.assertIsNone(parse_time("2026-10-12"))
        self.assertFalse(within(iso(T-timedelta(days=1)), T-timedelta(days=1), T))
        self.assertTrue(within(iso(T), T-timedelta(days=1), T))

    def test_dedupe_keeps_source_and_project_scope(self):
        a = {"projectId":"a", "url":"https://example.com/update?utm_source=x", "id":"1"}
        b = dict(a, url="https://example.com/update", id="2")
        c = dict(b, projectId="c")
        self.assertEqual(len(dedupe_events([a,b,c])), 2)
        self.assertEqual(len(dedupe_events([a,b])[0]["sources"]), 2)

    def test_relative_btc_is_ratio_not_subtraction(self):
        start, end = (T-timedelta(days=1)).timestamp()*1000, T.timestamp()*1000
        r = aligned_returns([[start,100],[end,110]], [[start,100],[end,105]], T, 1)
        self.assertAlmostEqual(r["usd"],10)
        self.assertAlmostEqual(r["relativeBtc"],(1.1/1.05-1)*100)

    def test_missing_or_misaligned_history_is_na(self):
        start, end = (T-timedelta(days=1)).timestamp()*1000, T.timestamp()*1000
        a = [[start,1],[end,2]]
        self.assertIsNone(aligned_returns(a,[],T,1)["usd"])
        self.assertIsNone(aligned_returns(a,[[start-120000,1],[end-120000,2]],T,1)["usd"])
        self.assertIsNone(nearest([[end+1000,4]],T))
        self.assertIsNone(nearest([[end-1000000,4]],T))

    def test_orderbook_walk_and_insufficient_depth(self):
        r=orderbook_metrics([[99,5],[98,100]],[[101,5],[102,100]],1000)
        self.assertAlmostEqual(r["spreadPct"],2)
        self.assertAlmostEqual(r["buySlippagePct"],(1000/(5+495/102)/100-1)*100)
        self.assertAlmostEqual(r["sellSlippagePct"],1.5)
        self.assertEqual(r["bidDepth2PctUsd"],10295)
        short=orderbook_metrics([[99,1]],[[101,1]],1000)
        self.assertIsNone(short["buySlippagePct"])
        self.assertIsNone(short["sellSlippagePct"])
        with self.assertRaises(ValueError):orderbook_metrics([[101,2]],[[100,2]],10)

    def test_feedback_dedup_bot_and_old_report(self):
        common={"projectId":"p","problemKey":"same","title":"issue","platform":"GitHub","publishedAt":iso(T-timedelta(hours=1))}
        a=dict(common,url="https://example.com/1",author="alice")
        b=dict(common,url="https://example.com/2",author="alice")
        c=dict(common,url="https://example.com/3",author="bot",isBot=True)
        d=dict(common,url="https://example.com/4",author="bob",publishedAt=iso(T-timedelta(days=3)))
        group=group_feedback([a,a,b,c,d],T)[0]
        self.assertEqual(group["independent24h"],1)
        self.assertEqual(group["independent7d"],2)
        self.assertEqual(len(group["reports"]),4)

    def test_correction_preserves_before_and_after(self):
        old={"id":"e","status":"planned","url":"https://example.com"}
        new=dict(old,status="completed")
        changes=corrections({"events":[old]},[new],T)
        self.assertEqual(changes[0]["before"],{"status":"planned"})
        self.assertEqual(changes[0]["after"],{"status":"completed"})

    def test_alerts_require_evidence_not_price_explanation(self):
        settings={"staleMinutes":30,"priceChangePct":20,"volumeMultiple":3,"feedbackSamples":5,"unlockPct":5,"depthDropPct":50,"depegPct":2}
        m={"projectId":"p","symbol":"A","quotedAt":iso(T),"url":"https://example.com","returns":{"24h":{"usd":25}},"volume24hUsd":400,"previous7CompleteDailyVolumes":[100]*7}
        data={"window":windows(T),"sources":[],"markets":[m],"events":[],"feedbackGroups":[]}
        self.assertEqual(len(build_alerts(data,settings)),2)
        m["quotedAt"]=iso(T-timedelta(hours=1))
        alerts=build_alerts(data,settings)
        self.assertEqual([a["level"] for a in alerts],["P2"])
        m["quotedAt"]=iso(T)
        m["returns"]["24h"]["usd"]=None
        m["previous7CompleteDailyVolumes"]=[]
        self.assertEqual(build_alerts(data,settings),[])

    def test_depeg_requires_two_distinct_recent_samples(self):
        settings={"staleMinutes":30,"priceChangePct":20,"volumeMultiple":3,"feedbackSamples":5,"unlockPct":5,"depthDropPct":50,"depegPct":2}
        m={"projectId":"p","symbol":"A","quotedAt":iso(T),"url":"https://example.com","pegUsd":1,"pegSamples":[{"time":iso(T),"usd":.95}]*2}
        data={"window":windows(T),"sources":[],"markets":[m],"events":[],"feedbackGroups":[]}
        self.assertEqual(build_alerts(data,settings),[])
        m["pegSamples"][0]={"time":iso(T-timedelta(minutes=10)),"usd":.96}
        self.assertEqual(len(build_alerts(data,settings)),1)


if __name__ == "__main__":unittest.main()
