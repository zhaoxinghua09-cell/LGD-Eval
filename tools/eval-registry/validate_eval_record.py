#!/usr/bin/env python3
"""
validate_eval_record.py — TC-01 评测登记记录校验脚本（本地草案，标准库实现）。

仅校验本地 JSON 记录的结构与规则一致性；不联网、不读取/修改远程仓库、不发布。
规则编号对应 TC-01 技术设计稿 V1–V8。

用法:
    python validate_eval_record.py <record.json> [--json]

退出码:
    0 = pass / unscored（结构可接受，证据不足已降级）
    1 = incomplete / rejected（绑定缺失或硬性结构错误）
"""
import json, re, sys, hashlib

SHA256_RE = re.compile(r"^(sha256:)?[a-f0-9]{64}$")
SHA1_RE = re.compile(r"^[a-f0-9]{40}$")
RELATIONS = {"self", "participating", "non-affiliated"}
CASE_KINDS = {"real", "synthetic", "simulated"}
SPLITS = {"public", "hold-out", "blind", "internal"}
GRADES = {"A", "B", "C", "D"}
RISK = {"high", "medium", "low", "unknown"}


def _missing(issues, field, msg, rule):
    issues.append({"rule": rule, "field": field, "issue": msg})


def validate(rec: dict):
    issues = []
    warnings = []

    # V1 身份绑定
    t = rec.get("target") or {}
    if not t.get("repo"):
        _missing(issues, "target.repo", "缺评测对象仓库标识", "V1")
    if not t.get("commit_sha"):
        _missing(issues, "target.commit_sha", "缺源码 commit SHA", "V1")
    elif not SHA1_RE.match(str(t["commit_sha"])):
        issues.append({"rule": "V1", "field": "target.commit_sha", "issue": "commit SHA 不是 40 位十六进制"})
    fp = t.get("source_fingerprint_sha256")
    if not fp:
        _missing(issues, "target.source_fingerprint_sha256", "缺源码/制品指纹", "V1")
    elif not SHA256_RE.match(str(fp)):
        issues.append({"rule": "V1", "field": "target.source_fingerprint_sha256", "issue": "指纹不符合 sha256 格式"})

    # V2 版本绑定
    e = rec.get("engine") or {}
    for f in ("name", "version", "commit_sha", "rule_set_version", "rule_fingerprint"):
        if not e.get(f):
            _missing(issues, f"engine.{f}", "引擎/规则版本绑定缺失", "V2")
    b = rec.get("benchmark") or {}
    for f in ("suite", "version", "dataset_version"):
        if not b.get(f):
            _missing(issues, f"benchmark.{f}", "基准/数据集版本缺失", "V2")
    if b.get("split") and b["split"] not in SPLITS:
        issues.append({"rule": "V2", "field": "benchmark.split", "issue": f"split 取值非法: {b['split']}"})
    if b.get("case_kind") and b["case_kind"] not in CASE_KINDS:
        issues.append({"rule": "V2", "field": "benchmark.case_kind", "issue": f"case_kind 取值非法: {b['case_kind']}"})

    # V3 字段分离：score（含 risk_level）/ evidence / authorization 三组独立存在；
    # 风险等级为 score.risk_level 子字段，不得在顶层混写。
    for group in ("score", "evidence", "authorization"):
        if group not in rec:
            issues.append({"rule": "V3", "field": group, "issue": "评分/证据/授权分组缺失，禁止混写自由文本"})
    if "risk_level" in rec:
        issues.append({"rule": "V3", "field": "risk_level", "issue": "风险等级必须位于 score.risk_level，不得顶层混写"})

    # V5 独立性一致
    v = rec.get("verifier") or {}
    rel = v.get("relation")
    ind = v.get("independent")
    if rel and rel not in RELATIONS:
        issues.append({"rule": "V5", "field": "verifier.relation", "issue": f"relation 取值非法: {rel}"})
    if rel in ("self", "participating") and ind is True:
        issues.append({"rule": "V5", "field": "verifier.independent", "issue": "self/participating 不得标记为 independent"})
    if rel == "non-affiliated" and ind is False:
        warnings.append({"rule": "V5", "field": "verifier.independent", "issue": "non-affiliated 通常 independent=true，请复核"})

    # V4 缺证据降级
    ev = rec.get("evidence") or {}
    evidence_ok = bool(ev.get("command")) and bool(fp)
    artifacts = ev.get("artifacts") or []
    if artifacts:
        for i, a in enumerate(artifacts):
            if not a.get("sha256") or not SHA256_RE.match(str(a["sha256"])):
                issues.append({"rule": "V4", "field": f"evidence.artifacts[{i}].sha256", "issue": "制品指纹缺失或格式非法"})
                evidence_ok = False

    score = rec.get("score") or {}
    grade = score.get("grade")
    risk = score.get("risk_level")
    if grade and grade not in GRADES:
        issues.append({"rule": "V3", "field": "score.grade", "issue": f"grade 取值非法: {grade}"})
    if risk and risk not in RISK:
        issues.append({"rule": "V3", "field": "score.risk_level", "issue": f"risk_level 取值非法: {risk}"})
    if grade == "A" and not (rel == "non-affiliated" and ind is True):
        issues.append({"rule": "V5", "field": "score.grade", "issue": "A 级仅可由非关联独立验证给出"})

    # V6 真实案例授权
    auth = rec.get("authorization") or {}
    if b.get("case_kind") == "real" and auth.get("consent") in (None, "pending", "unknown"):
        issues.append({"rule": "V6", "field": "authorization.consent", "issue": "真实案例授权未确认，禁止入公开集"})

    # V7 历史关联（提示级）
    h = rec.get("history") or {}
    if h.get("prior_eval_id") and not h.get("impact_note"):
        warnings.append({"rule": "V7", "field": "history.impact_note", "issue": "关联前置评测时应填规则/版本变更影响说明"})

    # 汇总状态
    hard = [x for x in issues if x["rule"] in ("V1", "V2", "V3")]
    if issues and any(x["rule"] == "V3" and "顶层" in x["issue"] for x in issues):
        status = "rejected"
    elif hard:
        status = "incomplete"
    elif not evidence_ok:
        status = "unscored"
        # 强制降级
        if score.get("grade"):
            warnings.append({"rule": "V4", "field": "score.grade", "issue": "证据不足，grade 应置空"})
        if risk != "unknown":
            warnings.append({"rule": "V4", "field": "score.risk_level", "issue": "证据不足，risk_level 应为 unknown"})
    else:
        status = "pass"

    return {"status": status, "issues": issues, "warnings": warnings,
            "record_id": rec.get("eval_id"), "schema_version": rec.get("schema_version")}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        rec = json.load(f)
    result = validate(rec)
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"record: {result['record_id']}  schema: {result['schema_version']}")
        print(f"status: {result['status']}")
        for x in result["issues"]:
            print(f"  [ISSUE {x['rule']}] {x['field']}: {x['issue']}")
        for x in result["warnings"]:
            print(f"  [WARN  {x['rule']}] {x['field']}: {x['issue']}")
    return 1 if result["status"] in ("incomplete", "rejected") else 0


if __name__ == "__main__":
    sys.exit(main())
