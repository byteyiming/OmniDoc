# Ollama 请求超时问题修复

## 问题描述

Ollama API 请求在 300 秒（5分钟）后超时，导致文档生成失败。这通常发生在：

1. **使用大型模型**（如 `mixtral`）：生成速度较慢
2. **生成长文档**：需要更多时间生成完整内容
3. **复杂提示词**：模型需要更多时间处理

## 错误示例

```
RuntimeError: Ollama API error: HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=300)
```

## 解决方案

### 1. 增加超时时间（推荐）

在 `.env` 文件中设置 `OLLAMA_TIMEOUT`：

```env
# Ollama request timeout (in seconds)
# Increase for large models or long document generation
OLLAMA_TIMEOUT=600      # Default: 600 seconds (10 minutes)
# OLLAMA_TIMEOUT=1800   # For very long documents (30 minutes)
```

### 2. 动态超时计算

系统现在会根据 `max_tokens` 自动计算超时时间：

- **默认超时**：600 秒（10分钟）
- **动态计算**：`max_tokens * 0.2 + 60` 秒
- **最大超时**：1800 秒（30分钟）

例如：
- `max_tokens=8192` → 超时 ≈ 1700 秒（~28分钟）
- `max_tokens=4096` → 超时 ≈ 880 秒（~15分钟）
- `max_tokens=2048` → 超时 ≈ 470 秒（~8分钟）

### 3. 使用更快的模型

对于开发环境，使用更快的模型：

```env
OLLAMA_DEFAULT_MODEL=dolphin3    # 更快的模型（8B）
# OLLAMA_DEFAULT_MODEL=mixtral   # 更慢但质量更好的模型（47B）
```

### 4. 减少 max_tokens

如果超时仍然发生，可以减少 `max_tokens`：

```env
OLLAMA_MAX_TOKENS=4096   # 减少到 4096 tokens（约 16,000 字符）
# OLLAMA_MAX_TOKENS=8192 # 默认：8192 tokens（约 32,000 字符）
```

### 5. 使用混合模式

对于复杂文档，使用混合模式（Gemini + Ollama）：

```env
LLM_PROVIDER=ollama
GEMINI_API_KEY=your_key

# 关键文档使用 Gemini（更快、更可靠）
# 其他文档使用 Ollama（免费）
```

## 配置指南

### 开发环境（快速迭代）

```env
OLLAMA_DEFAULT_MODEL=dolphin3
OLLAMA_MAX_TOKENS=4096
OLLAMA_TIMEOUT=300      # 5 minutes (faster feedback)
```

### 生产环境（质量优先）

```env
OLLAMA_DEFAULT_MODEL=mixtral
OLLAMA_MAX_TOKENS=8192
OLLAMA_TIMEOUT=1800     # 30 minutes (for complex docs)
```

### 混合模式（推荐）

```env
LLM_PROVIDER=ollama
OLLAMA_DEFAULT_MODEL=dolphin3
OLLAMA_TIMEOUT=600
GEMINI_API_KEY=your_key

# 关键文档自动使用 Gemini（不需要担心超时）
# 其他文档使用 Ollama
```

## 超时时间建议

| 模型 | 推荐超时 | 说明 |
|------|---------|------|
| dolphin3 (8B) | 300-600s | 较快，5-10分钟足够 |
| mixtral (47B) | 600-1800s | 较慢，10-30分钟 |
| llama2 (7B) | 300-600s | 中等速度 |
| codellama (13B) | 600-1200s | 中等速度 |

## 故障排除

### 问题 1：仍然超时

**解决方案**：
1. 增加 `OLLAMA_TIMEOUT` 到 1800 或更高
2. 检查 Ollama 服务是否正常：`ollama list`
3. 检查系统资源（CPU/内存）是否足够
4. 考虑使用更快的模型或混合模式

### 问题 2：生成速度太慢

**解决方案**：
1. 使用更快的模型（dolphin3 而不是 mixtral）
2. 减少 `max_tokens`
3. 使用混合模式（关键文档用 Gemini）
4. 检查系统资源

### 问题 3：内存不足

**解决方案**：
1. 使用较小的模型
2. 关闭其他应用程序
3. 减少并发请求
4. 增加系统内存

## 验证修复

### 检查超时配置

```python
from src.llm.ollama_provider import OllamaProvider
import os

provider = OllamaProvider()
print(f"Request Timeout: {provider.request_timeout} seconds")
print(f"Environment Variable: {os.getenv('OLLAMA_TIMEOUT', 'not set')}")
```

### 测试不同超时值

```python
import os

# 设置超时
os.environ["OLLAMA_TIMEOUT"] = "1800"

from src.llm.ollama_provider import OllamaProvider
provider = OllamaProvider()

# 测试生成
result = provider.generate("Generate a long document...", max_tokens=8192)
print(f"Generated: {len(result)} characters")
```

## 最佳实践

1. **开发环境**：使用较短的超时（300-600s）和较快的模型
2. **生产环境**：使用较长的超时（600-1800s）和混合模式
3. **复杂文档**：使用 Gemini 或增加超时时间
4. **简单文档**：使用 Ollama 和默认超时

## 总结

- ✅ **超时时间可配置**：通过 `OLLAMA_TIMEOUT` 环境变量
- ✅ **动态超时计算**：根据 `max_tokens` 自动调整
- ✅ **更好的错误信息**：提供清晰的超时错误和建议
- ✅ **默认值优化**：从 300 秒增加到 600 秒（10分钟）

**推荐配置**：
```env
OLLAMA_TIMEOUT=600      # 10 minutes (good balance)
OLLAMA_MAX_TOKENS=8192  # Long documents
OLLAMA_DEFAULT_MODEL=dolphin3  # Fast model
```

对于复杂文档，考虑使用混合模式或增加超时到 1800 秒（30分钟）。

