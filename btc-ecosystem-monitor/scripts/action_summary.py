"""Render a bounded report directly in GitHub Actions Summary."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 800_000  # GitHub job summaries have a 1 MiB per-step limit.


def summary(data, markdown, outcome="success"):
    mode = data.get("mode", "unknown")
    coverage = data.get("coverage", {})
    header = ["# ₿ BTC Observatory · Actions 运行结果", ""]
    if outcome != "success" or mode != "collected":
        header += ["> ⚠️ 本次在线采集未成功完成。下面可能是仓库已有快照；请核对报告截止时间，不能当成最新数据。", ""]
    elif coverage.get("failedSources", 0):
        header += ["> ⚠️ 已生成部分覆盖简报，存在来源访问失败；失败不代表没有事件。", ""]
    header += [f"- 报告截止：`{data.get('window', {}).get('cutoff', 'N/A')}`",
               f"- 至少一个来源成功的项目：**{coverage.get('checkedProjects', 0)} / {coverage.get('totalProjects', 0)}**",
               f"- 成功来源：**{coverage.get('successfulSources', 0)}**；失败来源：**{coverage.get('failedSources', 0)}**",
               "- 完整 Markdown、JSON 和网页产物：在本次运行页面的 **Artifacts** 下载 `btc-evidence` 与 `btc-dashboard`。",
               "- 若启用 Pages，本次运行的部署结果显示网站链接。Summary 本身不运行交互式 JavaScript。", "", "---", ""]
    result = "\n".join(header) + markdown
    encoded = result.encode("utf-8")
    if len(encoded) > MAX_BYTES:
        result = encoded[:MAX_BYTES].decode("utf-8", errors="ignore").rsplit("\n", 1)[0]
        result += "\n\n---\n报告较长，Summary 已截断。请下载 btc-evidence 中的完整 daily.md。\n"
    return result


def main():
    data = json.loads((ROOT / "web/data/snapshot.json").read_text())
    markdown = (ROOT / "web/data/daily.md").read_text()
    text = summary(data, markdown, os.getenv("COLLECT_OUTCOME", "success"))
    target = os.getenv("GITHUB_STEP_SUMMARY")
    if target:
        with open(target, "a", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
