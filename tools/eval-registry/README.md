# eval-registry · TC-01 评测登记格式本地骨架（0.1-draft）

> **状态：隔离分支底稿，待独立评测与终审，勿合并。**
> 本目录为 P0 地基工件的评测登记侧骨架；尚未经利益隔离的独立复跑与终审。
> 所有样例为合成占位数据，不含真实身份、客户数据或可识别信息。

## 目录

```
tools/eval-registry/
├── validate_eval_record.py   # TC-01 登记记录校验脚本（Python 标准库，离线）
├── metrics_contract.json     # 评测指标契约（指标族/类型/聚合/等级策略）
├── make_samples.py           # 生成三份合成样例记录（占位指纹）
├── selfcheck.py              # 本地自检：断言三份评测样例预期状态
└── eval-records/
    ├── sample_pass.json              # 绑定齐全、证据齐全 → pass
    ├── sample_unscored.json           # 绑定缺失 → incomplete
    └── sample_evidence_missing.json  # 绑定齐全但缺证据 → unscored
```

委托/身份校验样例属另一工件（TC-02），不在本目录；本自检不引用身份校验器。

## 运行

```powershell
cd tools/eval-registry
python selfcheck.py            # 一键复跑三份样例断言（推荐先跑）
python make_samples.py         # 重新生成合成样例（覆盖 eval-records/）
python validate_eval_record.py eval-records/sample_pass.json
```

退出码：`0` = pass / unscored / valid；`1` = incomplete / rejected（绑定缺失、结构错误或硬性约束冲突）。

## 校验规则（V1–V8）

| 规则 | 语义 |
|---|---|
| V1 | 评测对象 commit SHA 与制品指纹必填且格式合法 |
| V2 | 引擎/规则/数据集版本绑定必填；枚举取值合法 |
| V3 | 评分、证据、授权分组分离；风险等级位于 `score.risk_level`，禁止顶层混写 |
| V4 | 缺证据时 grade 置空、risk_level=unknown，记 unscored |
| V5 | self/participating 不得标 independent；A 级仅非关联独立验证可给 |
| V6 | 真实案例授权未确认禁止入公开集 |
| V7 | 关联前置评测须填版本变更影响说明（提示级） |
| V8 | 已归档记录只读，重测另起新记录（流程约束，非脚本检查） |

## 边界与禁区

- 脚本不联网、不读取或修改远程仓库、不创建分支/PR/Release；
- 样例标识为 `example/…`、`did:example:…`、占位 SHA/指纹，禁止用于真实评测集；
- 标准草案引用不代表兼容认证或被采纳；对外公开 schema、投稿标准组织、邀请外部复跑均须单独审批；
- 本目录代码随仓库根 LICENSE（MIT）；指标名/阈值待与评测套件共同定稿。

## 已知缺口（正文自述，不藏附录）

- 指标契约（`score.metrics` 具体指标集与阈值）待与评测套件对齐；
- 校验脚本尚未接入真实核心仓记录回填；
- 互操作/第二实现复跑断言、CI 接线未做；
- 本骨架未经独立第三方复跑，当前结论仅限本地样例自洽。
