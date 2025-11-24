#!/usr/bin/env python3
"""
Test script to verify categorized logging is working correctly
Run this to ensure all log categories are creating proper log files
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.utils.logger import get_logger, LogCategory
from src.config.settings import get_settings

def test_all_categories():
    """Test logging to all categories"""
    settings = get_settings()
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    print("🧪 Testing Categorized Logging System")
    print("=" * 50)
    print(f"Log directory: {log_dir.absolute()}")
    print(f"Environment: {settings.environment.value}")
    print()
    
    # Test each category
    categories = {
        "API": ("src.web.app", LogCategory.API),
        "Business": ("src.coordination.coordinator", LogCategory.BUSINESS),
        "Agents": ("src.agents.base_agent", LogCategory.AGENTS),
        "Tasks": ("src.tasks.generation_tasks", LogCategory.TASKS),
        "WebSocket": ("src.web.websocket_manager", LogCategory.WEBSOCKET),
        "Database": ("src.context.context_manager", LogCategory.DATABASE),
        "LLM": ("src.llm.gemini_provider", LogCategory.LLM),
        "General": ("src.utils.cache", LogCategory.GENERAL),
    }
    
    print("Testing log categories:")
    print("-" * 50)
    
    for category_name, (module_name, category) in categories.items():
        logger = get_logger(module_name, category=category)
        
        # Log at different levels
        logger.debug(f"DEBUG: Test message from {category_name}")
        logger.info(f"INFO: Test message from {category_name}")
        logger.warning(f"WARNING: Test message from {category_name}")
        logger.error(f"ERROR: Test message from {category_name}")
        
        # Check if log file exists
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = log_dir / f"{category.value}_{settings.environment.value}_{timestamp}.log"
        error_file = log_dir / f"error_{settings.environment.value}_{timestamp}.log"
        
        status = "✅" if log_file.exists() else "❌"
        print(f"{status} {category_name:12} -> {log_file.name}")
        
        if log_file.exists():
            size = log_file.stat().st_size
            print(f"   └─ Size: {size} bytes")
    
    # Check error log
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d')
    error_file = log_dir / f"error_{settings.environment.value}_{timestamp}.log"
    if error_file.exists():
        size = error_file.stat().st_size
        print(f"✅ Error log      -> {error_file.name} ({size} bytes)")
    
    print()
    print("=" * 50)
    print("✅ Logging test complete!")
    print()
    print("📁 Check log files in:", log_dir.absolute())
    print()
    print("To view logs in real-time:")
    print(f"  tail -f {log_dir}/api_{settings.environment.value}_*.log")
    print(f"  tail -f {log_dir}/error_{settings.environment.value}_*.log")

if __name__ == "__main__":
    test_all_categories()

