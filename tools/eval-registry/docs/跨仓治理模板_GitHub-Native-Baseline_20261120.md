# XLGD/LGD 跨仓 GitHub 原生治理基线模板（Native First Baseline）

> 版本：2026-11-20 · 状态：待 Steven Zhao 批准后生效 · 本轮仅出方案，未改动任何远程设置。
> 适用范围：XLGD / LGD / UIBC / LGD-Eval / SynomosAI / Medxpert 公开与私有核心仓。
> 纪律：CI 成功 ≠ 质量验收；内部自评 ≠ 独立第三方验证；功能启用 ≠ 有效运行。

## 1. 仓库分级

| 级别 | 定义 | 代表对象 | 基线强度 |
|---|---|---|---|
| T1 核心治理/协议/评测/发布 | 承载协议、门禁算法、独立评测、对外发布 | lgd-engine、lgd-gate、LGD-Eval、evaluation-protocol、evaluation-evidence、uibc-core、skillgate、skill-audit、lgd-theory、xlgd | 全套强制 |
| T2 产品/MCP/分发 | 对外提供包、MCP 服务、连接器 | medxpert-* 连接器、*-mcp、*-connector、PyPI/MCP 发布仓 | 强制门禁 + 发布安全 |
| T3 工具/静态/内容 | 文档、清单、站点、示例、脚本 | pages、awesome 清单、examples、docs | 轻量门禁 |
| T4 例外 | 套餐受限私有仓、上游 fork/镜像、临时夹具 | 见 `gh-native-audit/exceptions.tsv` | 逐项书面豁免或降级 |

## 2. 分支规则集（Ruleset / Branch Protection）基线

### 2.1 默认分支规则（T1/T2 强制）
- [ ] 目标：默认分支（`~DEFAULT_BRANCH` 或 `refs/heads/main`）。
- [ ] 规则类型：`pull_request`（禁止直接推送）、`required_status_checks`、`non_fast_forward`、`deletion` 禁止。
- [ ] 必需状态检查：绑定**真实存在且近期成功**的 CI/评测门禁（如 `test (3.13)`、`lgd-ci-gate`、独立评测门禁）；规则集/保护中必须枚举上下文，不得留空。
- [ ] `enforce_admins` 开启；管理员不得绕过评审（禁止 `OrganizationAdmin:always` 绕过）。
- [ ] 禁止强制推送（`allow_force_pushes=false`）、禁止删除分支。
- [ ] PR 审查：≥1 名审批人；`dismiss_stale_reviews=true`；核心路径要求 Code Owner 审批；对话全部解决。
- [ ] 推荐：签名提交（`required_signatures`）、线性历史。

**验收标准**：在无审批/检查未绿/存在未解决对话时，PR 无法合并；规则集在网页与 API 双侧一致；绕过授权清单可审计。

### 2.2 标签与发布不可变
- [ ] 发布标签（`refs/tags/v*`）规则：禁止删除、禁止移动（`deletion` + `update` 双禁）。
- [ ] Release 与标签一一对应；标签指向的 commit 与源码、制品、发布说明指纹一致。

## 3. Actions 最小权限与供应链

### 3.1 Token 权限
- [ ] 每个工作流顶层显式声明 `permissions: contents: read`；写权限（contents/packages/security-events/id-token）仅在需要的作业级逐项放开。
- [ ] 禁止无 `permissions` 块（避免取仓库默认写权限）。
- [ ] 定时任务/推送触发的 bot 提交，需限定最小身份与可写路径。

### 3.2 Action 固定
- [ ] 第三方 Action 固定到提交 SHA（保留版本注释）；禁止 `@main/@master/@v*` 浮动引用。
- [ ] 内部跨仓 Action 同样固定 SHA 或已发布不可变版本。
- [ ] 组织级 Actions 策略：精选允许来源 + 强制 SHA 固定（`sha_pinning_required=true`），关闭 `allowed_actions=all`。

### 3.3 外部 PR 隔离
- [ ] 避免 `pull_request_target`；如必须使用，作业不得接触任何非默认 Secrets，`GITHUB_TOKEN` 只读。
- [ ] 外部贡献者 PR 的不可信上下文不得注入发布/评测凭据。

### 3.4 Secrets 边界
- [ ] 发布凭据优先 OIDC 短期凭证（`id-token: write` + 信任关系）；长期 Token（PyPI/GitLab/Zenodo/PAT/API Key）列入台账并定期轮换。
- [ ] 评测 LLM Key 仅限评测作业，不进入发布作业；Secret 命名与引用清单可审计。

## 4. 发布安全与可验证性

- [ ] 发布 Environment（pypi/mcp/服务部署）配置 ≥1 名审批人与部署分支策略；无审批人不得自动发布。
- [ ] OIDC Trusted Publishing 验证可用后，移除长期 Token 兜底。
- [ ] 制品记录 SHA-256 哈希；生成构建来源证明（provenance/attestation）与 SBOM，并随 Release 留存。
- [ ] 留存可下载测试报告、评测结果、构建日志；建立证据索引（EVIDENCE-INDEX）关联版本/commit/制品。
- [ ] 校验源码 commit、标签、包、Release Notes 四者一致；不一致阻断发布。

## 5. 质量门禁有效性（反虚假绿色）

- [ ] 门禁/评测步骤**不得** `continue-on-error: true`；安全扫描类建议性步骤可非阻断，但须与强制门禁分开标注。
- [ ] 门禁调用方必须是利益隔离的独立评测号；同生态自评（如 `LGD-Eval/lgd-gate` 自评算法）仅作参考，不能作为唯一放行依据。
- [ ] 必需检查必须对应近期真实成功的 Run；长期失败/无 Run 的检查上下文须清理或修复。
- [ ] 工作流命名唯一，避免重复定义同名门禁。

## 6. 开发者生态与项目管理

- [ ] 健康文件：CONTRIBUTING、CODE_OF_CONDUCT、SECURITY.md、CODEOWNERS、Issue Forms、PR 模板。
- [ ] 统一治理标签：`bug`、`security`、`feature`、`protocol-change`、`evidence-gap`、`good first issue`、`help wanted`。
- [ ] 核心仓接入统一 Projects V2 路线图；Issue 关联负责人、验收标准、证据链接；跨仓依赖/阻塞显式建模。
- [ ] 设外部贡献者入口（Discussions/复现专区/第三方实现索引）与认可机制。

## 7. 数据与度量

- [ ] 每周只读巡检 Views/Clones/Contributors/Releases/Packages；区分可见数据与不可见数据（dependents、referrers、私有仓流量需补充数据源）。
- [ ] 月度生态增长报告：外部贡献、Issue/PR、复现、外部引用；fork/上游镜像提交不计为自有外部贡献。

## 8. 例外清单（T4）

| 类别 | 数量 | 处置建议 |
|---|---:|---|
| Blocked 套餐受限私有仓 | 18 | 升级 GitHub Pro/Team 后补审计；或书面接受当前不可验证状态 |
| Fork 待裁定 | 18 | 逐仓确认：保留上游镜像（降级基线、开启上游同步）或转为下游治理仓（套用 T1/T2） |
| Scratch 临时/夹具/探针 | 7 | 确认用途后归档、删除或降至 T3 轻量基线 |
| 无工作流静态/内容仓 | 126 | 适用 T3 轻量基线；不强制发布证明与评测门禁 |

> 明细见 `gh-native-audit/exceptions.tsv`；例外须登记理由、有效期与复核人，不得永久豁免强制安全门禁。

## 9. 变更执行门禁

- 本模板任何远程落地（规则集、保护、Actions 策略、Environment、Secrets、工作流改动）均为变更动作，须先提交具体变更计划，经 Steven Zhao 单独批准后执行。
- 落地后回跑只读审计脚本（`gh-native-audit/07/08/11`）复核五态由 M/P 转 V，并留存证据。
