# CLI 验证说明

## 当前验证目标

本文件用于记录 `host/cli` 当前实现的样例覆盖范围、回归检查方式与基础质量门槛，帮助判断实现是否稳定朝“客户交付级工业网络方案生成”方向推进。

## 当前覆盖样例

### 1. 标准样例
- `industrial-network-planner/examples/standard-input-example.json`

### 2. 最小可运行样例
- `host/cli/examples/minimal-viable-input.json`

### 3. 高完整度样例
- `host/cli/examples/high-completeness-input.json`

### 4. 远程维护主导样例
- `host/cli/examples/remote-maintenance-heavy-input.json`

### 5. 地址受限继承样例
- `host/cli/examples/address-constrained-input.json`

### 6. 多车间协同样例
- `host/cli/examples/multi-workshop-input.json`

### 7. 高冗余诉求样例
- `host/cli/examples/redundancy-demand-input.json`

### 8. 多重冲突组合样例
- `host/cli/examples/compound-conflict-input.json`

### 9. 基础冲突样例
- `/tmp/conflict-input.json`

## 回归脚本

执行方式：

```bash
python3 host/cli/scripts/run_regression.py
```

当前检查内容包括：

- 每个样例都能成功生成正式 HTML
- 输出中包含以下关键标记：
  - `## 输出前自检`
  - `## 证据边界说明`
  - `**章节摘要**`
  - `**章节结论**`
  - `**规则主题**`

## 基础质量门槛检查

执行方式：

```bash
python3 host/cli/scripts/check_report_quality.py
```

当前检查内容包括：

- 是否覆盖核心章节标题
- 是否存在明显占位式表达
- 文档章节数量是否达到基本结构要求

## 当前结论

当前回归样例与质量门槛检查已证明：

- CLI 主流程可运行
- 不同输入丰富度下都能形成结构完整的方案文档
- 远程维护主导、地址强继承、多车间协同、高冗余诉求等场景均可生成稳定输出
- 基础冲突与多重冲突组合场景下能保持证据边界和降级策略
- 章节叙述、章节结论与规则主题均可稳定输出
- 当前输出已通过基础质量门槛，未发现明显占位式措辞残留

## 当前仍未被充分验证的部分

以下能力仍需后续继续增强验证：

- 更复杂行业差异下的规则适应性
- 冲突消解的细粒度质量，而不仅是结构层面的降级
- 更成熟的正式交付文稿语言质量
- 对超大输入规模、更多对象数量和更复杂依赖关系的鲁棒性

## 建议下一步

建议后续继续增强：

- 行业类型差异化样例
- 更细粒度的冲突质量评估
- 更自然的正式交付文稿润色
- 更系统的中间推演深度

这样才能更接近“最终客户交付级方案生成器”的验证要求。
