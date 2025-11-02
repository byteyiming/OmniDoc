"""
Pytest Configuration and Shared Fixtures
Following Google's software engineering best practices:
- Test isolation
- Reusable fixtures
- Scalable test infrastructure
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.context.context_manager import ContextManager
from src.rate_limit.queue_manager import RequestQueue
from src.utils.file_manager import FileManager
from src.quality.quality_checker import QualityChecker
from src.llm.provider_factory import ProviderFactory


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def context_manager(temp_db):
    """Context manager fixture with temporary database"""
    cm = ContextManager(db_path=temp_db)
    yield cm
    cm.close()


@pytest.fixture
def file_manager(temp_dir):
    """File manager fixture with temporary directory"""
    return FileManager(base_dir=str(temp_dir))


@pytest.fixture
def rate_limiter():
    """Rate limiter fixture with relaxed limits for testing"""
    return RequestQueue(max_rate=1000, period=60)  # High limit for tests


@pytest.fixture
def quality_checker():
    """Quality checker fixture"""
    return QualityChecker(min_words=50)  # Lower threshold for tests


@pytest.fixture
def mock_gemini_provider(monkeypatch):
    """Mock Gemini provider that returns predictable responses"""
    def mock_generate(prompt, **kwargs):
        return """# Test Document

## Section 1
Test content with enough words to pass quality checks.

## Section 2
More test content here.

## Section 3
Additional content for completeness.
"""
    
    class MockProvider:
        def generate(self, prompt, **kwargs):
            return mock_generate(prompt, **kwargs)
        
        def get_default_model(self):
            return "gemini-2.0-flash"
        
        def get_provider_name(self):
            return "gemini"
        
        def get_available_models(self):
            return ["gemini-2.0-flash"]
    
    return MockProvider()


@pytest.fixture
def mock_llm_provider(mock_gemini_provider):
    """Alias for mock_gemini_provider for backward compatibility"""
    return mock_gemini_provider


@pytest.fixture
def sample_requirements_summary():
    """Sample requirements summary for testing"""
    return {
        "user_idea": "Build a simple blog platform",
        "project_overview": "A platform for users to create and share blog posts",
        "core_features": [
            "User authentication",
            "Post creation",
            "Comment system"
        ],
        "technical_requirements": {
            "backend": "Python",
            "database": "SQLite",
            "frontend": "React"
        }
    }


@pytest.fixture
def sample_user_idea():
    """Sample user idea for testing"""
    return "Create a simple task management app"


@pytest.fixture(scope="session")
def api_key_available():
    """Check if API keys are available for integration tests"""
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    return {
        "gemini": gemini_key is not None,
        "openai": openai_key is not None,
        "any": gemini_key is not None or openai_key is not None
    }


@pytest.fixture
def test_project_id():
    """Generate a unique project ID for testing"""
    import uuid
    return f"test_{uuid.uuid4().hex[:8]}"

