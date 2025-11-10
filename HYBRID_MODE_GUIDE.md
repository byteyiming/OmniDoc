# 混合模式指南 (Hybrid Mode Guide)

## 什么是混合模式？

混合模式是一个智能的 LLM 提供商配置策略，它让**关键的复杂代理使用 Gemini（高质量）**，而**其他代理使用 Ollama（低成本）**。

这样可以：
- ✅ **保证关键文档的质量**：技术文档、API 文档、数据库架构等使用 Gemini
- ✅ **节省成本**：其他文档使用免费的 Ollama
- ✅ **最佳平衡**：质量与成本的完美平衡

## 默认混合配置

当 `LLM_PROVIDER=ollama` 或未设置时，系统会自动启用混合模式：

### 使用 Gemini 的代理（关键文档）

1. **Requirements Analyst** (`requirements_analyst`)
   - 需求文档是项目的基础
   - 需要准确理解用户意图
   - 影响后续所有文档

2. **Technical Documentation Agent** (`technical_agent`)
   - 技术规格文档最复杂
   - 需要遵循详细的指令（8个章节、Mermaid图、API设计等）
   - 技术准确性至关重要

3. **API Documentation Agent** (`api_agent`)
   - API 文档需要精确性
   - 包含详细的端点和数据模型
   - 影响开发者的使用体验

4. **Database Schema Agent** (`database_schema_agent`)
   - 数据库设计是关键决策
   - 影响系统架构和性能
   - 需要准确的关系设计

### 使用 Ollama 的代理（其他文档）

- PM Documentation Agent
- User Stories Agent
- Developer Documentation Agent
- Stakeholder Communication Agent
- User Documentation Agent
- Test Documentation Agent
- Quality Reviewer Agent
- Format Converter Agent
- Project Charter Agent
- Setup Guide Agent
- Marketing Plan Agent
- Business Model Agent
- Support Playbook Agent
- Legal Compliance Agent
- Document Improver Agent

## 如何使用混合模式

### 方法 1：自动启用（推荐）

只需在 `.env` 文件中设置：

```env
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3
```

系统会自动启用混合模式，关键代理使用 Gemini，其他使用 Ollama。

**要求**：需要设置 `GEMINI_API_KEY` 环境变量。

### 方法 2：在代码中显式启用

```python
from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager

# 混合模式：关键代理使用 Gemini，其他使用 Ollama
coordinator = WorkflowCoordinator(
    context_manager=ContextManager(),
    provider_name="ollama",  # 默认使用 Ollama
    provider_config={
        "technical_agent": "gemini",
        "api_agent": "gemini",
        "database_schema_agent": "gemini",
        "requirements_analyst": "gemini",
    }
)

# 生成文档
results = coordinator.generate_all_docs(
    user_idea="创建一个在线购物平台",
    profile="team"
)
```

### 方法 3：自定义混合配置

你可以根据需要自定义哪些代理使用 Gemini：

```python
coordinator = WorkflowCoordinator(
    context_manager=ContextManager(),
    provider_name="ollama",
    provider_config={
        # 只让技术文档使用 Gemini
        "technical_agent": "gemini",
        # 其他都使用 Ollama（默认）
    }
)
```

## 禁用混合模式

### 方法 1：所有代理使用 Ollama

```python
coordinator = WorkflowCoordinator(
    context_manager=ContextManager(),
    provider_name="ollama",
    provider_config={}  # 空的 config，所有代理使用 Ollama
)
```

或者直接设置环境变量，不设置 `GEMINI_API_KEY`：

```env
LLM_PROVIDER=ollama
# 不设置 GEMINI_API_KEY
```

### 方法 2：所有代理使用 Gemini

```python
coordinator = WorkflowCoordinator(
    context_manager=ContextManager(),
    provider_name="gemini"  # 所有代理使用 Gemini
)
```

或者：

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
```

## 混合模式的优势

### 1. 成本效益

- **Gemini 使用**：只用于 4 个关键代理（约 20% 的代理）
- **Ollama 使用**：用于 16+ 个其他代理（约 80% 的代理）
- **成本节省**：相比全部使用 Gemini，可以节省约 80% 的 API 成本

### 2. 质量保证

- **关键文档高质量**：技术文档、API 文档、数据库架构使用 Gemini
- **其他文档足够好**：其他文档使用 Ollama 也能满足需求
- **最佳平衡**：质量与成本的最佳平衡点

### 3. 灵活性

- **可自定义**：可以根据项目需求调整哪些代理使用 Gemini
- **可禁用**：可以完全禁用混合模式
- **可扩展**：可以添加更多代理到 Gemini 列表

## 验证混合模式

### 检查日志

运行文档生成后，查看日志：

```
INFO: Hybrid mode enabled: Key agents (technical, API, database, requirements) use Gemini, others use Ollama
INFO: Agents using Gemini: technical_agent, api_agent, database_schema_agent, requirements_analyst
INFO: Agents using Ollama: pm_agent, user_agent, test_agent, ...
```

### 检查代理配置

```python
from src.coordination.coordinator import WorkflowCoordinator

coordinator = WorkflowCoordinator()

# 检查关键代理
print(f"Technical Agent: {coordinator.technical_agent.provider_name}")
print(f"API Agent: {coordinator.api_agent.provider_name}")
print(f"Database Agent: {coordinator.database_schema_agent.provider_name}")
print(f"Requirements Agent: {coordinator.requirements_analyst.provider_name}")

# 检查其他代理
print(f"PM Agent: {coordinator.pm_agent.provider_name}")
print(f"User Agent: {coordinator.user_agent.provider_name}")
```

预期输出（混合模式）：
```
Technical Agent: gemini
API Agent: gemini
Database Agent: gemini
Requirements Agent: gemini
PM Agent: ollama
User Agent: ollama
```

## 最佳实践

### 1. 开发环境

```env
# .env
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3
# 不设置 GEMINI_API_KEY（所有代理使用 Ollama，免费快速）
```

### 2. 生产环境（混合模式）

```env
# .env.production
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3
GEMINI_API_KEY=your_production_api_key
# 关键文档使用 Gemini，其他使用 Ollama
```

### 3. 高质量模式（全部 Gemini）

```env
# .env.high_quality
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
# 所有文档使用 Gemini（最高质量，但成本较高）
```

## 成本估算

假设生成一个完整的项目文档集：

### 全部使用 Gemini
- 20 个代理 × 平均 5000 tokens = 100,000 tokens
- 成本：约 $0.50 - $1.00（取决于模型）

### 混合模式
- 4 个关键代理使用 Gemini：4 × 5000 = 20,000 tokens
- 16 个其他代理使用 Ollama：免费
- 成本：约 $0.10 - $0.20
- **节省：80%**

### 全部使用 Ollama
- 20 个代理全部使用 Ollama：免费
- 成本：$0
- **但质量可能不够好（特别是技术文档）**

## 故障排除

### 问题 1：混合模式未启用

**症状**：所有代理都使用 Ollama

**解决方案**：
1. 检查是否设置了 `GEMINI_API_KEY`
2. 检查 `provider_config` 是否为空
3. 检查日志中是否有 "Hybrid mode enabled" 消息

### 问题 2：Gemini API 调用失败

**症状**：关键代理报错

**解决方案**：
1. 检查 `GEMINI_API_KEY` 是否有效
2. 检查 API 配额是否足够
3. 检查网络连接

### 问题 3：想禁用混合模式

**解决方案**：
1. 设置 `provider_config={}` 显式禁用
2. 或者不设置 `GEMINI_API_KEY`，系统会自动回退到全部 Ollama

## 总结

混合模式是一个智能的解决方案，它：

1. ✅ **自动启用**：当使用 Ollama 作为默认提供商时自动启用
2. ✅ **成本效益**：节省约 80% 的 API 成本
3. ✅ **质量保证**：关键文档使用 Gemini 保证质量
4. ✅ **灵活配置**：可以自定义哪些代理使用 Gemini
5. ✅ **易于使用**：无需复杂配置，开箱即用

**推荐使用场景**：
- 生产环境（平衡质量与成本）
- 大型项目（需要高质量技术文档）
- 预算有限但需要关键文档高质量

**不推荐使用场景**：
- 开发环境（可以全部使用 Ollama）
- 对质量要求极高的项目（可以全部使用 Gemini）
- 预算充足的项目（可以全部使用 Gemini）

