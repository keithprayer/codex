# 维护与发布

## 日常步骤

1. 编辑 `config.json`，先核实协议全名、网络、唯一资产标识与官方来源。
2. 在 `curated.json` 记录不可自动访问的公告、用户反馈、生态指标及未来日期。可先在网页保存本地草稿，再导出合并。
3. 运行 `npm test` 和 `npm run collect`，检查来源失败、旧报价、分页缺口及样本数量。
4. 检查 `web/data/daily.md`、`snapshot.json`，修改同一事件的原 ID 来保留更正。
5. 运行 GitHub Actions 的 **BTC Monitor**，在 Summary 审阅简报；勾选 publish 后会部署交互看板。

## 网络与失败处理

需要访问 `api.github.com`、`api.coingecko.com`，以及配置的官方 RSS 域名；配置盘口后需要 `api.kraken.com`。受限环境应由环境管理员放行，不能通过改代理绕过策略。测试使用离线响应，不要求外部 API 在线。

429/5xx 最多重试两次；每次请求 20 秒超时、5 MB 上限。GitHub Issue 最多 10 页，达到上限标 partial；公开发布记录最多 100 条，满页保守标 partial。RSS 不接受实体声明。API 凭据只送到指定主机，重定向被拒绝。

HTTP 403/429、响应格式变化或源不可用会写入 source error。采集器仍输出不完整简报，工作流可成功；这是“完成采集尝试”，**不是来源全部成功**。发布前应查看 coverage 和来源表。

首次采集可能因 CoinGecko 限额或历史时间粒度产生 N/A。不要用页面不带时间的数字填补精确窗口。默认不会自动分类 GitHub Issue 是否属于真实产品故障，也不会自动执行其中建议的命令。

## 部署约束

静态应用只读取同源 JSON，没有浏览器端写入服务。关注与草稿使用 localStorage，不能跨设备自动同步。云端权威数据来自 GitHub 仓库和 Actions。

根目录 `.github/workflows/btc-monitor.yml` 统一处理采集、Actions Summary 展示、快照提交与可选 Pages 部署。手动运行的 publish 选项默认开启，取消后只生成报告与产物。定时采集需要 `BTC_MONITOR_ENABLED=true`，定时部署另需 `BTC_PAGES_ENABLED=true`。无 push 部署触发器，并发组避免多个运行同时修改数据。Summary 超过 800 KB 时截断并提示下载完整报告。

Pages 会托管 dist 的内容。若私有仓库的套餐不支持 Pages，可在其他静态托管平台选项目子目录作为根目录，执行 `npm run build` 并发布 dist；先运行采集才有在线数据。

## 验证范围

`npm test` 覆盖窗口边界、相对收益、时间对齐、原始盘口滑点、样本去重、机器人排除、来源失败、身份门槛、日期校验、HTML 转义和更正记录。浏览器冒烟脚本见 `tests/browser_smoke.py`；开发环境另需 Playwright 与 Chromium，仅用于测试，不是部署依赖。
