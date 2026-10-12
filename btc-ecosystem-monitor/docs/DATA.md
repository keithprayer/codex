# 配置与证据格式

## config.json

每个项目包含 `id/name/ecosystems/network/protocol/officialUrl/identityStatus/repos/feeds/assets/metrics/visibility`。GitHub repo 为 `owner/repo`；RSS 必须是可公开读取的 HTTPS XML feed，重定向会拒绝，需填写最终地址。不能将私有 URL 或凭据放进配置；配置会被复制到网页。

资产示例（仅格式，提交前自行核实实际资产）：

```json
{
  "id": "unique-network-asset",
  "symbol": "SYMBOL",
  "network": "已核实网络",
  "standard": "协议标准",
  "uniqueId": "已核实的原生标识、合约或发行 ID",
  "identityStatus": "verified",
  "identitySource": "https://example.com/official-asset",
  "coinGeckoId": "verified-provider-id",
  "marketEnabled": true
}
```

`krakenPair` 可选，限确认为同一资产的 USD 交易对（如已核实的 `STXUSD`）。添加此字段才会请求盘口。`pegUsd` 与 `pegSource` 同时存在才评估锚定规则；未确认锚定关系不要填写。报价映射核实是维护者的责任。

## curated.json

所有条目需要唯一 `id`、已有 `projectId` 和 HTTPS 原始 `url`。日期要求 ISO 8601 时区：`2026-10-12T06:00:00Z`。未知时分设 `null`，原始日历日期写在 summary；不能猜测午夜 UTC。

```json
{
  "schemaVersion": 1,
  "events": [{
    "id": "manual-upgrade-001",
    "projectId": "rgb",
    "title": "示例格式，使用前替换为原始证据",
    "summary": "计划与实际执行分开；标注原始日期及核验范围。",
    "url": "https://example.com/announcement",
    "type": "upgrade",
    "evidence": "statement",
    "status": "planned",
    "publishedAt": null,
    "effectiveAt": null,
    "dedupeKey": "same-underlying-announcement"
  }],
  "feedback": [{
    "id": "manual-feedback-001",
    "projectId": "rgb",
    "problemKey": "wallet-recovery-same-root-issue",
    "title": "反馈主题",
    "summary": "原始报告摘要",
    "platform": "GitHub",
    "author": "original-author",
    "isBot": false,
    "url": "https://example.com/original-feedback",
    "publishedAt": null,
    "updatedAt": null,
    "status": "open",
    "reproduction": "not_verified",
    "teamResponse": "尚未取得团队回应"
  }],
  "metrics": [{
    "id": "manual-metric-001",
    "projectId": "rgb",
    "name": "公开索引器记录数",
    "value": null,
    "unit": "条",
    "scope": "仅指定索引器，不代表全网",
    "observedAt": "2026-10-12T06:00:00Z",
    "url": "https://example.com/indexer"
  }]
}
```

上面是字段示例，仓库默认 curated.json 为空，示例不进入实际简报。

证据类型：`confirmed`、`statement`、`user_report`、`inference`。状态：`planned`、`published`、`completed`、`open`、`resolved`、`unknown`。

人工核实严重事件可设置 `riskLevel: "P0"` 且 `evidence: "confirmed"`。解锁可设置 `unlockPctCirculating`，应有分母来源及时间；配合未来 `effectiveAt` 判断阈值。严重反馈必须同时设置 `severity: "severe"` 和 `reproduction: "independently_reproduced"` 才走独立复现预警。

合并反馈以相同 `projectId + problemKey` 为准；相同原始 URL 不重复。自动 GitHub Issue 默认以仓库和 Issue 编号作为 problemKey，不进行未经核实的跨帖语义合并。跨平台账号视为独立账号，不代表已核实的独立自然人。

修正自动记录时，人工条目使用同一原始 URL 和事件 ID（`gh-release-数字` / `gh-issue-数字`），人工记录优先。保留事件 ID 可比较更正记录。新的 URL 若属同一公告，设置一致的 dedupeKey 并保留原始链接。

## 输出文件

- `web/data/snapshot.json`：窗口、项目、公告、合并反馈、行情、来源、预警、指标、更正。
- `web/data/daily.md`：确定性模板简报，不调用生成式模型推断因果。
- `web/data/config.json`：面向网页的配置副本。
- `web/data/archive/`：最近 90 次在线采集快照与 Markdown。
- `web/data/archive-index.json`：历史下载列表。

来源状态 `ok` 仅表示该适配器定义范围成功完成；`partial/error/not_checked/not_configured` 均不能推出没有事件。GitHub Issues 是“过去 7 日更新的公开 Issue”，不是全平台投诉；RSS 无法覆盖完整 7 日时标 partial。

历史档案保留当时状态。采集失败不会把上一期快照伪装为当前数据。更正列表保留最近 200 条。
