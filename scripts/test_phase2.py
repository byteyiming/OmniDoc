#!/usr/bin/env python3
"""
Phase 2 Test Script: Multi-Agent Documentation Generation
Tests the workflow coordinator with multiple agents
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager


def test_multi_agent_workflow():
    """
    Phase 2 test: Generate requirements + PM documentation from user idea
    """
    print("=" * 60)
    print("Phase 2 Test: Multi-Agent Documentation Generation")
    print("=" * 60)
    print()
    
    # Test input
    test_idea = "Create a simple blog platform"
    print(f"📝 Test Input: '{test_idea}'")
    print()
    
    try:
        # Initialize coordinator with context manager
        context_manager = ContextManager(db_path="test_phase2.db")
        coordinator = WorkflowCoordinator(context_manager=context_manager)
        
        # Generate all documentation
        results = coordinator.generate_all_docs(test_idea)
        
        # Verify results
        print()
        print("=" * 60)
        print("Test Verification:")
        print("=" * 60)
        
        checks = [
            ("Requirements generated", "requirements" in results["files"]),
            ("PM documentation generated", "pm_documentation" in results["files"]),
            ("Project ID created", results.get("project_id") is not None),
            ("Requirements file exists", Path(results["files"]["requirements"]).exists()),
            ("PM file exists", Path(results["files"]["pm_documentation"]).exists()),
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"{status} {check_name}")
            if not check_result:
                all_passed = False
        
        # Check workflow status
        print()
        print("=" * 60)
        print("Workflow Status:")
        print("=" * 60)
        status = coordinator.get_workflow_status(results["project_id"])
        print(f"Completed agents: {status['completed_agents']}")
        print(f"Total outputs: {status['total_outputs']}")
        
        print()
        if all_passed:
            print("✅ ALL CHECKS PASSED!")
            print(f"📄 Generated files: {len(results['files'])}")
            return True
        else:
            print("⚠️  Some checks failed.")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'context_manager' in locals():
            context_manager.close()


if __name__ == "__main__":
    success = test_multi_agent_workflow()
    sys.exit(0 if success else 1)

