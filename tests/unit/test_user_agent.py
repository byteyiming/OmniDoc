"""
Unit Tests: UserDocumentationAgent
Fast, isolated tests for user documentation agent
"""
import pytest
from src.agents.user_documentation_agent import UserDocumentationAgent


@pytest.mark.unit
class TestUserDocumentationAgent:
    """Test UserDocumentationAgent class"""
    
    def test_agent_initialization(self, mock_llm_provider, file_manager):
        """Test agent initialization"""
        agent = UserDocumentationAgent(
            llm_provider=mock_llm_provider,
            file_manager=file_manager
        )
        
        assert agent.agent_name == "UserDocumentationAgent"
        assert agent.file_manager is not None
    
    def test_generate_user_doc(self, mock_llm_provider, file_manager, sample_requirements_summary):
        """Test generating user documentation"""
        agent = UserDocumentationAgent(
            llm_provider=mock_llm_provider,
            file_manager=file_manager
        )
        
        result = agent.generate(sample_requirements_summary)
        
        assert result is not None
        assert len(result) > 0
    
    def test_generate_and_save(self, mock_llm_provider, file_manager, sample_requirements_summary):
        """Test generating and saving user documentation"""
        agent = UserDocumentationAgent(
            llm_provider=mock_llm_provider,
            file_manager=file_manager
        )
        
        file_path = agent.generate_and_save(sample_requirements_summary, output_filename="guide.md")
        
        assert file_path is not None
        assert file_manager.file_exists("guide.md")

