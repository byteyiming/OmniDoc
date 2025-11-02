"""
Unit Tests: ContextManager
Fast, isolated tests for context management
"""
import pytest
from src.context.context_manager import ContextManager
from src.context.shared_context import (
    RequirementsDocument,
    AgentOutput,
    AgentType,
    DocumentStatus
)
from datetime import datetime


@pytest.mark.unit
class TestContextManager:
    """Test ContextManager class"""
    
    def test_create_project(self, context_manager):
        """Test creating a project"""
        project_id = context_manager.create_project("test_001", "Test idea")
        
        assert project_id == "test_001"
    
    def test_save_and_get_requirements(self, context_manager, test_project_id):
        """Test saving and retrieving requirements"""
        req_doc = RequirementsDocument(
            user_idea="Build a blog",
            project_overview="A blogging platform",
            core_features=["Posts", "Comments"],
            technical_requirements={"backend": "Python"},
            user_personas=[],
            business_objectives=["Engagement"],
            constraints=[],
            assumptions=[]
        )
        
        context_manager.create_project(test_project_id, "Build a blog")
        context_manager.save_requirements(test_project_id, req_doc)
        
        retrieved = context_manager.get_requirements(test_project_id)
        
        assert retrieved is not None
        assert retrieved.user_idea == "Build a blog"
        assert retrieved.project_overview == "A blogging platform"
    
    def test_save_and_get_agent_output(self, context_manager, test_project_id):
        """Test saving and retrieving agent outputs"""
        output = AgentOutput(
            agent_type=AgentType.REQUIREMENTS_ANALYST,
            document_type="requirements",
            content="# Requirements",
            file_path="docs/requirements.md",
            quality_score=85.0,
            status=DocumentStatus.COMPLETE,
            generated_at=datetime.now()
        )
        
        context_manager.create_project(test_project_id, "Test")
        context_manager.save_agent_output(test_project_id, output)
        
        retrieved = context_manager.get_agent_output(test_project_id, AgentType.REQUIREMENTS_ANALYST)
        
        assert retrieved is not None
        assert retrieved.agent_type == AgentType.REQUIREMENTS_ANALYST
        assert retrieved.content == "# Requirements"
        assert retrieved.status == DocumentStatus.COMPLETE
    
    def test_get_shared_context(self, context_manager, test_project_id):
        """Test getting complete shared context"""
        context_manager.create_project(test_project_id, "Test idea")
        
        context = context_manager.get_shared_context(test_project_id)
        
        assert context.project_id == test_project_id
        assert context.user_idea == "Test idea"
    
    def test_context_persistence(self, temp_db, test_project_id):
        """Test that context persists across instances"""
        # Create and save
        cm1 = ContextManager(db_path=temp_db)
        cm1.create_project(test_project_id, "Persistent idea")
        
        req = RequirementsDocument(
            user_idea="Persistent idea",
            project_overview="Test",
            core_features=[],
            technical_requirements={},
            user_personas=[],
            business_objectives=[],
            constraints=[],
            assumptions=[]
        )
        cm1.save_requirements(test_project_id, req)
        cm1.close()
        
        # Retrieve in new instance
        cm2 = ContextManager(db_path=temp_db)
        retrieved = cm2.get_requirements(test_project_id)
        cm2.close()
        
        assert retrieved is not None
        assert retrieved.user_idea == "Persistent idea"

