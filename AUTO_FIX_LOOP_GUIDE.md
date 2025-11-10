# 自动修复循环（Auto-Fix Loop）使用指南

## 概述

自动修复循环是一个强大的自我纠错系统，允许本地模型（如 mixtral、dolphin3）通过迭代改进来提升文档质量。当文档质量评分低于阈值时，系统会自动使用 `DocumentImproverAgent` 改进文档。

## 为什么需要自动修复循环？

### 本地模型 vs 云端模型的区别

- **Gemini（云端模型）**：万亿级参数，能够一次性生成高质量、符合复杂指令的文档
- **Mixtral/Dolphin3（本地模型）**：47B/8B 参数，虽然强大，但在遵循极其复杂和冗长的指令时容易"漂移"或"忘记"约束

### 解决方案

与其强求本地模型"一次成功"，不如让系统自动迭代改进：

1. **生成文档** → 使用本地模型生成初始文档
2. **质量评估** → `QualityReviewerAgent` 评估文档质量
3. **自动改进** → 如果质量分数低于阈值，`DocumentImproverAgent` 自动改进文档
4. **迭代提升** → 重复过程直到达到质量标准

## 启用自动修复循环

### 方法 1：环境变量（推荐）

在 `.env` 文件中设置：

```env
# Enable auto-fix loop
ENABLE_AUTO_FIX=true
AUTO_FIX_THRESHOLD=70.0  # Quality score threshold (0-100)
```

### 方法 2：代码配置

在 `src/config/settings.py` 中添加：

```python
enable_auto_fix: bool = True
auto_fix_threshold: float = 70.0
```

## 配置参数

### ENABLE_AUTO_FIX

- **类型**：`boolean` (string: "true" or "false")
- **默认值**：`false`
- **说明**：启用或禁用自动修复循环

### AUTO_FIX_THRESHOLD

- **类型**：`float` (0-100)
- **默认值**：`70.0`
- **说明**：质量分数阈值。文档分数低于此值将被自动改进

**推荐值**：
- **严格模式**：`80.0` - 只改进质量较差的文档
- **平衡模式**：`70.0` - 改进中等质量的文档（推荐）
- **宽松模式**：`60.0` - 改进大部分文档

## 工作流程

### 1. 质量评估

`QualityReviewerAgent` 评估所有生成的文档，生成 `quality_review.md` 报告，包含：
- 总体质量分数
- 每个文档的单独分数
- 改进建议

### 2. 分数提取

系统自动从 `quality_review.md` 中提取：
- **总体分数**：`Overall Quality Score: X/100`
- **文档分数**：每个文档部分的 `Quality Score: X/100`

### 3. 改进决策

系统决定哪些文档需要改进：
- 总体分数 < `AUTO_FIX_THRESHOLD` → 改进所有关键文档
- 文档分数 < `AUTO_FIX_THRESHOLD` → 改进特定文档

### 4. 自动改进

对于需要改进的文档：
1. 读取原始文档内容
2. 提取文档特定的质量反馈
3. 调用 `DocumentImproverAgent` 生成改进版本
4. 覆盖原文件
5. 更新文档字典

### 5. 优先级

改进优先级（按顺序）：
1. **Technical Specification** - 技术规格文档
2. **API Documentation** - API 文档
3. **Database Schema** - 数据库架构
4. **Developer Documentation** - 开发者文档
5. **Requirements** - 需求文档

## 使用场景

### 场景 1：本地模型（Mixtral/Dolphin3）

**推荐配置**：
```env
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=mixtral
ENABLE_AUTO_FIX=true
AUTO_FIX_THRESHOLD=70.0
```

**效果**：
- 初始生成可能得分 40-60 分
- 自动改进后提升到 70-85 分
- 质量接近云端模型水平

### 场景 2：混合模式 + 自动修复

**推荐配置**：
```env
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3
GEMINI_API_KEY=your_key
ENABLE_AUTO_FIX=true
AUTO_FIX_THRESHOLD=70.0
```

**效果**：
- 关键文档（Technical, API, Database）使用 Gemini（高质量）
- 其他文档使用 Ollama（成本低）
- 所有文档通过自动修复循环进一步改进

### 场景 3：云端模型（Gemini）

**推荐配置**：
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
ENABLE_AUTO_FIX=false  # 通常不需要，质量已经很高
```

**效果**：
- 初始生成得分 80-95 分
- 通常不需要自动修复

## 日志输出

### 启用自动修复时

```
🔧 Auto-Fix Loop: Analyzing quality review and improving documents with low scores
📊 Quality Analysis: Overall score = 45/100, Found 8 document scores
⚠️  Overall quality score (45/100) is below threshold (70), triggering auto-fix
  📝 Will improve: Technical Specification (score: 42/100)
  📝 Will improve: API Documentation (score: 38/100)
  📝 Will improve: Database Schema (score: 55/100)
🔧 Auto-improving Technical Specification...
✅ Improved Technical Specification (score: 42/100 → improved)
🔧 Auto-improving API Documentation...
✅ Improved API Documentation (score: 38/100 → improved)
🎉 Auto-Fix Loop: Successfully improved 3 document(s): Technical Specification, API Documentation, Database Schema
```

### 无需改进时

```
✅ Auto-Fix Loop: No documents needed improvement (all scores above threshold)
```

## 最佳实践

### 1. 选择合适的阈值

- **首次使用**：从 `70.0` 开始
- **质量优先**：提高到 `80.0`
- **速度优先**：降低到 `60.0`

### 2. 监控改进效果

查看 `quality_review.md` 和日志，了解：
- 改进前后的分数对比
- 哪些文档需要改进
- 改进是否有效

### 3. 结合混合模式

对于关键文档，使用混合模式（Gemini）生成，然后对所有文档启用自动修复循环。

### 4. 调整改进优先级

如果某些文档类型总是需要改进，可以：
- 提高这些文档的生成质量（使用更好的模型）
- 调整 `AUTO_FIX_THRESHOLD`
- 修改 `documents_to_improve` 列表

## 故障排除

### 问题 1：自动修复未触发

**可能原因**：
1. `ENABLE_AUTO_FIX` 未设置为 `true`
2. 质量分数高于阈值
3. 质量评估失败

**解决方案**：
1. 检查 `.env` 文件中的 `ENABLE_AUTO_FIX=true`
2. 降低 `AUTO_FIX_THRESHOLD` 到 `60.0`
3. 检查 `quality_review.md` 文件是否生成

### 问题 2：改进后质量未提升

**可能原因**：
1. 改进提示词不够明确
2. 模型能力限制
3. 原始文档问题太多

**解决方案**：
1. 检查 `DocumentImproverAgent` 的提示词
2. 使用更强大的模型（mixtral 而不是 dolphin3）
3. 启用混合模式（关键文档用 Gemini）

### 问题 3：改进时间过长

**可能原因**：
1. 改进的文档太多
2. 模型响应速度慢
3. 超时设置太短

**解决方案**：
1. 提高 `AUTO_FIX_THRESHOLD` 减少改进数量
2. 使用更快的模型（dolphin3）
3. 增加 `OLLAMA_TIMEOUT`

## 性能影响

### 时间成本

- **每次改进**：额外 30-120 秒（取决于文档大小和模型）
- **改进 3 个文档**：额外 2-6 分钟
- **总体影响**：增加 10-20% 的生成时间

### 质量提升

- **改进前**：40-60 分（本地模型）
- **改进后**：70-85 分（接近云端模型）
- **提升幅度**：+30-45 分

### 成本

- **本地模型**：无额外成本
- **云端模型**：如果改进使用 Gemini，会增加 API 调用成本

## 总结

自动修复循环是一个强大的工具，特别适合：

1. **本地模型用户**：提升文档质量到接近云端模型水平
2. **混合模式用户**：进一步优化所有文档
3. **质量优先项目**：确保文档达到高标准

**推荐配置**：
```env
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=mixtral
ENABLE_AUTO_FIX=true
AUTO_FIX_THRESHOLD=70.0
GEMINI_API_KEY=your_key  # 可选：混合模式
```

这将为您提供最佳的质量和成本平衡。

