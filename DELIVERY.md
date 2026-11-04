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
| Python | 审查修复后 22 项 pytest 与 Ruff 全部通过 |
| Compose | Linux aarch64 上四服务与独立测试桩均 healthy；仅 127.0.0.1:8080 暴露 |
| 全链路测试桩 | 真实 HTTP 五层链路返回 200，3 项命中/1 项缺口，权重 9/10，90 分，mode=test |
| 浏览器 | Chrome 桌面与 Pixel 7 共 4 项 Playwright 通过，其中 2 项不拦截 API |
| 真实 DeepSeek | 尚未验证，等待用户在本地填写 API key |
| GitHub CI / GHCR | PR #1 两轮全部通过（41800911602 / 41801960117）；中文历史改写后最终检查与 main 镜像发布继续核验 |
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
- DeepSeek /models 从 Python 容器访问在 0.35 秒收到 401，证明网络可达；无密钥业务请求返回 503 LLM_NOT_CONFIGURED。这不是一次真实模型成功调用。

## 中文提交历史

根据用户明确要求，已将全部历史提交信息改为中文，保留代码树、提交拆分、作者与原始时间。远端通过精确 force-with-lease 原子更新，未覆盖其他人的提交。历史改写导致 SHA 更新，旧回滚版本 0af54bf / 7b05387 分别对应 4150188 / bba0256；已按新标签再次部署验证，证据文件记录当前历史的版本号。旧 CI 运行仍是真实执行记录，其源树与对应中文提交相同。
