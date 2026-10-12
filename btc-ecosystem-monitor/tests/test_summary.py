import unittest
from scripts.action_summary import summary


class SummaryTests(unittest.TestCase):
    def test_failed_run_does_not_relabel_old_snapshot(self):
        data={'mode':'collected','window':{'cutoff':'2026-10-12T06:00:00Z'},'coverage':{'checkedProjects':2,'totalProjects':9,'failedSources':1}}
        text=summary(data,'# 原始报告','failure')
        self.assertIn('不能当成最新数据',text)
        self.assertIn('2026-10-12T06:00:00Z',text)

    def test_partial_coverage_displayed(self):
        text=summary({'mode':'collected','coverage':{'failedSources':2}},'body')
        self.assertIn('部分覆盖简报',text)
        self.assertIn('btc-dashboard',text)

    def test_summary_respects_github_byte_limit(self):
        text=summary({'mode':'collected'},'一条证据\n'*300000)
        self.assertLess(len(text.encode('utf-8')),1024*1024)
        self.assertIn('Summary 已截断',text)
