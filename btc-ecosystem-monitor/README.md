# BTC Observatory · 比特币生态观察站

中文监控看板 + Python 数据采集器 + 可追溯 Markdown 每日简报。项目放在 `keithprayer/codex/btc-ecosystem-monitor`，不依赖数据库或付费 AI 服务。**本项目尚未发布；发布由仓库所有者手动执行。**

## 本地运行

需要 Node.js 20+、Python 3.11+；无第三方运行依赖，无需 `npm install`。

```bash
cd btc-ecosystem-monitor
npm run dev
# 浏览器打开 http://localhost:4173
```

初始快照明确标为“等待首次采集”，不使用聊天中的历史简报伪装实时数据。

```bash
npm test                  # 计算、采集边界、报告与前端安全测试
npm run check             # 语法检查
npm run collect           # 在线采集，会访问公开外部 API
npm run build             # 产出 dist/，可部署到任意静态托管
```

可选环境变量：`GITHUB_TOKEN` 用于提高 GitHub API 限额；`COINGECKO_API_KEY` 是 CoinGecko Demo API key。Python 使用进程环境，不自动读取 `.env`。**不要把密钥放入 config.json、curated.json 或 web/。**

## GitHub Actions 运行、展示和部署

1. 合并本项目 PR 到 `main`。
2. Settings → Pages → Build and deployment → Source 选 **GitHub Actions**。
3. 可选：在 Settings → Secrets and variables → Actions 添加 `COINGECKO_API_KEY`（Demo API key）。GitHub token 由 Actions 自动提供。
4. Actions → **BTC Monitor** → **Run workflow**。默认勾选 `publish`：自动测试 → 采集 → 生成 Summary → 构建 → 保存快照 → 部署 GitHub Pages。
5. 本次运行的 **Summary** 直接显示中文每日简报、核查数量、来源失败、报价与风险；**deploy** 作业显示交互看板链接。
6. 完整数据和网页分别在 **Artifacts** 中下载 `btc-evidence`、`btc-dashboard`。取消 `publish` 可只运行和展示简报，不部署网站。

不需要本地运行或单独服务器。网页“重新读取快照”只读取最近一次已部署数据；下一次工作流完成部署后，看板会显示新的报告。

**定时运行：**在仓库 Actions Variables 设置 `BTC_MONITOR_ENABLED=true`，每天 **00:17 UTC** 自动采集并在 Summary 展示；再设置 `BTC_PAGES_ENABLED=true`，定时任务也会同步部署看板。GitHub 调度可能延迟。默认不开启定时任务，首次发布由你手动触发。

仓库当前是 private。GitHub Pages 的私有仓库支持取决于 GitHub 套餐；Pages 网站受众也不一定与仓库可见性一致。若套餐不支持 Pages，取消 `publish`，仍可在私有仓库 Actions Summary 查看全部报告并下载网页产物。也可把 `dist/` 部署到其他静态托管服务。

若分支保护禁止 Actions 直接提交，快照保存步骤会失败，但前面的 Summary 和 Artifacts 仍可查看；为监控数据选择允许写入的运行分支，或按仓库策略调整数据提交方式。

## 能力和边界

| 能力 | 实现 |
|---|---|
| 生态与身份 | 9 个初始项目组；多标签项目合并，资产按网络和唯一标识分别管理。CRC20 全名、网络、资产 ID 未核实时不能启用行情 |
| 公告 | GitHub Releases、可配置 RSS/Atom；合并相同链接或显式 dedupeKey；公布、生效、状态分开 |
| 用户反馈 | GitHub Issues（排除 PR）；同问题按 platform + author 去重，机器人排除。新报告与旧问题更新分开计时 |
| 行情 | CoinGecko 聚合现货、8 日历史；USD、对齐 BTC 后的 sats、24h/7d 和相对 BTC 收益 |
| 流动性 | 可选 Kraken **USD** 原始盘口适配器；价差、两侧 ±2% 深度、买卖逐档滑点，余额不足时 N/A |
| 人工证据 | curated.json 支持公告、反馈、生态指标、升级与解锁日期；网页可导出公告和反馈草稿 |
| 历史与更正 | 每次在线采集归档，保留最近 90 期；同事件 ID 的重要字段变化保留 before / after |
| 展示 | 项目搜索、生态过滤、本地关注、详情、行情图、预警、未来日历、Markdown/JSON 导出 |

**不做“全网已覆盖”的承诺。** 默认没有 X、Telegram、Discord 登录采集，没有自动语义归因或修复验证。融资、合作、上币、安全事件只有在配置公告源或人工录入后才会进入简报；网页 UI 不会直接写 GitHub。GitHub Issue 评论的团队回应和复现情况需人工补充。RPC、RGB 私有状态、私有 Lightning 通道等专属指标没有自动连接；在页面明确 N/A，通过带范围与观察时间的人工指标补充。

默认只有 STX 启用行情。LIGHT、ORDI、DOG 保留参考身份，须自行复核网络、资产 ID 和聚合行情映射后，把对应 `identityStatus` 改成 `verified`、`marketEnabled` 改成 `true`。CRC Garden 的 LEAF、AXBT 仍是待核验候选；不假设 AXBT 是美元稳定币。

## 数据质量与预警

- 报告窗口是 `(start, cutoff]`；未来窗口是 `(cutoff, cutoff+7d]`。无时区的日期不能冒充 UTC 时间。
- 报价保留提供方 `last_updated`，读取时间另存；晚于报告截止的报价不使用。
- 收益端点最多落后目标 15 分钟，BTC 与资产端点差最多 60 秒。实际端点保存在 `returns.*.endpoints`；不满足条件则 N/A。
- 相对 BTC 收益为 `(1 + asset_return) / (1 + btc_return) - 1`，不是直接相减。
- 成交额是提供方报价时刻滚动 24h，不强称为本报告统一截止窗口。聚合报价不代表 Bitcoin 原生链上成交额。
- ±2% 深度受盘口返回档数限制；`depthComplete=false` 时仅是下界，不触发深度下降规则。滑点不含手续费，不承诺成交。
- P0 必须是人工 `confirmed` 事件。P1 支持绝对 24h 收益 >20%、同问题 24h ≥5 独立账号或严重独立复现、解锁 >流通量 5%、同场所 24h 深度下降 >50%、显式锚定资产连续两次偏离 >2%。
- 放量 >3× 的计算器已实现，但默认采集器没有“前 7 个完整日”成交额适配器，因此**不评估该规则**；不会拿 CoinGecko 滚动成交额历史冒充完整日成交量。
- 深度与脱锚规则需要足够历史采集。每日一次不足以证明 30 分钟内连续脱锚，请按需要手动运行或调整 cron。未满足历史条件的规则不触发，不等于没有风险。
- P2 列出来源失败、部分覆盖、未配置、缺失/过期报价；连续失败次数另存。只有完整成功核查的特定来源才能写“未发现新增”。

详细数据格式见 [docs/DATA.md](docs/DATA.md)，维护流程见 [docs/OPERATIONS.md](docs/OPERATIONS.md)。
