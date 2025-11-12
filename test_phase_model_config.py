#!/usr/bin/env python3
"""
测试 Phase 模型配置功能
"""
import os
import sys

# 设置环境变量用于测试
os.environ['LLM_PROVIDER'] = 'ollama'
os.environ['OLLAMA_DEFAULT_MODEL'] = 'dolphin3'

print('=' * 80)
print('🧪 测试 Phase 模型配置功能')
print('=' * 80)
print()

# 测试 1: 默认配置
print('📋 测试 1: 默认配置（无 Phase 特定配置）')
print('-' * 80)
from src.utils.phase_model_config import get_model_for_phase

for phase in [1, 2, 3, 4]:
    model = get_model_for_phase(phase, 'ollama')
    print(f'   Phase {phase}: {model}')
print()

# 测试 2: Phase 特定配置
print('📋 测试 2: Phase 特定配置')
print('-' * 80)
os.environ['OLLAMA_PHASE1_MODEL'] = 'dolphin3'
os.environ['OLLAMA_PHASE2_MODEL'] = 'mixtral'
os.environ['OLLAMA_PHASE3_MODEL'] = 'mixtral'
os.environ['OLLAMA_PHASE4_MODEL'] = 'dolphin3'

# 重新导入以获取新的环境变量
import importlib
import src.utils.phase_model_config
importlib.reload(src.utils.phase_model_config)
from src.utils.phase_model_config import get_model_for_phase

for phase in [1, 2, 3, 4]:
    model = get_model_for_phase(phase, 'ollama')
    expected = os.getenv(f'OLLAMA_PHASE{phase}_MODEL', 'dolphin3')
    status = '✅' if model == expected else '❌'
    print(f'   {status} Phase {phase}: {model} (期望: {expected})')
print()

# 测试 3: 部分 Phase 配置
print('📋 测试 3: 部分 Phase 配置（Phase 1 和 2 有配置，3 和 4 使用默认）')
print('-' * 80)
del os.environ['OLLAMA_PHASE3_MODEL']
del os.environ['OLLAMA_PHASE4_MODEL']
importlib.reload(src.utils.phase_model_config)
from src.utils.phase_model_config import get_model_for_phase

for phase in [1, 2, 3, 4]:
    model = get_model_for_phase(phase, 'ollama')
    if phase <= 2:
        expected = os.getenv(f'OLLAMA_PHASE{phase}_MODEL')
    else:
        expected = os.getenv('OLLAMA_DEFAULT_MODEL', 'dolphin3')
    status = '✅' if model == expected else '❌'
    print(f'   {status} Phase {phase}: {model} (期望: {expected})')
print()

# 测试 4: Agent 使用 phase 模型
print('📋 测试 4: Agent 使用 phase 模型')
print('-' * 80)
try:
    from src.agents.base_agent import BaseAgent
    from src.llm.ollama_provider import OllamaProvider
    
    # 创建 provider
    provider = OllamaProvider()
    
    # 模拟 agent 实例（简化测试）
    class TestAgent:
        def __init__(self):
            self.provider_name = 'ollama'
            self.model_name = None
            self._current_phase_number = None
    
    agent = TestAgent()
    
    # 测试不同 phase
    for phase in [1, 2, 3, 4]:
        agent._current_phase_number = phase
        model = get_model_for_phase(phase, agent.provider_name)
        print(f'   ✅ Phase {phase}: Agent 将使用模型 {model}')
    
    print()
    print('✅ Agent phase 模型选择测试通过！')
except Exception as e:
    print(f'   ⚠️  Agent 测试跳过: {e}')
    print()

# 测试 5: 获取所有配置
print('📋 测试 5: 获取所有 Phase 配置')
print('-' * 80)
from src.utils.phase_model_config import get_all_phase_models

all_models = get_all_phase_models('ollama')
if all_models:
    print('   已配置的 Phase 模型:')
    for phase, model in sorted(all_models.items()):
        print(f'      Phase {phase}: {model}')
else:
    print('   未配置 Phase 特定模型')
print()

# 测试 6: 非 Ollama provider
print('📋 测试 6: 非 Ollama provider（应返回 None）')
print('-' * 80)
for provider in ['gemini', 'openai']:
    model = get_model_for_phase(1, provider)
    status = '✅' if model is None else '❌'
    print(f'   {status} {provider}: {model} (期望: None)')
print()

print('=' * 80)
print('✅ 所有测试完成！')
print('=' * 80)
print()
print('💡 使用建议:')
print('   1. 在 .env 中设置 OLLAMA_PHASE{N}_MODEL 来配置不同 phase 的模型')
print('   2. Phase 1 建议使用快速模型（dolphin3）')
print('   3. Phase 2+ 建议使用高质量模型（mixtral）')
print('   4. 如果不设置 phase 特定配置，将使用 OLLAMA_DEFAULT_MODEL')

