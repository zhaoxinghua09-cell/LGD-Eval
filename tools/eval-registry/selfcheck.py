#!/usr/bin/env python3
"""
selfcheck.py — eval-registry 本地自检（离线，Python 标准库）。

仅校验 TC-01 评测登记样例（pass / incomplete / unscored）。
委托/身份样例属另一工件，不在本目录，故本自检不引用身份校验器。
不联网、不读取或修改远程仓库、不创建分支/PR/Release。

用法: python selfcheck.py [--json]
退出码: 0 = 全部符合预期；1 = 有断言失败。
"""
import json
import os
import sys

import validate_eval_record as ev

HERE = os.path.dirname(os.path.abspath(__file__))

CASES = [
    ("eval-records/sample_pass.json", "pass"),
    ("eval-records/sample_unscored.json", "incomplete"),
    ("eval-records/sample_evidence_missing.json", "unscored"),
]


def load(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as f:
        return json.load(f)


def main():
    results = []
    ok = True

    for rel, expected in CASES:
        rec = load(rel)
        r = ev.validate(rec)
        passed = r["status"] == expected
        ok &= passed
        results.append({
            "case": rel,
            "expected": expected,
            "actual": r["status"],
            "passed": passed,
            "issues": len(r["issues"]),
            "warnings": len(r["warnings"]),
        })

    if "--json" in sys.argv:
        print(json.dumps({"all_passed": ok, "results": results}, ensure_ascii=False, indent=2))
    else:
        print("eval-registry self-check")
        for r in results:
            mark = "PASS" if r["passed"] else "FAIL"
            print(f"  [{mark}] {r['case']}: expected={r['expected']} actual={r['actual']} "
                  f"(issues={r['issues']}, warnings={r['warnings']})")
        print(f"\nall_passed={ok}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
