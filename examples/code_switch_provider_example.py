"""
示例：在代码中切换 LLM 提供商

这个示例展示了如何在代码中切换使用不同的 LLM 提供商（Ollama、Gemini、OpenAI）
"""
import os
from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager
from src.agents.requirements_analyst import RequirementsAnalyst
from src.agents.technical_documentation_agent import TechnicalDocumentationAgent
from src.llm.provider_factory import ProviderFactory


def example_1_use_ollama():
    """示例 1：所有代理使用 Ollama"""
    print("=" * 60)
    print("示例 1：所有代理使用 Ollama")
    print("=" * 60)
    
    # 创建 coordinator，指定使用 Ollama
    coordinator = WorkflowCoordinator(
        context_manager=ContextManager(),
        provider_name="ollama"  # 所有代理都使用 Ollama
    )
    
    # 生成文档
    results = coordinator.generate_all_docs(
        user_idea="创建一个在线购物平台，支持商品浏览、购物车、订单管理等功能",
        profile="team"
    )
    
    print(f"\n✅ 生成的文档: {list(results['files'].keys())}")
    print(f"📁 项目 ID: {results['project_id']}")
    return results


def example_2_use_gemini():
    """示例 2：所有代理使用 Gemini"""
    print("\n" + "=" * 60)
    print("示例 2：所有代理使用 Gemini")
    print("=" * 60)
    
    # 确保设置了 Gemini API Key
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  警告: GEMINI_API_KEY 未设置，将使用环境变量中的配置")
    
    # 创建 coordinator，指定使用 Gemini
    coordinator = WorkflowCoordinator(
        context_manager=ContextManager(),
        provider_name="gemini"  # 所有代理都使用 Gemini
    )
    
    # 生成文档
    results = coordinator.generate_all_docs(
        user_idea="创建一个社交网络应用，连接专业人士",
        profile="team"
    )
    
    print(f"\n✅ 生成的文档: {list(results['files'].keys())}")
    print(f"📁 项目 ID: {results['project_id']}")
    return results


def example_3_mixed_providers():
    """示例 3：混合使用不同提供商（关键文档用 Gemini，其他用 Ollama）"""
    print("\n" + "=" * 60)
    print("示例 3：混合使用不同提供商")
    print("=" * 60)
    
    # 创建 coordinator，为不同代理指定不同提供商
    coordinator = WorkflowCoordinator(
        context_manager=ContextManager(),
        provider_name="ollama",  # 默认使用 Ollama
        provider_config={
            # 需求分析和技术文档使用 Gemini（质量重要）
            "requirements_analyst": "gemini",
            "technical_agent": "gemini",
            "api_agent": "gemini",
            # 其他代理使用 Ollama（节省成本）
            # "pm_agent": "ollama",  # 使用默认
            # "user_agent": "ollama",  # 使用默认
        }
    )
    
    # 生成文档
    results = coordinator.generate_all_docs(
        user_idea="创建一个任务管理应用，支持团队协作",
        profile="team"
    )
    
    print(f"\n✅ 生成的文档: {list(results['files'].keys())}")
    print(f"📁 项目 ID: {results['project_id']}")
    print("\n💡 提示: 需求分析、技术文档、API 文档使用了 Gemini，其他使用了 Ollama")
    return results


def example_4_individual_agents():
    """示例 4：直接创建单个代理并指定提供商"""
    print("\n" + "=" * 60)
    print("示例 4：直接创建单个代理")
    print("=" * 60)
    
    # 创建使用 Ollama 的需求分析代理
    requirements_agent = RequirementsAnalyst(
        provider_name="ollama",
        model_name="dolphin3"  # 可选：指定模型
    )
    
    # 创建使用 Gemini 的技术文档代理
    technical_agent = TechnicalDocumentationAgent(
        provider_name="gemini"
    )
    
    print(f"✅ 需求分析代理: {requirements_agent.provider_name} ({requirements_agent.model_name})")
    print(f"✅ 技术文档代理: {technical_agent.provider_name} ({technical_agent.model_name})")
    
    # 使用代理生成文档
    context_manager = ContextManager()
    project_id = "example_project_001"
    
    # 生成需求文档
    req_path = requirements_agent.generate_and_save(
        user_idea="创建一个博客平台",
        output_filename="requirements.md",
        project_id=project_id,
        context_manager=context_manager
    )
    print(f"\n📄 需求文档: {req_path}")
    
    # 获取需求摘要
    context = context_manager.get_shared_context(project_id)
    if context and context.requirements:
        req_summary = {
            "user_idea": context.requirements.user_idea,
            "project_overview": context.requirements.project_overview,
            "core_features": context.requirements.core_features,
            "technical_requirements": context.requirements.technical_requirements
        }
        
        # 生成技术文档
        tech_path = technical_agent.generate_and_save(
            requirements_summary=req_summary,
            output_filename="technical_spec.md",
            project_id=project_id,
            context_manager=context_manager
        )
        print(f"📄 技术文档: {tech_path}")
    else:
        print("⚠️  无法获取需求摘要")


def example_5_use_provider_factory():
    """示例 5：使用 ProviderFactory 创建提供商实例"""
    print("\n" + "=" * 60)
    print("示例 5：使用 ProviderFactory")
    print("=" * 60)
    
    # 创建 Ollama 提供商
    ollama_provider = ProviderFactory.create(
        provider_name="ollama",
        default_model="dolphin3"
    )
    
    # 创建 Gemini 提供商
    gemini_provider = ProviderFactory.create(
        provider_name="gemini"
        # API Key 从环境变量读取
    )
    
    print(f"✅ Ollama 提供商: {ollama_provider.get_provider_name()}")
    print(f"   模型: {ollama_provider.get_default_model()}")
    print(f"✅ Gemini 提供商: {gemini_provider.get_provider_name()}")
    print(f"   模型: {gemini_provider.get_default_model()}")
    
    # 使用提供商创建代理
    requirements_agent = RequirementsAnalyst(llm_provider=ollama_provider)
    technical_agent = TechnicalDocumentationAgent(llm_provider=gemini_provider)
    
    print(f"\n✅ 需求分析代理使用: {requirements_agent.provider_name}")
    print(f"✅ 技术文档代理使用: {technical_agent.provider_name}")


def example_6_environment_variable():
    """示例 6：使用环境变量设置提供商"""
    print("\n" + "=" * 60)
    print("示例 6：使用环境变量")
    print("=" * 60)
    
    # 在代码中设置环境变量
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["OLLAMA_DEFAULT_MODEL"] = "dolphin3"
    
    # 创建 coordinator（会自动使用环境变量）
    coordinator = WorkflowCoordinator(
        context_manager=ContextManager()
        # provider_name 为 None，会使用环境变量
    )
    
    print(f"✅ 使用环境变量设置的提供商: {os.getenv('LLM_PROVIDER')}")
    print(f"✅ Coordinator 创建的代理将使用: {os.getenv('LLM_PROVIDER')}")


def main():
    """主函数：运行所有示例"""
    print("\n" + "=" * 60)
    print("在代码中切换 LLM 提供商 - 示例")
    print("=" * 60)
    print("\n这些示例展示了如何在代码中切换使用不同的 LLM 提供商")
    print("请根据需要运行相应的示例函数\n")
    
    # 取消注释以运行相应的示例
    
    # 示例 1：使用 Ollama
    # example_1_use_ollama()
    
    # 示例 2：使用 Gemini（需要设置 GEMINI_API_KEY）
    # example_2_use_gemini()
    
    # 示例 3：混合使用不同提供商
    # example_3_mixed_providers()
    
    # 示例 4：直接创建单个代理
    # example_4_individual_agents()
    
    # 示例 5：使用 ProviderFactory
    example_5_use_provider_factory()
    
    # 示例 6：使用环境变量
    example_6_environment_variable()
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("   - 取消注释相应的示例函数来运行")
    print("   - 确保 Ollama 正在运行（如果使用 Ollama）")
    print("   - 确保设置了 GEMINI_API_KEY（如果使用 Gemini）")
    print("   - 查看 CODE_SWITCH_PROVIDER.md 获取更多详细信息")


if __name__ == "__main__":
    main()

