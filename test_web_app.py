#!/usr/bin/env python3
"""
Test script for Web App functionality
Tests document generation, status checking, and results retrieval
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def test_async_generation():
    """Test async document generation"""
    print("=" * 80)
    print("Test 1: Async Document Generation")
    print("=" * 80)
    
    try:
        context_manager = ContextManager()
        coordinator = WorkflowCoordinator(context_manager=context_manager)
        
        user_idea = "创建一个简单的任务管理应用，支持添加、删除、完成任务"
        project_id = f"test_{asyncio.get_event_loop().time()}"
        
        print(f"📝 User Idea: {user_idea}")
        print(f"🆔 Project ID: {project_id}")
        print(f"👥 Profile: team")
        print(f"🔄 Workflow Mode: docs_first")
        print("\n🚀 Starting generation...")
        
        # Test async generation
        results = await coordinator.async_generate_all_docs(
            user_idea=user_idea,
            project_id=project_id,
            profile="team",
            workflow_mode="docs_first"
        )
        
        print(f"\n✅ Generation complete!")
        print(f"📁 Project ID: {results['project_id']}")
        print(f"📄 Generated files: {len(results.get('files', {}))}")
        
        if results.get('files'):
            print("\n📋 Generated Documents:")
            for doc_type, file_path in results['files'].items():
                print(f"   - {doc_type}: {file_path}")
        
        if results.get('status'):
            print("\n📊 Status:")
            for doc_type, status in results['status'].items():
                print(f"   - {doc_type}: {status}")
        
        if results.get('execution_summary'):
            summary = results['execution_summary']
            print(f"\n📈 Execution Summary:")
            print(f"   Total Documents: {summary.get('total_documents', 0)}")
            print(f"   Successful: {summary.get('successful_count', 0)}")
            print(f"   Failed: {summary.get('failed_count', 0)}")
            print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_sync_generation():
    """Test sync document generation"""
    print("\n" + "=" * 80)
    print("Test 2: Sync Document Generation")
    print("=" * 80)
    
    try:
        context_manager = ContextManager()
        coordinator = WorkflowCoordinator(context_manager=context_manager)
        
        user_idea = "创建一个博客平台，支持用户注册、文章发布、评论功能"
        project_id = f"test_sync_{asyncio.get_event_loop().time()}"
        
        print(f"📝 User Idea: {user_idea}")
        print(f"🆔 Project ID: {project_id}")
        print(f"👥 Profile: individual")
        print(f"🔄 Workflow Mode: docs_first")
        print("\n🚀 Starting generation...")
        
        # Test sync generation
        results = coordinator.generate_all_docs(
            user_idea=user_idea,
            project_id=project_id,
            profile="individual",
            workflow_mode="docs_first"
        )
        
        print(f"\n✅ Generation complete!")
        print(f"📁 Project ID: {results['project_id']}")
        print(f"📄 Generated files: {len(results.get('files', {}))}")
        
        if results.get('files'):
            print("\n📋 Generated Documents:")
            for doc_type, file_path in results['files'].items():
                print(f"   - {doc_type}: {file_path}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_context_manager():
    """Test context manager operations"""
    print("\n" + "=" * 80)
    print("Test 3: Context Manager Operations")
    print("=" * 80)
    
    try:
        context_manager = ContextManager()
        project_id = "test_context_001"
        
        # Create project
        context_manager.create_project(project_id, "Test project idea")
        print(f"✅ Created project: {project_id}")
        
        # Update status
        context_manager.update_project_status(
            project_id=project_id,
            status="in_progress",
            user_idea="Test project idea",
            profile="team",
            completed_agents=[]
        )
        print(f"✅ Updated status: in_progress")
        
        # Get status
        status = context_manager.get_project_status(project_id)
        print(f"✅ Retrieved status: {status.get('status')}")
        
        # Get shared context
        context = context_manager.get_shared_context(project_id)
        print(f"✅ Retrieved shared context: {context is not None}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("🧪 Web App Functionality Tests")
    print("=" * 80)
    print("\nThis script tests:")
    print("1. Async document generation")
    print("2. Sync document generation")
    print("3. Context manager operations")
    print("\n" + "=" * 80 + "\n")
    
    # Test 1: Context Manager
    test_context_manager()
    
    # Test 2: Sync Generation (faster for testing)
    print("\n⏳ Running sync generation test (this may take a while)...")
    sync_results = test_sync_generation()
    
    # Test 3: Async Generation (if sync works)
    if sync_results:
        print("\n⏳ Running async generation test (this may take a while)...")
        async_results = await test_async_generation()
    else:
        print("\n⏭️  Skipping async test (sync test failed)")
        async_results = None
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    print(f"✅ Context Manager: {'PASS' if test_context_manager() else 'FAIL'}")
    print(f"✅ Sync Generation: {'PASS' if sync_results else 'FAIL'}")
    print(f"✅ Async Generation: {'PASS' if async_results else 'FAIL'}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

