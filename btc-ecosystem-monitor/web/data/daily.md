# BTC 生态每日简报 · 2026-10-12

UTC 截止：2026-10-12T16:02:56Z
24h 窗口：(2026-10-11T16:02:56Z, 2026-10-12T16:02:56Z]
7d 窗口：(2026-10-05T16:02:56Z, 2026-10-12T16:02:56Z]
未来 7 日：(2026-10-12T16:02:56Z, 2026-10-19T16:02:56Z]

范围：9 个项目组；至少一个来源成功核查 6 个。
自动来源覆盖不等于完整项目核查；社交平台、私有网络和人工审阅仍可能缺失。

## 公告与单项目更新

### RGB Protocol
协议：RGB client-side validation；网络：Bitcoin；身份：protocol_only。
可见范围：客户端验证的私有状态不可全网枚举；公开索引不等于全网。
- 【项目方声明 / published】How Privacy Is Preserved in RGB Protocol on Bitcoin；公布 2026-10-07T07:00:00Z；生效 N/A；[原文](https://rgb.info/privacy-in-rgb-protocol-on-bitcoin/)。请打开官方原文核查具体声明、计划与生效时间。
- 【项目方声明 / published】Stablecoins, Privacy, and Lightning on RGB Protocol；公布 2026-10-06T15:01:55Z；生效 N/A；[原文](https://rgb.info/stablecoin-privacy-bitcoin-rgb-origin-seoul/)。请打开官方原文核查具体声明、计划与生效时间。

### Bitlight Labs
协议：RGB / Lightning；网络：Bitcoin products / BNB Smart Chain token；身份：review_required。
可见范围：项目的 BTC 生态标签与代币发行网络分别记录；启用行情前重新确认合约。
- 公告来源覆盖不足，无法判断有无新增。

### Lightning Labs
协议：Taproot Assets / Lightning Network；网络：Bitcoin；身份：protocol_only。
可见范围：私有通道、支付成功率和私有 Universe 不属于公开全网数据。
- 已成功核查的下列公告来源未发现窗口内新增（不覆盖其他来源）：[lightninglabs/taproot-assets releases](https://github.com/lightninglabs/taproot-assets/releases) @ 2026-10-12T16:02:57Z

### UniSat · ORDI 观察组
协议：BRC-20；网络：Bitcoin mainnet；身份：review_required。
可见范围：ORDI 是独立观察资产，不是 UniSat 项目代币；聚合报价可能包含跨链表示。
- 已成功核查的下列公告来源未发现窗口内新增（不覆盖其他来源）：[unisat-wallet/extension releases](https://github.com/unisat-wallet/extension/releases) @ 2026-10-12T16:03:04Z

### CRC Garden
协议：CRC-20（协议全名待核实）；网络：Bitcoin L1（项目方声明，待核实）；身份：unverified。
可见范围：CRC20 名称有歧义。全名、网络、唯一资产标识全部通过后才能启用报价；不假设 AXBT 锚定美元。
- 公告来源覆盖不足，无法判断有无新增。

### DOG · Runes
协议：Runes；网络：Bitcoin mainnet；身份：review_required。
可见范围：当前入口是区块浏览器，不视为发行方官方公告源。
- 公告来源覆盖不足，无法判断有无新增。

### Atomicals
协议：Atomicals / ARC-20；网络：Bitcoin mainnet；身份：protocol_only。
可见范围：尚未选择具体 ARC-20 资产，避免误用 Cosmos ATOM 行情。
- 已成功核查的下列公告来源未发现窗口内新增（不覆盖其他来源）：[atomicals/atomicals-electrumx releases](https://github.com/atomicals/atomicals-electrumx/releases) @ 2026-10-12T16:03:05Z

### CAT Protocol
协议：Covenant Attested Token / CAT20；网络：Fractal Bitcoin；身份：protocol_only。
可见范围：部署网络与具体 token ID 分别核验，不把 Fractal 自动归为 Bitcoin 主网。
- 已成功核查的下列公告来源未发现窗口内新增（不覆盖其他来源）：[CATProtocol/cat-token-box releases](https://github.com/CATProtocol/cat-token-box/releases) @ 2026-10-12T16:03:06Z

### Stacks
协议：Stacks / Proof of Transfer；网络：Stacks mainnet；身份：verified。
可见范围：官方文章的计划与链上实际执行分开记录；sBTC / stBTC 须另外添加资产。
- 公告来源覆盖不足，无法判断有无新增。

## 原始反馈（按问题合并）

样本按平台账号去重；跨平台身份未经确认，不能代表全部用户。

- **Lightning Labs / [bug]: memory spike on litd + tapd start up**：24h 1，7d 1 个独立账号。
  - [bufo24 / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2347)：公布 2026-10-12T12:14:56Z；更新 2026-10-12T14:55:33Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [bug]: Supply commitment spends the transfer outpoint after a transfer proof retargets the genesis anchor**：24h 1，7d 1 个独立账号。
  - [SadiqJaf / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2344)：公布 2026-10-12T08:03:01Z；更新 2026-10-12T08:03:01Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [bug]: AddAssetBuyOrder/AddAssetSellOrder return another concurrent order's accepted quote**：24h 0，7d 0 个独立账号。
  - [hieblmi / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2302)：公布 2026-09-11T13:28:50Z；更新 2026-10-09T12:47:58Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / rpcserver: VerifyProofResponse.DecodedProof omits predecessor IDs that DecodeProof can expose**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2214)：公布 2026-07-13T15:34:12Z；更新 2026-10-09T09:41:56Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / taprpc: granular macaroon permissions for advanced custom-anchor commit, log-only publish, and proof import**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2213)：公布 2026-07-13T15:34:09Z；更新 2026-10-09T09:41:53Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / rpc: expose custom-anchor capabilities and a machine-readable API version via GetInfo**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2212)：公布 2026-07-13T15:34:07Z；更新 2026-10-09T09:41:49Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / proof+tapfreighter: support unconfirmed multi-hop proof paths end to end**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2211)：公布 2026-07-13T15:34:05Z；更新 2026-10-09T09:41:45Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / rpc: support multi-packet wallet funding for grouped multi-issuance transfers**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2210)：公布 2026-07-13T15:34:03Z；更新 2026-10-09T09:41:42Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / rpcserver: preserve no-new-change funding semantics through CommitVirtualPsbts to lnd**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2209)：公布 2026-07-13T15:34:01Z；更新 2026-10-09T09:41:39Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / rpc: make PublishAndLogTransfer idempotent (request ID + transfer-status reconciliation)**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2208)：公布 2026-07-13T15:33:59Z；更新 2026-10-09T09:41:36Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / assetwalletrpc: make CommitVirtualPsbts idempotent (request ID + status/lease lookup)**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2207)：公布 2026-07-13T15:33:57Z；更新 2026-10-09T09:41:34Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / rpcserver: use an independent bounded context for post-funding lease cleanup in CommitVirtualPsbts**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2206)：公布 2026-07-13T15:33:55Z；更新 2026-10-09T09:41:25Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [feature]: Itest tranches should use same network**：24h 0，7d 0 个独立账号。
  - [GeorgeTsagk / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2162)：公布 2026-06-16T15:47:45Z；更新 2026-10-09T09:41:10Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [bug]: transfer proof stuck PENDING, listAssets zero**：24h 0，7d 0 个独立账号。
  - [beeforbacon / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2000)：公布 2026-02-18T21:22:37Z；更新 2026-10-09T09:40:58Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / ListAssets with group_key filter returns empty while ListBalances reports a non-zero group balance**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2076)：公布 2026-04-20T10:48:40Z；更新 2026-10-09T09:40:49Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / ListBatches REST path filter silently returns empty on wrong batch_key encoding**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2080)：公布 2026-04-20T10:48:42Z；更新 2026-10-09T09:40:45Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / ListGroups: commit to one canonical group-key encoding in responses**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2079)：公布 2026-04-20T10:48:41Z；更新 2026-10-09T09:40:30Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / events: cover asset visibility, group discovery, universe sync, federation, chain sync, and mint replay**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2081)：公布 2026-04-20T11:11:47Z；更新 2026-10-09T09:40:15Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / Optimise universe proof leaf additional inputs**：24h 0，7d 0 个独立账号。
  - [ffranr / GitHub](https://github.com/lightninglabs/taproot-assets/issues/503)：公布 2023-09-13T18:24:52Z；更新 2026-10-09T09:39:54Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / proofs+tarodb: stop storing proofs files in the DB switch to mmap access to on disk files everywhere**：24h 0，7d 0 个独立账号。
  - [Roasbeef / GitHub](https://github.com/lightninglabs/taproot-assets/issues/147)：公布 2022-09-27T23:42:07Z；更新 2026-10-09T09:38:54Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / proofs: introduce proof compression or tomb-stoning scheme **：24h 0，7d 0 个独立账号。
  - [Roasbeef / GitHub](https://github.com/lightninglabs/taproot-assets/issues/10)：公布 2022-04-13T01:48:09Z；更新 2026-10-09T09:38:43Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / tapdb: add table to track anchored altLeaves**：24h 0，7d 0 个独立账号。
  - [jharveyb / GitHub](https://github.com/lightninglabs/taproot-assets/issues/1241)：公布 2024-12-05T10:07:49Z；更新 2026-10-09T09:38:10Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / tapdb: deleting an absent key from a DB-backed MS-SMT corrupts later inserts**：24h 0，7d 0 个独立账号。
  - [darioAnongba / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2322)：公布 2026-09-29T15:53:33Z；更新 2026-10-09T07:01:48Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / tapchannel: aux sweeper assumes fixed layout**：24h 0，7d 0 个独立账号。
  - [jtobin / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2205)：公布 2026-07-13T14:38:21Z；更新 2026-10-09T03:11:15Z；复现 not_verified；状态 closed；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [feature]: Authenticated mutable application state for Collectible assets**：24h 0，7d 0 个独立账号。
  - [vctt94 / GitHub](https://github.com/lightninglabs/taproot-assets/issues/2326)：公布 2026-10-04T16:45:19Z；更新 2026-10-05T22:37:52Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [bug]: Briefly Unavailable Feerate Source defaults to 25 sats/vB leading to FCs**：24h 1，7d 1 个独立账号。
  - [TheBlueMatt / GitHub](https://github.com/lightningnetwork/lnd/issues/11316)：公布 2026-10-11T22:14:00Z；更新 2026-10-11T22:34:40Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [epic]: BOLT 12 Implementation Roadmap**：24h 0，7d 0 个独立账号。
  - [bitromortac / GitHub](https://github.com/lightningnetwork/lnd/issues/10736)：公布 2026-04-16T13:31:59Z；更新 2026-10-09T16:30:13Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / feature: convey required-output taproot metadata to the aux sweeper**：24h 0，7d 1 个独立账号。
  - [jtobin / GitHub](https://github.com/lightningnetwork/lnd/issues/11305)：公布 2026-10-09T10:14:22Z；更新 2026-10-09T10:14:22Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / itest flake: commit sweep resolver can remain unresolved after fee-bump/confirmation race**：24h 0，7d 0 个独立账号。
  - [ziggie1984 / GitHub](https://github.com/lightningnetwork/lnd/issues/10938)：公布 2026-06-27T17:09:12Z；更新 2026-10-09T07:10:47Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / lnd should exit with no-success error code when automatically shut down due to bitcoind problems**：24h 0，7d 0 个独立账号。
  - [Talkless / GitHub](https://github.com/lightningnetwork/lnd/issues/5625)：公布 2021-08-12T10:16:54Z；更新 2026-10-09T01:26:56Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / postgres nodes with "many" on chain transactions are very slow**：24h 0，7d 0 个独立账号。
  - [ZZiigguurraatt / GitHub](https://github.com/lightningnetwork/lnd/issues/11289)：公布 2026-10-01T17:32:12Z；更新 2026-10-08T14:49:51Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [bug]: fixed-width node announcement address decoders accept short reads**：24h 0，7d 0 个独立账号。
  - [s1ns3nz0 / GitHub](https://github.com/lightningnetwork/lnd/issues/11211)：公布 2026-09-20T14:50:09Z；更新 2026-10-07T13:31:32Z；复现 not_verified；状态 closed；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / Channel-open race with latent nil dereference**：24h 0，7d 0 个独立账号。
  - [morehouse / GitHub](https://github.com/lightningnetwork/lnd/issues/11259)：公布 2026-09-24T16:22:13Z；更新 2026-10-07T01:51:59Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [bug]: link fails on adds that do NOT exceed the max fee exposure limit**：24h 0，7d 1 个独立账号。
  - [MPins / GitHub](https://github.com/lightningnetwork/lnd/issues/11296)：公布 2026-10-06T14:02:41Z；更新 2026-10-06T14:04:35Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [bug]: Force-close recovery can remain in waiting_close after restart despite sufficient confirmations**：24h 0，7d 0 个独立账号。
  - [ripsline / GitHub](https://github.com/lightningnetwork/lnd/issues/11182)：公布 2026-09-08T19:59:26Z；更新 2026-10-05T22:06:36Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Lightning Labs / [bug]: Known TLV records in lnwire decode with the wrong length and shift the stream**：24h 0，7d 1 个独立账号。
  - [Nuhiat-Arefin / GitHub](https://github.com/lightningnetwork/lnd/issues/11295)：公布 2026-10-05T18:51:30Z；更新 2026-10-05T18:52:55Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Stacks / [Flaky Test] tests::nakamoto_integrations::follower_bootup_across_multiple_cycles**：24h 0，7d 0 个独立账号。
  - [github-actions[bot] / GitHub](https://github.com/stacks-network/stacks-core/issues/7721)：公布 2026-10-11T06:41:02Z；更新 2026-10-11T06:41:03Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Stacks / at-block reads the base tip during block replay and tx simulate**：24h 0，7d 1 个独立账号。
  - [ryanwaits / GitHub](https://github.com/stacks-network/stacks-core/issues/7713)：公布 2026-10-09T02:45:04Z；更新 2026-10-09T02:52:50Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Stacks / cleanup: remove deprecated `helium` logic**：24h 0，7d 0 个独立账号。
  - [fdefelici / GitHub](https://github.com/stacks-network/stacks-core/issues/6408)：公布 2025-08-21T06:45:54Z；更新 2026-10-08T09:53:27Z；复现 not_verified；状态 closed；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Stacks / [chore] remove mocknet from stacks-core**：24h 0，7d 0 个独立账号。
  - [wileyj / GitHub](https://github.com/stacks-network/stacks-core/issues/6553)：公布 2025-10-01T14:50:23Z；更新 2026-10-07T11:09:40Z；复现 not_verified；状态 closed；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Stacks / cleanup: remove `BurnchainConfig::rpc_ssl` configuration**：24h 0，7d 0 个独立账号。
  - [fdefelici / GitHub](https://github.com/stacks-network/stacks-core/issues/6362)：公布 2025-08-11T13:14:01Z；更新 2026-10-07T06:44:42Z；复现 not_verified；状态 closed；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Stacks / [Flaky Test] tests::nakamoto_integrations::test_tenure_extend_from_flashblocks**：24h 0，7d 0 个独立账号。
  - [github-actions[bot] / GitHub](https://github.com/stacks-network/stacks-core/issues/7686)：公布 2026-09-30T06:42:51Z；更新 2026-10-06T12:28:04Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。
- **Stacks / [Flaky Test] tests::signer::v0::tenure_extend::new_tenure_no_winner_while_proposing_block_then_ignored**：24h 0，7d 0 个独立账号。
  - [github-actions[bot] / GitHub](https://github.com/stacks-network/stacks-core/issues/7705)：公布 2026-10-05T06:54:26Z；更新 2026-10-06T06:42:53Z；复现 not_verified；状态 open；团队回应 未自动核查评论；Issue 关闭不等于独立验证修复。

## 行情

| 资产 / 网络 | USD | sats | 24h | 7d | 相对 BTC 24h / 7d | 24h 成交额 USD | 报价时间 / 来源 |
|---|---:|---:|---:|---:|---:|---:|---|
| RGB Protocol（协议/产品） | 不适用 | 不适用 | 不适用 | 不适用 | 不适用 | 不适用 | 未选择代币 |
| LIGHT / BNB Smart Chain | N/A | N/A | N/A | N/A | N/A / N/A | N/A | 身份待核验或尚未采集 |
| Lightning Labs（协议/产品） | 不适用 | 不适用 | 不适用 | 不适用 | 不适用 | 不适用 | 未选择代币 |
| ORDI / Bitcoin mainnet | N/A | N/A | N/A | N/A | N/A / N/A | N/A | 身份待核验或尚未采集 |
| LEAF / 待核实 | N/A | N/A | N/A | N/A | N/A / N/A | N/A | 身份待核验或尚未采集 |
| AXBT / 待核实 | N/A | N/A | N/A | N/A | N/A / N/A | N/A | 身份待核验或尚未采集 |
| DOG / Bitcoin mainnet | N/A | N/A | N/A | N/A | N/A / N/A | N/A | 身份待核验或尚未采集 |
| Atomicals（协议/产品） | 不适用 | 不适用 | 不适用 | 不适用 | 不适用 | 不适用 | 未选择代币 |
| CAT Protocol（协议/产品） | 不适用 | 不适用 | 不适用 | 不适用 | 不适用 | 不适用 | 未选择代币 |
| STX / Stacks mainnet | N/A | N/A | 1.5533% | 6.6561% | 2.8645% / 9.9313% | N/A | 2026-10-12T16:02:57.000Z [来源](https://www.coingecko.com/en/coins/blockstack) |

收益只在历史端点符合时间容差且与 BTC 对齐时计算；实际端点、原始币种见 snapshot.json。成交额为报价时刻的提供方滚动窗口。

| 资产 | 场所 / 币种 | 价差 | 买盘 −2% / 卖盘 +2% USD | 指定金额买 / 卖滑点 | 时刻 |
|---|---|---:|---:|---:|---|
| STX | N/A / N/A | N/A | N/A / N/A | N/A / N/A | N/A |

STX 数据缺口：报价缺失或晚于报告截止


滑点名义金额 1000 USD，不含手续费。未配置原始盘口或盘口不足时为 N/A。

## 预警与待核查

- P2 / 待核查：Bitlight Labs — 来源覆盖不完整；未配置可自动采集源；需人工核查公告与反馈；N/A；[来源](https://bitlightlabs.com/)
- P2 / 待核查：CRC Garden — 来源覆盖不完整；未配置可自动采集源；需人工核查公告与反馈；N/A；[来源](https://crc.garden/)
- P2 / 待核查：DOG · Runes — 来源覆盖不完整；未配置可自动采集源；需人工核查公告与反馈；N/A；[来源](https://ordiscan.com/rune/DOGGOTOTHEMOON)
- P2 / 待核查：Lightning Labs — 来源覆盖不完整；Response exceeds 5 MB；2026-10-12T16:02:59Z；[来源](https://github.com/lightningnetwork/lnd/releases)
- P2 / 待核查：Stacks — STX 报价时间缺失或过期；不能确认当前价格及阈值；2026-10-12T16:02:57.000Z；[来源](https://www.coingecko.com/en/coins/blockstack)
- P2 / 待核查：Stacks — 来源覆盖不完整；分页/订阅源长度不足以证明完整窗口覆盖；2026-10-12T16:03:07Z；[来源](https://github.com/stacks-network/stacks-core/releases)
- P2 / 待核查：Stacks — 来源覆盖不完整；报价缺失或晚于报告截止；2026-10-12T16:03:09Z；[来源](https://www.coingecko.com/en/coins/blockstack)

## 未来 7 日

未取得经过标时的未来事件。此处不代表未来没有解锁、升级或活动。

## 来源覆盖与过期数据

| 来源 | 类型 | 状态 | 核查 UTC | 缺口 |
|---|---|---|---|---|
| [RGB Protocol RSS](https://rgb.info/feed/) | feed | ok | 2026-10-12T16:02:56Z | N/A |
| [Bitlight Labs 官方网站](https://bitlightlabs.com/) | manual | not_configured | N/A | 未配置可自动采集源；需人工核查公告与反馈 |
| [lightninglabs/taproot-assets releases](https://github.com/lightninglabs/taproot-assets/releases) | releases | ok | 2026-10-12T16:02:57Z | N/A |
| [lightninglabs/taproot-assets issues](https://github.com/lightninglabs/taproot-assets/issues) | feedback | ok | 2026-10-12T16:02:58Z | N/A |
| [lightningnetwork/lnd releases](https://github.com/lightningnetwork/lnd/releases) | releases | error | 2026-10-12T16:02:59Z | Response exceeds 5 MB |
| [lightningnetwork/lnd issues](https://github.com/lightningnetwork/lnd/issues) | feedback | ok | 2026-10-12T16:03:02Z | N/A |
| [unisat-wallet/extension releases](https://github.com/unisat-wallet/extension/releases) | releases | ok | 2026-10-12T16:03:04Z | N/A |
| [unisat-wallet/extension issues](https://github.com/unisat-wallet/extension/issues) | feedback | ok | 2026-10-12T16:03:05Z | N/A |
| [CRC Garden 官方网站](https://crc.garden/) | manual | not_configured | N/A | 未配置可自动采集源；需人工核查公告与反馈 |
| [DOG · Runes 官方网站](https://ordiscan.com/rune/DOGGOTOTHEMOON) | manual | not_configured | N/A | 未配置可自动采集源；需人工核查公告与反馈 |
| [atomicals/atomicals-electrumx releases](https://github.com/atomicals/atomicals-electrumx/releases) | releases | ok | 2026-10-12T16:03:05Z | N/A |
| [atomicals/atomicals-electrumx issues](https://github.com/atomicals/atomicals-electrumx/issues) | feedback | ok | 2026-10-12T16:03:06Z | N/A |
| [CATProtocol/cat-token-box releases](https://github.com/CATProtocol/cat-token-box/releases) | releases | ok | 2026-10-12T16:03:06Z | N/A |
| [CATProtocol/cat-token-box issues](https://github.com/CATProtocol/cat-token-box/issues) | feedback | ok | 2026-10-12T16:03:07Z | N/A |
| [stacks-network/stacks-core releases](https://github.com/stacks-network/stacks-core/releases) | releases | partial | 2026-10-12T16:03:07Z | 分页/订阅源长度不足以证明完整窗口覆盖 |
| [stacks-network/stacks-core issues](https://github.com/stacks-network/stacks-core/issues) | feedback | ok | 2026-10-12T16:03:08Z | N/A |
| [STX 行情](https://www.coingecko.com/en/coins/blockstack) | market | partial | 2026-10-12T16:03:09Z | 报价缺失或晚于报告截止 |

## 关键变化与更正

无已记录更正；首次采集仅建立基线。
