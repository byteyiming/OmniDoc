# 在代码中切换 LLM 提供商

## 方法一：修改 WorkflowCoordinator（推荐）

### 1. 创建 Coordinator 时指定提供商

```python
from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager

# 使用 Ollama
coordinator = WorkflowCoordinator(
    context_manager=ContextManager(),
    provider_name="ollama"  # 所有代理都使用 Ollama
)

# 使用 Gemini
coordinator = WorkflowCoordinator(
    context_manager=ContextManager(),
    provider_name="gemini"  # 所有代理都使用 Gemini
)

# 生成文档
results = coordinator.generate_all_docs(
    user_idea="创建一个社交网络应用",
    profile="team"
)
```

### 2. 为不同代理指定不同提供商

```python
from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager

# 创建 coordinator（需要修改代码支持）
coordinator = WorkflowCoordinator(
    context_manager=ContextManager(),
    provider_name="ollama",  # 默认使用 Ollama
    provider_config={
        "requirements_analyst": "gemini",  # 需求分析使用 Gemini
        "technical_agent": "ollama",       # 技术文档使用 Ollama
        "api_agent": "gemini"              # API 文档使用 Gemini
    }
)
```

## 方法二：直接创建代理时指定提供商

### 单个代理使用特定提供商

```python
from src.agents.requirements_analyst import RequirementsAnalyst
from src.agents.technical_documentation_agent import TechnicalDocumentationAgent

# 使用 Ollama 的需求分析代理
requirements_agent = RequirementsAnalyst(
    provider_name="ollama",
    model_name="dolphin3"  # 可选：指定模型
)

# 使用 Gemini 的技术文档代理
technical_agent = TechnicalDocumentationAgent(
    provider_name="gemini",
    model_name="gemini-2.0-flash-exp"  # 可选：指定模型
)

# 使用代理生成文档
req_path = requirements_agent.generate_and_save(
    user_idea="创建一个社交网络应用",
    output_filename="requirements.md"
)

tech_path = technical_agent.generate_and_save(
    requirements_summary={"user_idea": "..."},
    output_filename="technical_spec.md"
)
```

### 指定 API Key

```python
from src.agents.requirements_analyst import RequirementsAnalyst

# 使用 Gemini 并指定 API Key
agent = RequirementsAnalyst(
    provider_name="gemini",
    api_key="your_gemini_api_key_here"
)

# 使用 OpenAI 并指定 API Key
agent = RequirementsAnalyst(
    provider_name="openai",
    api_key="your_openai_api_key_here"
)
```

## 方法三：使用 ProviderFactory 创建提供商

### 创建自定义提供商实例

```python
from src.llm.provider_factory import ProviderFactory
from src.agents.requirements_analyst import RequirementsAnalyst

# 创建 Ollama 提供商
ollama_provider = ProviderFactory.create(
    provider_name="ollama",
    default_model="dolphin3"
)

# 创建 Gemini 提供商
gemini_provider = ProviderFactory.create(
    provider_name="gemini",
    api_key="your_gemini_api_key_here",
    default_model="gemini-2.0-flash-exp"
)

# 使用提供商创建代理
requirements_agent = RequirementsAnalyst(
    llm_provider=ollama_provider
)

technical_agent = TechnicalDocumentationAgent(
    llm_provider=gemini_provider
)
```

## 方法四：修改 WorkflowCoordinator 源码（高级）

### 修改 coordinator.py 支持 provider_name 参数

```python
# 在 src/coordination/coordinator.py 中修改 __init__ 方法

class WorkflowCoordinator:
    def __init__(
        self,
        context_manager: Optional[ContextManager] = None,
        rate_limiter: Optional[RequestQueue] = None,
        provider_name: Optional[str] = None,  # 新增：默认提供商
        provider_config: Optional[Dict[str, str]] = None  # 新增：每个代理的提供商配置
    ):
        """
        Initialize workflow coordinator
        
        Args:
            context_manager: Context manager instance
            rate_limiter: Shared rate limiter for all agents
            provider_name: Default provider name for all agents (uses env var if None)
            provider_config: Dict mapping agent names to provider names (overrides default)
        """
        settings = get_settings()
        self.context_manager = context_manager or ContextManager()
        self.rate_limiter = rate_limiter or RequestQueue(
            max_rate=settings.rate_limit_per_minute, 
            period=60
        )
        self.file_manager = FileManager(base_dir=settings.docs_dir)
        
        # 获取默认提供商（从参数或环境变量）
        default_provider = provider_name or os.getenv("LLM_PROVIDER", "gemini")
        provider_config = provider_config or {}
        
        # 辅助函数：获取代理的提供商
        def get_agent_provider(agent_name: str) -> str:
            return provider_config.get(agent_name, default_provider)
        
        # 初始化代理（使用指定的提供商）
        self.requirements_analyst = RequirementsAnalyst(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("requirements_analyst")
        )
        self.pm_agent = PMDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("pm_agent")
        )
        self.technical_agent = TechnicalDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("technical_agent")
        )
        # ... 其他代理类似
```

## 完整示例

### 示例 1：所有代理使用 Ollama

```python
from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager
import os

# 设置环境变量（可选，也可以在代码中指定）
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["OLLAMA_DEFAULT_MODEL"] = "dolphin3"

# 创建 coordinator
coordinator = WorkflowCoordinator(
    context_manager=ContextManager()
)

# 生成文档
results = coordinator.generate_all_docs(
    user_idea="创建一个在线购物平台",
    profile="team"
)

print(f"生成的文档: {results['files']}")
```

### 示例 2：混合使用不同提供商

```python
from src.agents.requirements_analyst import RequirementsAnalyst
from src.agents.technical_documentation_agent import TechnicalDocumentationAgent
from src.agents.api_documentation_agent import APIDocumentationAgent
from src.context.context_manager import ContextManager
from src.rate_limit.queue_manager import RequestQueue

# 创建共享的 rate limiter
rate_limiter = RequestQueue(max_rate=60, period=60)
context_manager = ContextManager()

# 需求分析使用 Gemini（质量更好）
requirements_agent = RequirementsAnalyst(
    provider_name="gemini",
    rate_limiter=rate_limiter
)

# 技术文档使用 Ollama（免费）
technical_agent = TechnicalDocumentationAgent(
    provider_name="ollama",
    rate_limiter=rate_limiter
)

# API 文档使用 Gemini
api_agent = APIDocumentationAgent(
    provider_name="gemini",
    rate_limiter=rate_limiter
)

# 生成文档
project_id = "project_001"

# 1. 生成需求文档
req_path = requirements_agent.generate_and_save(
    user_idea="创建一个在线购物平台",
    output_filename="requirements.md",
    project_id=project_id,
    context_manager=context_manager
)

# 2. 获取需求摘要
context = context_manager.get_shared_context(project_id)
req_summary = {
    "user_idea": context.requirements.user_idea,
    "project_overview": context.requirements.project_overview,
    "core_features": context.requirements.core_features,
    "technical_requirements": context.requirements.technical_requirements
}

# 3. 生成技术文档
tech_path = technical_agent.generate_and_save(
    requirements_summary=req_summary,
    output_filename="technical_spec.md",
    project_id=project_id,
    context_manager=context_manager
)

# 4. 生成 API 文档
api_path = api_agent.generate_and_save(
    requirements_summary=req_summary,
    technical_summary=tech_path,
    output_filename="api_documentation.md",
    project_id=project_id,
    context_manager=context_manager
)

print(f"需求文档: {req_path}")
print(f"技术文档: {tech_path}")
print(f"API 文档: {api_path}")
```

### 示例 3：在 Web 应用中动态切换

```python
# 在 src/web/app.py 中修改

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager

app = FastAPI()

class GenerationRequest(BaseModel):
    user_idea: str
    project_id: Optional[str] = None
    profile: Optional[str] = "team"
    provider_name: Optional[str] = None  # 新增：允许指定提供商

@app.post("/generate")
async def generate_docs(request: GenerationRequest):
    """生成文档（支持指定提供商）"""
    # 创建 coordinator，使用指定的提供商
    coordinator = WorkflowCoordinator(
        context_manager=ContextManager(),
        provider_name=request.provider_name  # 如果为 None，使用环境变量
    )
    
    # 生成文档
    results = coordinator.generate_all_docs(
        user_idea=request.user_idea,
        project_id=request.project_id,
        profile=request.profile
    )
    
    return results
```

## 使用环境变量（最简单）

```python
import os
from src.coordination.coordinator import WorkflowCoordinator

# 在代码中设置环境变量
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["OLLAMA_DEFAULT_MODEL"] = "dolphin3"

# 创建 coordinator（会自动使用环境变量）
coordinator = WorkflowCoordinator()

# 生成文档
results = coordinator.generate_all_docs("你的项目想法")
```

## 检查当前使用的提供商

```python
from src.agents.requirements_analyst import RequirementsAnalyst

# 创建代理
agent = RequirementsAnalyst(provider_name="ollama")

# 检查提供商信息
print(f"提供商: {agent.provider_name}")
print(f"模型: {agent.model_name}")
print(f"代理名称: {agent.agent_name}")
```

## 最佳实践

### 1. 开发环境使用 Ollama

```python
# 开发时：使用本地 Ollama（免费、快速）
coordinator = WorkflowCoordinator(
    provider_name="ollama"
)
```

### 2. 生产环境使用 Gemini

```python
# 生产时：使用 Gemini（质量高、稳定）
coordinator = WorkflowCoordinator(
    provider_name="gemini"
)
```

### 3. 关键文档使用 Gemini，其他使用 Ollama

```python
# 需求分析和技术文档使用 Gemini（质量重要）
requirements_agent = RequirementsAnalyst(provider_name="gemini")
technical_agent = TechnicalDocumentationAgent(provider_name="gemini")

# 其他文档使用 Ollama（节省成本）
api_agent = APIDocumentationAgent(provider_name="ollama")
user_agent = UserDocumentationAgent(provider_name="ollama")
```

## 注意事项

1. **API Key 安全**：不要在代码中硬编码 API Key，使用环境变量
2. **Rate Limiting**：不同提供商有不同的速率限制，注意共享 rate_limiter
3. **模型兼容性**：确保指定的模型在提供商中可用
4. **成本控制**：Gemini 和 OpenAI 按使用量收费，Ollama 免费但需要本地资源

## 快速参考

```python
# 方法 1：环境变量（最简单）
os.environ["LLM_PROVIDER"] = "ollama"

# 方法 2：创建代理时指定
agent = RequirementsAnalyst(provider_name="ollama")

# 方法 3：使用 ProviderFactory
provider = ProviderFactory.create(provider_name="ollama")
agent = RequirementsAnalyst(llm_provider=provider)

# 方法 4：修改 WorkflowCoordinator（需要修改源码）
coordinator = WorkflowCoordinator(provider_name="ollama")
```

