#!/usr/bin/env python3
"""生成 TC-01 合成样例记录（占位指纹，无真实数据）。"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "eval-records")
os.makedirs(OUT, exist_ok=True)

def sha1(c): return c * 40
def sha256(c): return "sha256:" + c * 64

passed = {
  "eval_id": "eval-20261120-001",
  "schema_version": "1.0",
  "run_at": "2026-11-20T10:00:00+08:00",
  "trigger": "regression",
  "target": {"repo": "example/uibc-adapter-sample", "commit_sha": sha1("a"),
             "package_name": "example-adapter", "package_version": "0.1.0",
             "source_fingerprint_sha256": sha256("b")},
  "engine": {"name": "lgd-gate", "version": "0.0.0", "commit_sha": sha1("c"),
             "rule_set_version": "r0.0", "rule_fingerprint": sha256("d")},
  "benchmark": {"suite": "uibc-conformance", "version": "0.0.0", "dataset_version": "ds0.0",
                "split": "internal", "blind": False, "case_kind": "synthetic"},
  "verifier": {"identity": "self", "relation": "self", "independent": False,
               "method": "local conformance suite, synthetic cases"},
  "score": {"metrics": {"compat_pass": 6, "compat_total": 7, "regression_pass": 7, "regression_total": 7},
            "grade": "C", "risk_level": "medium"},
  "evidence": {"command": "example-cli run --suite uibc-conformance --dataset ds0.0 --record eval-20261120-001",
               "log_ref": "internal://eval/20261120-001",
               "artifacts": [{"name": "conformance-report.json", "sha256": sha256("e"),
                               "ref": "internal://eval/20261120-001/report.json"}],
               "coverage": {"cases": 7, "passed": 6, "failed": 0, "untested": 1}},
  "authorization": {"license": "Apache-2.0", "consent": "not-required",
                    "data_scope": "synthetic internal-only", "privacy_notes": "no customer data"},
  "history": {"prior_eval_id": None, "rerun_reason": "baseline template", "impact_note": "n/a"}
}

unscored = {
  "eval_id": "eval-20261120-002",
  "schema_version": "1.0",
  "run_at": "2026-11-20T10:30:00+08:00",
  "trigger": "manual",
  "target": {"repo": "example/draft-adapter", "commit_sha": "", "package_name": "",
             "package_version": "", "source_fingerprint_sha256": ""},
  "engine": {"name": "lgd-gate", "version": "", "commit_sha": "", "rule_set_version": "", "rule_fingerprint": ""},
  "benchmark": {"suite": "uibc-conformance", "version": "", "dataset_version": "",
                "split": "internal", "blind": False, "case_kind": "synthetic"},
  "verifier": {"identity": "self", "relation": "self", "independent": False, "method": "draft record"},
  "score": {"metrics": {}, "grade": None, "risk_level": "unknown"},
  "evidence": {"command": "", "log_ref": "", "artifacts": [], "coverage": {}},
  "authorization": {"license": "", "consent": "unknown", "data_scope": "", "privacy_notes": ""},
  "history": {"prior_eval_id": None, "rerun_reason": "", "impact_note": ""}
}

evidence_missing = {
  "eval_id": "eval-20261120-003",
  "schema_version": "1.0",
  "run_at": "2026-11-20T11:00:00+08:00",
  "trigger": "commit-push",
  "target": {"repo": "example/registry-adapter", "commit_sha": sha1("f"),
             "package_name": "registry-adapter", "package_version": "0.2.0",
             "source_fingerprint_sha256": sha256("1")},
  "engine": {"name": "lgd-gate", "version": "0.1.0", "commit_sha": sha1("7"),
             "rule_set_version": "r0.1", "rule_fingerprint": sha256("2")},
  "benchmark": {"suite": "uibc-conformance", "version": "0.1.0", "dataset_version": "ds0.1",
                "split": "internal", "blind": False, "case_kind": "synthetic"},
  "verifier": {"identity": "self", "relation": "self", "independent": False, "method": "not run yet"},
  "score": {"metrics": {}, "grade": None, "risk_level": "unknown"},
  "evidence": {"command": "", "log_ref": "", "artifacts": [], "coverage": {}},
  "authorization": {"license": "MIT", "consent": "not-required", "data_scope": "synthetic internal-only", "privacy_notes": ""},
  "history": {"prior_eval_id": None, "rerun_reason": "", "impact_note": ""}
}

for name, rec in [("sample_pass.json", passed), ("sample_unscored.json", unscored), ("sample_evidence_missing.json", evidence_missing)]:
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    print("wrote", name)
