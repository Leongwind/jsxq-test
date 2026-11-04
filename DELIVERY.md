# CareerLens 交付与验证记录

实施开始：2026-11-04 15:57:13（Asia/Shanghai）。总时限 180 分钟；阶段完成即推进，不等待预算时间段。

## 已实现

Vue 3 → Node BFF → Java/Spring Boot → Python → OpenAI-compatible LLM 完整同步链路；简历文本/脱敏样例、预置岗位/自定义 JD、结构化提取、技能证据校验、归一化、确定性评分、问题与缺口解释。四服务 Compose、健康检查、单元/端到端测试、PR CI 与 SHA 镜像发布配置均已提交实现。

## 已完成的验证

| 项目 | 实际结果 |
| --- | --- |
| BFF | 16 项 Vitest 通过；TypeScript 与生产构建通过 |
| Java | Java 21 容器内 `mvn -B verify` 通过；10 项 JUnit 通过 |
| Web | 6 项 Vitest、TypeScript、Vite 构建通过 |
| Python | 真实模型兼容修复后 24 项 pytest 与 Ruff 全部通过 |
| Compose | Linux aarch64 上四服务与独立测试桩均 healthy；仅 127.0.0.1:8080 暴露 |
| 全链路测试桩 | 真实 HTTP 五层链路返回 200，3 项命中/1 项缺口，权重 9/10，90 分，mode=test |
| 浏览器 | 测试模式 Chrome 桌面与 Pixel 7 共 4 项 Playwright 通过，其中 2 项不拦截 API；真实样例桌面额外 1/1 通过 |
| 真实 DeepSeek | 已通过真实五层链路；deepseek-flash、mode=live，3 项命中/1 项缺口、90 分 |
| GitHub CI / GHCR | PR #1 与 main 检查全部通过；四镜像 amd64/arm64 发布成功、匿名清单核验通过，并实际拉取部署 |
| 固定版本部署/回滚 | 已实际完成 bba0256 → 4150188 → bba0256，三次健康与岗位冒烟通过 |

全链路测试 requestId 示例：`459b5204-c4bb-493b-9a05-b6e06309fcd7`（测试模式，非真实模型）。

## 实际使用的验证命令

```bash
# Docker Hub 直连超时，本机使用可访问镜像；无 Docker 重启或全局镜像配置修改
CAREERLENS_MIRROR=docker.m.daocloud.io/library scripts/compose.sh build
scripts/compose.sh -f compose.yml -f infra/compose.test.yml up -d --no-build --wait
python3 scripts/smoke.py --analyze
# apps/web 下
PLAYWRIGHT_CHANNEL=chrome PLAYWRIGHT_BASE_URL=http://localhost:8080 npm run e2e
# BFF 下
npm run typecheck && npm test && npm run build
# Java 的宿主机没有 Maven，实际使用 Maven/Java 21 容器挂载源码执行 mvn -B verify
```

## 架构取舍与边界

- 岗位目录为 Java 维护的版本化 JSON；没有数据库和持久化用户简历。
- LLM 提取与算法评分分离。证据校验拒绝无原文支撑的技能，评分可单独复算和测试；模型仍可能遗漏技能或误解优先级。
- 不做复杂 OR 条件、跨技能推断、学历/经验/软技能评分；分数不代表录用概率。
- 用户在实施阶段明确改用 DeepSeek。保留 OpenAI-compatible 协议，未声称实际使用 GPT/Claude。
- CI 使用显式测试桩，不使用用户密钥；测试桩成功不能代替真实 LLM 验证。
- 本地仅绑定回环地址。未开发公网多用户所需的鉴权、配额和访问控制；没有进行公网服务器部署。
- 简历与 JD 来源、处理方式见 docs/SOURCES.md。预置 JD 是技术要求节选整理，不是完整招聘原文。

## 部署与回滚方式

目标是四个服务同一 commit SHA 的镜像集合。远端镜像用 `scripts/deploy.sh <sha>` 拉取并启动；已存在的本机镜像用 `scripts/deploy.sh <sha> --local`。回滚使用上一已验证 SHA，并再次等待健康、执行冒烟。

脚本不自动构建缺失版本，也不在失败时自动选择旧版本；必须显式指定目标。实际完成三次版本切换，并通过 BFF /health 返回的 version 与四个容器 Config.Image 逐一确认。证据见 [docs/evidence/rollback.json](docs/evidence/rollback.json)。这验证本地镜像版本回滚，不声称验证了远端服务器或自动故障恢复。

## 答辩与 AI 记录

答辩提纲：docs/DEFENSE.md。AI_LOG.md 记录决策和工具执行摘要；docs/AI_CONVERSATION.md 导出可见用户/助手消息，排除内部推理和工具原始输出，并脱敏密钥。

## 验证证据

- [首轮 GitHub CI](https://github.com/Leongwind/jsxq-test/actions/runs/41800911602)：Python、Web、BFF、Java 和全链路集成全部 success；PR 阶段镜像发布按设计跳过。
- [桌面截图](apps/web/evidence/full-chain-desktop.png)、[移动截图](apps/web/evidence/full-chain-mobile.png)：最新本地版本完整测试链路，明确标注测试模式。
- 新版本完整 Playwright 再次 4/4 通过；桌面、移动均检查无横向溢出。
- 初期无密钥时，DeepSeek /models 返回 401，业务请求返回 503 LLM_NOT_CONFIGURED；随后配置密钥并完成真实模型成功验收，见下节。

## 中文提交历史

根据用户明确要求，已将全部历史提交信息改为中文，保留代码树、提交拆分、作者与原始时间。远端通过精确 force-with-lease 原子更新，未覆盖其他人的提交。历史改写导致 SHA 更新，旧回滚版本 0af54bf / 7b05387 分别对应 4150188 / bba0256；已按新标签再次部署验证，证据文件记录当前历史的版本号。旧 CI 运行仍是真实执行记录，其源树与对应中文提交相同。

## 真实模型验收

2026-11-04 使用本地配置的 DeepSeek 密钥，经 Web → BFF → Java → Python → DeepSeek 完整请求返回成功。模型 `deepseek-flash`，`mode=live`，3 项命中、1 项缺口，匹配分数 90；requestId：`fe190221-97ad-4ee1-978d-fcf86c066bd3`。

首次真实调用曾因模型把项目经历返回为对象而被严格校验拒绝。已明确提示输出字符串，并将常见文本经历对象确定性展平为接口约定的字符串；嵌套对象和非文本值仍拒绝，技能证据与评分规则未放宽。新增两项回归测试后复测成功。没有使用测试桩替代真实结果。

另用题目提供的 Java 简历样例与沐瞳预置岗位完成真实浏览器验收：1/1 Playwright 通过，响应断言 `meta.mode=live`，无横向溢出。该样例得分 28（命中权重 10/总权重 36），与上述最小冒烟输入不同；[真实模型截图](apps/web/evidence/live-desktop.png) 保留了命中、缺口以及被证据校验过滤的提取项。真实模型仍可能遗漏原文技能，因此提示用户核对证据，未将分数表述为录用概率。

## 已发布镜像

[主分支发布流水线](https://github.com/Leongwind/jsxq-test/actions/runs/41805411105) 全部成功，发布版本为 `71f8c742cd94961e2af4bd8301e351a43341b6de`。四个服务镜像的注册表清单均已匿名读取，逐项确认同时包含 `linux/amd64` 与 `linux/arm64`；索引摘要记录在 [registry-release.json](docs/evidence/registry-release.json)。

```bash
scripts/deploy.sh 71f8c742cd94961e2af4bd8301e351a43341b6de
```

此版本为完整功能合并提交。后续提交仅补充交付材料；这里固定引用实际经过发布、清单核验与部署验收的版本，不使用浮动 latest 标签。

发布后，已从 GHCR 拉取四个镜像，在 Linux arm64 容器环境执行上述部署命令；逐一核对运行容器 Image ID 与下载镜像一致，RepoDigest 与注册表清单摘要一致，四服务健康。部署后的真实 DeepSeek 全链路再次返回 90 分、mode=live，requestId：`ace90ff6-a57c-44b4-9226-fbf7d51ad5ef`。完整可机器读取记录见 [ghcr-deployment.json](docs/evidence/ghcr-deployment.json)。

已完成本地固定版本回滚与 GHCR 发布版本部署，两者分别保留证据；没有公网服务器部署。
