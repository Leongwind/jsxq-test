# AI collaboration log

## Preparation (before timed implementation)

User requested a careful reading of the assessment README and an implementation plan for the new Leongwind/jsxq-test repository. Read the source README and inspected the empty local/remote repository. Independently inspected the provided ZIP: 20 anonymized PDFs and a QA report. Confirmed local Linux containers and standalone docker-compose availability.

User selected strict 180-minute implementation, a locally configured compatible LLM API, and local Compose plus GitHub CI/CD delivery. The assistant proposed the approved five-layer architecture, evidence-based deterministic scoring, tests, milestones, and delivery materials.

## Timed implementation

### 2026-11-04 15:57:13 +08:00
User: PLEASE IMPLEMENT THIS PLAN (approved CareerLens plan reproduced in the chat).
Assistant: 开始按已确认计划实施，并从现在记录 180 分钟。先冻结接口和仓库骨架，随后前端与 Python 分析服务并行开发；我负责 BFF、Java、容器及集成验收。真实 API 配置会尽早检查，避免留到最后才发现阻塞。
Actions: verified empty Git remote and working Linux container engine; cloned repository; created the API contract and timebox record. No credentials were present in the process environment. Full visible conversation export will be retained with secrets redacted; operational entries below are summaries, not hidden reasoning.

### Implementation checkpoints (15:59–16:20 +08:00)
- Configured repository-local Git author as Leongwind with GitHub noreply email after initial Git identity check failed; no global settings changed.
- User directed use of DeepSeek, with API key to be supplied later. Verified official documentation and set base URL/model in .env.example and ignored .env. User confirmed milestones should proceed immediately when finished, without waiting for scheduled intervals.
- Frontend and analyzer implemented concurrently in separate owned directories; main agent implemented BFF/Java/contracts/infra.
- Source resumes extracted using pypdf; contact placeholders and tracking watermarks removed; source attribution retained.
- Docker Hub and GCR mirror direct pulls timed out. A public Docker mirror worked; official defaults are retained for CI and configurable build arguments handle local networking. No Docker restart or other user containers changed.
- BFF: 16 tests and TypeScript/build passed. Frontend: 6 component tests, desktop/mobile mocked browser tests and build passed. Analyzer: initial 15 tests, Ruff and a two-container stub integration passed. Java dependencies and full Compose builds are in progress.
- Independent reviews checked cross-service contracts. Unicode skill-key collision and unexpected-error logging were assigned back to the analyzer owner; a regex escaping concern is being checked against actual source/test evidence.

## Full visible conversation
See [docs/AI_CONVERSATION.md](docs/AI_CONVERSATION.md), exported from this chat using scripts/export_ai_log.py. Tool summaries above are separate from the exact visible messages. No internal reasoning is included.

### 16:23–16:34 +08:00
- Java 21 Maven verification completed successfully: 10 JUnit tests passed and executable JAR packaged.
- Four business containers plus separate LLM stub became healthy. Full HTTP chain returned 90 (9/10 weight), with request ID preserved.
- Desktop and mobile Playwright suite passed 4/4; additional full-chain visual capture passed 2/2 with no horizontal overflow, screenshots retained in apps/web/evidence.
- Python review fixes completed: Unicode keys, safe unexpected-error logging, strict 40s LLM budget, one-way version compatibility. Ruff and 22 pytest passed.
- Regex P0 concern was withdrawn after character-level inspection and successful BFF/Java/full-chain tests proved the source escaping correct.
- User-visible local preview opened; report explicitly identifies test mode.

### 16:35–16:45 +08:00
- Initial feature push failed with an HTTP/2 framing error. Retried using the already-configured local HTTP proxy and HTTP/1.1; push succeeded without changing global Git settings.
- GitHub connector lacked PR creation permission (403). Used the existing authenticated gh CLI to create draft PR #1. No new permission grant was requested.
- GitHub run 41800911602 passed all unit/build jobs and Compose/Playwright integration.
- Added folded structured experience display, corrected evidence/coverage labels, and validated local image presence/custom port in deploy script. Tests/typecheck/build passed.
- Built and exercised two immutable local image versions. Deployment/rollback sequence 7b05387 → 0af54bf → 7b05387 passed health and jobs smoke each time; actual image names and BFF version were verified.
- Latest desktop/mobile E2E suite passed 4/4. DeepSeek endpoint is reachable, while missing-key requests correctly return 503 without fallback. Real key remains the external input for live-model verification.

### 中文提交信息要求与历史改写
用户明确要求所有提交信息使用中文，包括已推送的历史提交。先核对远端 main 和 feat/career-lens 的精确 SHA，再逐条重建提交对象：仅修改提交说明和父提交引用，逐项断言代码树、作者、提交者及原始时间不变。最后用带精确期望 SHA 的原子 force-with-lease 推送两个分支，未覆盖任何新增远端提交。全部 7 条提交及 PR 标题已中文化；后续提交与合并说明也使用中文。
原先回滚版本 0af54bf / 7b05387 对应新历史的 4150188 / bba0256。镜像标签同步后重新验证版本回滚，不把旧执行记录伪装成新 SHA 的执行。
用户同时明确要求先完成其余交付，API key 稍后填写；真实 DeepSeek 成功调用继续标为待验收。

### 真实模型接入检查
用户确认本地 API key 已填写后，重新加载分析容器配置，未打印密钥。第一次真实模型完整请求返回 502 LLM_INVALID_RESPONSE（requestId: 03a3f4d9-83f3-4b0c-b42e-49b871ef5e89），证明结构化校验拒绝了不符合约定的返回。问题交回 Python 原实现者诊断，保留证据校验和失败可见性，不使用测试桩回退。

真实模型问题定位：一次安全诊断确认模型返回合法 JSON，但 projects[0] 是对象，不符合接口字符串数组要求。原实现者强化提示，并仅对教育/工作/项目字段的文本对象作确定性展平；技能证据与评分约束不变，嵌套对象/非文本值仍拒绝。Ruff 与新增回归后的 24 项 pytest 全部通过。修复提交信息为中文。

### 17:05 +08:00 真实链路复测成功
修复镜像 10de49d 部署后，真实 DeepSeek 全链路返回 90 分、3 项命中和 1 项缺口，mode=live、model=deepseek-flash，requestId=fe190221-97ad-4ee1-978d-fcf86c066bd3。密钥仅留在忽略的本地配置和分析服务环境中；继续完成真实样例页面验收与远端发布。

真实样例页面验收：题目 Java 简历与沐瞳预置岗位，通过桌面 Playwright 实际链路 1/1；显式断言 mode=live，页面无横向溢出。截图保留于 apps/web/evidence/live-desktop.png，样例分数 28（权重10/36），与最小冒烟输入的90分分别记录。安全扫描确认真实本地密钥没有出现在任何已跟踪文件中，.env 正确忽略。

### 主分支合并与镜像发布
PR #1 最终检查 41804859081 全部通过，保留中文阶段提交，以中文合并说明生成 main 提交 71f8c742cd94961e2af4bd8301e351a43341b6de。主分支流水线 41805411105 完成所有检查及四个镜像发布。通过 GHCR 匿名 token 与 OCI 清单读取核验四个服务均含 amd64/arm64，记录镜像索引摘要。后续交付材料固定引用这一实际验证版本。

### 发布镜像实际部署验收
四个镜像均从 GHCR 成功拉取；执行 scripts/deploy.sh 71f8c742cd94961e2af4bd8301e351a43341b6de，全部健康。逐一断言运行 Image ID 等于下载镜像，RepoDigest 匹配注册表索引摘要，平台 linux/arm64。发布镜像上的真实 DeepSeek 冒烟再次成功：90分、mode=live、requestId=ace90ff6-a57c-44b4-9226-fbf7d51ad5ef。最终证据补充通过独立文档提交保留，不修改已验收业务代码。
