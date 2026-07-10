# CLI 实现骨架说明

## 当前状态

`host/cli/` 已从零依赖 Python CLI 骨架，推进到“按方法体章节驱动的可运行初版”，用于验证：

- 标准输入读取
- 最小合同校验
- 核心模板/规则资产加载
- 基于 ISA95 + IEC62443 的章节化文档装配
- 事实 / 建议 / 假设 / 待确认项分离表达
- 输出前结构自检
- 证据优先级与冲突消解
- 规则主题驱动
- 章节级表达改写与正式成文初步编排
- 高可用 / 冗余建议的边界化表达
- 多样例回归验证

## 当前目录

```text
host/cli/
  README.md
  cli-mvp-plan.md
  interface-contract.md
  IMPLEMENTATION.md
  VERIFICATION.md
  pyproject.toml
  examples/
  scripts/
  src/
    planner_cli/
      __init__.py
      core_loader.py
      evidence_policy.py
      exit_codes.py
      inference.py
      input_loader.py
      main.py
      models.py
      phrasing.py
      planner.py
      prose.py
      formal_support.py
      rule_topics.py
      validation.py
```

## 当前实现能力

当前实现已经完成：

- `generate` 子命令
- `--input`
- `--output`
- `--strict`
- 基于标准输入样例生成正式 HTML
- 按 `report-outline` 13 章结构输出
- 每章输出章节摘要、章节结论、目标、输入来源、规则主题、适用前提、闭环条件
- 条目级来源标注
- ISA95 / IEC62443 / 地址 / 部署 / 高可用推演初版
- 输出前结构自检
- 多场景样例回归验证

## 当前实现边界

当前实现仍然是“可运行初版”，尚未完成：

- 对 `industrial-network-planner/SKILL.md` 读取顺序的完整自动执行
- 对所有 `references/` 规则的深度结构化解析
- 更细粒度的字段级证据约束与冲突消解
- 更成熟的正式交付文稿语言质量
- 安装后直接使用 `planner` 命令的打包验证

## 下一步建议

建议接下来按以下顺序继续：

1. 深化复杂场景下的规则推演与冲突消解质量
2. 继续提升正式交付文稿语言质量
3. 补更高复杂度样例与验证策略
4. 再决定是否补测试与安装说明
