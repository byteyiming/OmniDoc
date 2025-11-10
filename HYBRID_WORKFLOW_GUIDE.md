# 混合工作流（Hybrid Workflow）指南

## 概述

混合工作流是一个专业级的文档生成系统，结合了**质量门（Quality Gate）**和**并行化（Parallelization）**两种策略，既能保证最高质量（通过 Gemini 的迭代改进），又能保证最高速度（通过并行化）。

## 工作流架构

### Phase 1: 质量门（Quality Gate）- 奠基性文档

对最关键的"奠基性"文档使用"生成 → 检查 → 改进"的**迭代循环**，确保最高质量。

#### 包含的文档

1. **Requirements（需求文档）**
   - 阈值：80.0
   - 重要性：所有其他文档的基础

2. **Project Charter（项目章程）**（Team only）
   - 阈值：75.0
   - 重要性：战略级文档

3. **User Stories（用户故事）**
   - 阈值：75.0
   - 重要性：产品级文档

4. **Technical Documentation（技术文档）**
   - 阈值：70.0
   - 重要性：技术级文档的基础

#### 工作流程

```
生成 V1 → 质量检查 → 分数 < 阈值？
    ↓                      ↓
   否                    是
    ↓                      ↓
继续使用 V1          生成质量反馈 → 改进 V2 → 使用 V2
```

### Phase 2: 并行生成（Parallel Execution）- 次要文档

一旦奠基性文档通过了质量门，所有其他依赖于它们的文档将使用 `ParallelExecutor` **并行生成**，以实现最大速度。

#### 包含的文档

- **L3 Tech Agents**: API Documentation, Database Schema, Setup Guide, Developer Documentation
- **Cross-Level Agents**: Test Documentation, User Documentation, Legal Compliance
- **L1/L2 Business Agents** (Team only): PM Documentation, Stakeholder Communication, Business Model, Marketing Plan
- **Support Agents**: Support Playbook

#### 依赖关系

- `setup_guide` 和 `dev_doc` 依赖 `api_doc`
- `stakeholder_doc` 依赖 `pm_doc`
- `marketing_plan` 依赖 `business_model`
- `support_playbook` 依赖 `user_doc`

#### 并行执行

- 最大并行数：8 个任务
- 自动处理依赖关系
- 依赖任务完成后自动触发后续任务

### Phase 3: 最终打包（Final Packaging）

#### 步骤

1. **交叉引用（Cross-Referencing）**
   - 在所有文档之间添加交叉引用
   - 生成文档索引

2. **质量审查（Quality Review）**
   - 生成最终质量报告
   - 评估所有文档的整体质量

3. **Claude CLI 文档**
   - 生成 Claude CLI 可读的文档

4. **格式转换（Format Conversion）**
   - 转换为 HTML、PDF、DOCX 格式

## 配置

### 环境变量

```env
# LLM Provider (推荐使用 Gemini 以获得最佳质量)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key

# 质量阈值（可选，默认值在代码中）
# Requirements: 80.0
# Project Charter: 75.0
# User Stories: 75.0
# Technical Documentation: 70.0

# 并行执行配置（可选）
# 最大并行数：8（在代码中配置）
```

### 代码配置

质量阈值可以在 `_run_agent_with_quality_loop` 调用中自定义：

```python
req_path, req_content = self._run_agent_with_quality_loop(
    agent_instance=self.requirements_analyst,
    agent_type=AgentType.REQUIREMENTS_ANALYST,
    generate_kwargs={"user_idea": user_idea},
    output_filename="requirements.md",
    project_id=project_id,
    quality_threshold=80.0  # 自定义阈值
)
```

## 工作流程示例

### 执行流程

```
🚀 Starting HYBRID Workflow
├── Phase 1: Foundational Documents (Quality Gate)
│   ├── Requirements (V1 → Check → V2 if needed)
│   ├── Project Charter (V1 → Check → V2 if needed)
│   ├── User Stories (V1 → Check → V2 if needed)
│   └── Technical Documentation (V1 → Check → V2 if needed)
│
├── Phase 2: Secondary Documents (Parallel)
│   ├── API Doc, DB Schema (并行)
│   ├── Setup Guide, Dev Doc (等待 API Doc)
│   ├── Test Doc, User Doc, Legal Doc (并行)
│   ├── PM Doc, Business Model (并行，Team only)
│   ├── Stakeholder Doc (等待 PM Doc)
│   ├── Marketing Plan (等待 Business Model)
│   └── Support Playbook (等待 User Doc)
│
└── Phase 3: Final Packaging
    ├── Cross-Referencing
    ├── Quality Review
    ├── Claude CLI Documentation
    └── Format Conversion (HTML, PDF, DOCX)
```

### 日志输出示例

```
🚀 Starting HYBRID Workflow - Project ID: project_20241201_123456, Profile: team
================================================================================
--- PHASE 1: Generating Foundational Documents (Quality Gate) ---
================================================================================
🔍 Running Quality Loop for requirements_analyst...
  📝 Step 1: Generating V1 for requirements_analyst...
  ✅ V1 generated: 5234 characters
  🔍 Step 2: Checking V1 quality for requirements_analyst...
  📊 V1 Quality Score: 65.20/100 (threshold: 80.0)
  ⚠️  [requirements_analyst] V1 quality (65.20/100) is below threshold (80.0). Triggering improvement loop...
  🔍 Step 3a: Generating quality feedback for requirements_analyst...
  ✅ Quality feedback generated: 1234 characters
  🔧 Step 3b: Improving requirements_analyst (V1 -> V2)...
  ✅ V2 (Improved) generated: 6789 characters
  📊 V2 Quality Score: 82.50/100 (improvement: +17.30)
  🎉 [requirements_analyst] Quality loop completed: V1 (65.20) -> V2 (improved)

... (其他奠基性文档类似) ...

================================================================================
✅ PHASE 1 COMPLETE: Foundational documents generated with quality gates
================================================================================
================================================================================
--- PHASE 2: Generating Secondary Documents (Parallel) ---
================================================================================
🚀 Executing 12 parallel tasks...
  ✅ api_documentation: /path/to/api_documentation.md
  ✅ database_schema: /path/to/database_schema.md
  ✅ setup_guide: /path/to/setup_guide.md
  ... (其他文档) ...
================================================================================
✅ PHASE 2 COMPLETE: 12 documents generated in parallel
================================================================================
================================================================================
--- PHASE 3: Final Packaging and Conversion ---
================================================================================
📎 Step 1: Adding cross-references to all documents...
  ✅ Added cross-references to 16 documents
  ✅ Document index created: /path/to/index.md
📊 Step 2: Generating final quality review report...
  ✅ Quality review report generated: /path/to/quality_review.md
📝 Step 3: Generating Claude CLI documentation...
  ✅ Claude CLI documentation generated: /path/to/claude.md
📄 Step 4: Converting documents to multiple formats...
  ✅ Converted 16 documents to 48 files (HTML, PDF, DOCX)
================================================================================
✅ PHASE 3 COMPLETE: Final packaging and conversion completed
================================================================================
🚀 HYBRID Workflow COMPLETED for project project_20241201_123456
================================================================================
```

## 优势

### 1. 质量保证

- **质量门**：确保关键文档达到高质量标准
- **迭代改进**：自动检测并改进低质量文档
- **文档类型特定检查**：使用 `DocumentTypeQualityChecker` 进行精确的质量评估

### 2. 性能优化

- **并行执行**：次要文档并行生成，大幅减少总时间
- **依赖管理**：自动处理文档之间的依赖关系
- **智能调度**：依赖任务完成后立即触发后续任务

### 3. 灵活性

- **可配置阈值**：为不同文档类型设置不同的质量阈值
- **混合模式支持**：可以与混合 LLM 模式（Gemini + Ollama）结合使用
- **可选自动修复**：可以通过 `ENABLE_AUTO_FIX` 启用额外的自动修复循环

## 与混合 LLM 模式的结合

混合工作流可以与混合 LLM 模式完美结合：

```env
# 混合 LLM 模式
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=mixtral
GEMINI_API_KEY=your_key

# 混合工作流自动使用：
# - Phase 1: Gemini（高质量，迭代改进）
# - Phase 2: Ollama（并行，快速，低成本）
```

## 性能对比

### 传统工作流（顺序执行）

- **时间**：~30-45 分钟
- **质量**：取决于模型能力
- **成本**：高（所有文档使用 Gemini）

### 混合工作流

- **时间**：~15-25 分钟（并行执行减少 40-50% 时间）
- **质量**：高（Phase 1 文档通过质量门）
- **成本**：中等（只有 Phase 1 文档使用 Gemini）

## 最佳实践

### 1. 使用 Gemini 进行 Phase 1

Phase 1 文档是基础，使用 Gemini 可以获得：
- 更高的初始质量
- 更好的指令遵循能力
- 更少需要改进的次数

### 2. 合理设置质量阈值

- **Requirements**: 80.0（最高标准）
- **Project Charter**: 75.0（高标准）
- **User Stories**: 75.0（高标准）
- **Technical Documentation**: 70.0（中等标准，可以稍低）

### 3. 监控质量改进

查看日志中的质量改进信息：
```
📊 V2 Quality Score: 82.50/100 (improvement: +17.30)
```

### 4. 检查并行执行结果

查看 Phase 2 的并行执行结果：
```
✅ PHASE 2 COMPLETE: 12 documents generated in parallel
```

## 故障排除

### 问题 1: 质量改进循环失败

**症状**：V1 质量低于阈值，但改进失败

**解决方案**：
1. 检查 `QualityReviewerAgent` 是否正常工作
2. 检查 `DocumentImproverAgent` 是否正常工作
3. 查看日志中的详细错误信息

### 问题 2: 并行执行卡住

**症状**：Phase 2 执行时间过长

**解决方案**：
1. 检查依赖关系是否正确设置
2. 检查是否有任务失败导致依赖阻塞
3. 查看 `ParallelExecutor` 的日志

### 问题 3: 质量阈值过低/过高

**症状**：所有文档都需要改进，或没有文档需要改进

**解决方案**：
1. 调整质量阈值（在 `_run_agent_with_quality_loop` 调用中）
2. 检查 `DocumentTypeQualityChecker` 的配置
3. 查看质量报告了解实际分数

## 总结

混合工作流是一个强大的系统，它：

1. **保证质量**：通过质量门确保关键文档达到高标准
2. **优化性能**：通过并行执行大幅减少总时间
3. **灵活配置**：支持自定义阈值和混合 LLM 模式
4. **自动改进**：自动检测并改进低质量文档

**推荐配置**：
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
```

这将为您提供最佳的质量和性能平衡。

