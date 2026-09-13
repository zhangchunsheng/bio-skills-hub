---
name: gcw
description: 通过分阶段、证据驱动的工作流，分析、重现、恢复并改编授权的公开网站。用于 gcw、网站拆解或克隆、基线搭建、设计 DNA 提取、WebGL/Canvas/着色器逆向、源码丢失恢复、路由重构以及视觉回归对比。
---

# GCW──网站复刻并重建引擎

在写代码前找证据。重构前先跑通。润色前做对比。

## 边界

- 只针对用户拥有所有权、已获许可或有明确授权的目标操作。授权不明确时要问清楚。
- 除非有明确授权，否则不碰私有或需要验证的内容。禁止绕过访问控制或处理任何凭证。
- 分别检查代码、字体、图片、模型和品牌的版权。版权声明需标注为 `SOURCE`、`PARTIAL` 或 `GUESS`。
- 把已部署的构建产物看作是证据，不要当成原始源码。

## 1. 明确展示工作流步骤

阅读 `references/clone-modes.md`。使用工具前展示此预检信息：

```markdown
- Outcome:
- Final deliverable:
- Editability target:
- Current phase:
- Site type:
- Ownership/authorization:
- Source availability:
- Baseline scope:
- Implementation path:
- Approximate or excluded scope:
```

在开始任何构建类的重构前，让用户选定一个最终交付契约，绝不能从用户画像中推断或设为默认：

- A: 仅研究或可运行回放 (`RESEARCH_OR_RUNNABLE_REPLAY`, `RUNNABLE_REPLAY`)
- B: 可编辑的忠实克隆 (`EDITABLE_FAITHFUL_CLONE`, `MAINTAINABLE_SOURCE`)
- C: 可编辑的忠实克隆，评审后做创意重建 (`EDITABLE_FAITHFUL_CLONE_THEN_CREATIVE`, `MAINTAINABLE_SOURCE`)

选择 B 是一个可持续使用的基线，不代表以后不能做创意重建。用户可以在 `REVIEW_GATE` 阶段把 B 升级为 C，或者在 B 交付完成后重新启动创意重建。意图或所有权不明确时多问一句。使用单一流程：`TEARDOWN_PHASE -> FAITHFUL_CLONE -> REVIEW_GATE -> CREATIVE_REBUILD`。仅做拆解的流程在第一阶段后就会停止。B/C 必须满足可编辑性要求，这是 `FAITHFUL_CLONE` 的硬性指标；`CREATIVE_REBUILD` 只做评审通过后的内容、品牌和功能创新。不要擅自扩大范围。

根据证据选择克隆路径：`SOURCE_ADAPT`（源码适配）、`CLEAN_REBUILD`（干净重建）或 `PRODUCTION_RECOVERY`（生产恢复）。只有在用户确认所有权/授权且拿不到可维护源码时，才启用生产恢复。

## 2. 建立规范

阅读工作区的 Agent 指令（如果有 `AGENTS.md` 或 `CLAUDE.md`）。令 `<skill-root>` 代表包含本 `SKILL.md` 的目录，在不覆盖已有证据的前提下进行初始化：

```text
python <skill-root>/scripts/init_reconstruction.py <workspace> --url <canonical-url> --authorization <owned|licensed|authorized>
```

对于构建工作，还需要传入 `--final-deliverable A|B|C` 和相匹配的 `--outcome`。没有该明确契约，初始化脚本会拒绝构建工作。仅拆解的初始化可以不传。

简单的非 GPU 页面可以选择 `--teardown-depth minimal`：它使用四部分的 SITE_SPEC，并将设计 DNA 设为推荐项而非阻塞项。`standard` 是默认的完整 12 部分拆解。对于复杂的渲染或恢复证据，使用 `deep`；GPU 目标无法使用 `minimal`。

阅读 `references/site-spec.md`。创建 `.gcw/SITE_SPEC.md` 作为草稿；在拆解证据和伴随技能（companion-skill）的结果整合完之前，不要将其定稿。将缺失的能力标记为 `N/A`。在第 9 节的子系统表中，用真实度和可信度标签写明每个关键的实现结论，不要用百分比掩盖具体差异。

## 3. 收集真实证据

优先检索官方仓库、源码映射（source maps）、框架元数据和公开部署证据。验证许可证。源码、部署产物和可编辑的实现要分开存放。gcw 会拒绝配置源（origin）之外带有凭据的 URL 以及跨域重定向。

在有 Playwright 的环境下运行清单盘点：

```text
node <skill-root>/scripts/site_inventory.mjs --url <canonical-url> --out <workspace>/.gcw/evidence/site-inventory.json
```

该命令还会写入 `.gcw/evidence/route-map.json`、`.gcw/evidence/network/requests.json` 和 `.gcw/evidence/source-maps.json`。源码映射（Source-map）证据记录响应头或注释指令、常规的 `.map` 探测、脱敏的 URL、受限的响应体大小，以及该响应是否为合法的 Source Map v3 对象。仅凭 HTTP 可达性不代表可访问 Source Map。默认大小限制为 20 MiB；如果授权证据需要更大空间，使用 `--source-map-max-bytes` 覆盖。

在有 Playwright 的环境下生成精简的交互状态草案：

```text
node <skill-root>/scripts/detect_interaction_states.mjs --url <canonical-url> --out <workspace>/.gcw/evidence/interaction-states.json
```

检测器记录 `:hover`、`:focus`/`:focus-visible` 以及常见的 `aria-expanded` 切换状态，并附带前后对比的截图。它的输出默认为 `reviewStatus: pending`：请手动移除误报，加上它无法自动发现的脚本驱动状态，然后把 `reviewStatus` 改为 `confirmed`。定稿脚本会拒绝未通过评审的草稿。

手动验证路由、断点、DOM 根节点、覆盖物（overlays）、滚动容器、输入状态、加载/稳定状态、GPU/媒体/web workers/iframes 以及外部数据。跨源 CSS、仅由伪元素触发的变化、canvas 状态以及多步交互需要手动发现。

在每次标准或深度 `TEARDOWN_PHASE`（拆解阶段）期间，调用 `design-dna` 技能并将完整的 JSON 保存在 `.gcw/evidence/design-dna/design-dna.json`。极简拆解推荐该证据，但即使缺失也不会阻塞定稿。在 `SITE_SPEC.md` 中总结关键发现；不要把兄弟 Schema 复制到第二份 gcw 文档中。如果所需的 `design-dna` 不可用，请停止并告知用户需要安装什么；不要用粗糙的猜测代替。

如果检测到 Canvas、WebGL、WebGPU 或着色器，还要调用 `web-shader-extractor`。将其原生制品保存在 `.gcw/evidence/web-shader-extractor/` 下，并达到 `TARGET_LOCKED` 和 `REPLAY_READY` 状态；拆解阶段不需要原始回放（Raw Replay）或 QA 报告。如果所需的伴随工具不可用，请在定稿前停止。当侦察确认没有符合条件的 GPU 表面时，将 `gpu-decision.json` 设置为 `not-applicable` 并引用相关的盘点证据。

Only after these decisions and calls are complete, integrate their results into `SITE_SPEC.md`, remove every `REQUIRED` placeholder, then run:

```text
python <skill-root>/scripts/finalize_teardown.py <workspace>
```

定稿脚本会验证伴随制品，更新 `teardown-manifest.json` 和 `evidence-index.json`，并将 SITE_SPEC 标记为最终版（final）。当拆解是最终输出时，应用相同的契约；仅用于研究的工作只会改变停止点，而不会改变拆解深度。

## 4. 构建限定范围的忠实基线

只恢复商定的页面、组件和状态。保留深层链接和响应式行为。用显式挡板（fixtures）替换不可用的服务。验证生产构建和预览，然后运行路由检查：

```text
python <skill-root>/scripts/route_smoke.py --base-url <preview-url> --route / --route /example
```

单页应用（SPA）的 HAR 挡板（fixtures）需要显式启用。在评审过的捕获配置中设置精确的 `harFixture.urlFilter`，需要时把第三方 API源添加到 `harFixture.rebaseOrigins`，然后记录并回放每个场景的固件：

```text
node <skill-root>/scripts/capture_compare.mjs --config <capture-scenarios.json> --output <record-results> --record-har <har-dir>
node <skill-root>/scripts/capture_compare.mjs --config <offline-capture-scenarios.json> --output <replay-results> --replay-har <har-dir>
```

记录过程会剥离凭据标头/Cookie，对敏感的查询/请求体字段进行脱敏，并在保存每个 HAR 之前将捕获的服务源重构到候选源。回放过程会阻止 Service Workers，优先匹配 HAR，阻止非本地的不匹配请求，并在 `capture-manifest.json` 中记录备用方案/被阻止的请求。对于完全离线的固件检查，把两个回放 URL 都指向本地候选预览，并验证候选侧的 API 路径没有出现在 `harFixtures.fallbacks` 中。

对于资源密集型或离线工作，阅读 `references/asset-provenance.md` 并从盘点生成不覆盖已有内容的草稿：

```text
python <skill-root>/scripts/generate_asset_manifest.py <workspace>/.gcw/evidence/site-inventory.json --out <workspace>/.gcw/asset-manifest.json
```

生成器会对静态资源进行分类和去重，提出确定性的本地路径，排除 API 噪声，并对不安全的 URL 进行脱敏。它会写入 `reviewStatus: pending`；在把状态更改为 `confirmed` 并运行 `download_assets.py` 之前，确认复用权限、用途、归属、范围和路径。它绝不会下载或覆盖已存在的清单。

对于最终的可维护源码构建和创意构建，阅读 `references/runtime-independence.md`。而恢复配置应阅读 `references/recovery-tiers.md` 和 `references/gates.md`，并添加溯源、哈希值、回放策略、路由/部署连续性、已知差距（Known Gaps）以及维护的 CI。使用 `MAINTAINABLE_REBUILD` 表示恢复后的可维护实现；`EDITABLE_REBUILD` 仅为已迁移的旧版别名。

对于 B/C，可以先把 `ARTIFACT_REPLAY` 构建为独立的预言机（oracle），但它不能作为最终的候选方案。在进行正式评审之前，完成 `.gcw/editability-evidence.json` 和 `.gcw/REPLACE_GUIDE.md`。证明一个可维护的源码入口点，证明在不编辑已部署包的情况下进行一次受控的内容更改，以及证明运行时的独立性。仅包含生产制品的重新运行无法通过交付关卡。

## 5. 验证匹配的状态

阅读 `references/qa-scenarios.md` 和 `references/tooling.md`：

```text
node <skill-root>/scripts/capture_compare.mjs --config <capture-scenarios.json> --output <results-dir>
python <skill-root>/scripts/batch_image_diff.py <results-dir> --diff-dir <results-dir>/diff
```

匹配视口、DPR（设备像素比）、路由、指针、滚动、随机种子、就绪状态和时间阶段。检查截图和 Diff 图像。完成 `CLONE_REPORT.md`，包括交付契约、子系统真实度、所需的可编辑性证据以及已知差距（Known Gaps）。只有在用户允许提交时，才留下本地的 `faithful-baseline` 检查点。

## 6. 在 REVIEW_GATE 处暂停

展示基线、预览、截图、Diff、`CLONE_REPORT.md` 以及已知差距。在用户做出选择前，不要开始创意更改：

- A: 保真度不足；返回 `FAITHFUL_CLONE`（忠实克隆）。
- B: 基线已接受；停止。
- C: 基线已接受以进行创新；创建 `.gcw/CREATIVE_BRIEF.md`，然后进入 `CREATIVE_REBUILD`（创意重建）。

使用 `scripts/advance_workflow.py` 记录状态流转。进入 `REVIEW_GATE` 需要一份完成的 `CLONE_REPORT.md`；B/C 此外还需要确认过的可编辑性证据，且拒绝将最终策略设为 `ARTIFACT_REPLAY`。离开关卡时会重新验证交付契约，需要指定 `--decision A|B|C` 参数，且选定的目标必须与上述列表匹配。决策 C 可以将已接受的 B 基线升级为 C，并且需要完成 `CREATIVE_BRIEF.md`；脚本绝不会自行创建或填充该凭证。在 B 交付达到 `COMPLETE` 之后，用户后续可以通过 `--to CREATIVE_REBUILD --decision C` 重新开始；这将在升级持久化契约前重新验证已接受的 B 决策和可编辑性证据。选择 A 无法使用此路径。在 `finalize_teardown.py` 通过之前，脚本拒绝离开拆解阶段。

## 7. 诚实收尾

重新运行承诺的 QA，报告跳过的检查，并区分观察到的行为、许可复用和原始实现。在发布改编版之前，清除追踪代码和原品牌残留。未经用户授权，切勿推送（push）、打标签（tag）、发布（release）或部署。
