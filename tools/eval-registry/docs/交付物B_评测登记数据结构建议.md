# 交付物 B · 评测登记数据结构建议

## 1. 设计原则

- 对象身份、引擎/规则版本、评分、风险、证据、授权状态**分字段存储**，不得混写为一段自由文本；
- 每条评测记录可回溯到源码 commit、制品哈希、规则版本与评测数据集版本；
- 历史记录不可篡改，重测另起新记录并关联前置记录。

## 2. 建议 JSON Schema（字段表）

| 字段组 | 字段 | 类型 | 说明 |
|---|---|---|---|
登记元数据 | eval_id / schema_version / run_at / trigger | string | 评测唯一标识、结构版本、时间、触发原因 |
评测对象 | target.repo / target.commit_sha / target.package_name / target.package_version / target.source_fingerprint_sha256 | string | 身份与源码-制品指纹绑定 |
引擎与规则 | engine.name / engine.version / engine.commit_sha / rule_set_version / rule_fingerprint | string | 评分引擎与规则集版本，规则变更可追溯 |
基准 | benchmark.suite / benchmark.version / benchmark.dataset_version / benchmark.split / benchmark.blind / benchmark.case_kind | string/bool | 测试集版本、公开/留出、真实/合成/模拟 |
验证方 | verifier.identity / verifier.relation / verifier.independent / verifier.method | string/bool | 关系：self / participating / non-affiliated；是否独立 |
评分 | score.metrics{} / score.grade / score.risk_level | object/string | 指标与分级，与风险分级分离 |
证据 | evidence.command / evidence.log_url / evidence.artifacts[{name,sha256,url}] / evidence.coverage | object | 可复现命令、日志、制品哈希、覆盖率 |
授权 | authorization.license / authorization.consent / authorization.data_scope / authorization.privacy_notes | string | 数据授权、隐私与 IP 边界 |
历史 | history.prior_eval_id / history.rerun_reason / history.impact_note | string | 重测关联、规则变更影响说明 |

## 3. 示例骨架

```json
{
  "eval_id": "eval-20261120-001", "schema_version": "1.0", "run_at": "2026-11-20T00:00:00+08:00", "trigger": "rule-release",
  "target": {"repo": "owner/repo", "commit_sha": "…", "package_name": "…", "package_version": "…", "source_fingerprint_sha256": "…"},
  "engine": {"name": "lgd-engine", "version": "…", "commit_sha": "…", "rule_set_version": "…", "rule_fingerprint": "…"},
  "benchmark": {"suite": "uibc-conformance", "version": "…", "dataset_version": "…", "split": "held-out", "blind": true, "case_kind": "synthetic"},
  "verifier": {"identity": "…", "relation": "non-affiliated", "independent": true, "method": "…"},
  "score": {"metrics": {}, "grade": "B", "risk_level": "medium"},
  "evidence": {"command": "…", "log_url": "…", "artifacts": [], "coverage": {}},
  "authorization": {"license": "…", "consent": "…", "data_scope": "…", "privacy_notes": "…"},
  "history": {"prior_eval_id": "…", "rerun_reason": "…", "impact_note": "…"}
}
```

## 4. 当前缺口对照

- 证据索引类资产 22 仓；清单/包元数据 83；制品指纹/证明 14；评分记录 23；风险分级记录仅 3；授权/许可证文件 174。
- 评分、风险、证据、授权尚未结构化分离；历史评测追溯与重测关联不足。
