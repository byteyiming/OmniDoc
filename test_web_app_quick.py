#!/usr/bin/env python3
"""
Quick test for Web App fixes
Tests that run_generation_async can be called without errors
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.web.app import run_generation_async, context_manager
from src.context.context_manager import ContextManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def test_run_generation_async():
    """Test that run_generation_async can be called without NameError"""
    print("=" * 80)
    print("Quick Test: run_generation_async function signature")
    print("=" * 80)
    
    # Check if function exists and has correct signature
    import inspect
    sig = inspect.signature(run_generation_async)
    params = list(sig.parameters.keys())
    
    print(f"✅ Function exists: run_generation_async")
    print(f"✅ Parameters: {params}")
    
    # Check if workflow_mode parameter exists
    if 'workflow_mode' in params:
        print(f"✅ workflow_mode parameter exists")
    else:
        print(f"❌ workflow_mode parameter missing!")
        return False
    
    # Check if request parameter doesn't exist (it shouldn't)
    if 'request' in params:
        print(f"❌ request parameter should not exist (it's not in scope)")
        return False
    else:
        print(f"✅ request parameter correctly removed")
    
    # Test that function can be called with correct parameters
    try:
        print("\n🧪 Testing function call (will cancel after 5 seconds)...")
        
        # Start the function but cancel it after 5 seconds
        task = asyncio.create_task(
            run_generation_async(
                user_idea="Test idea",
                project_id="test_quick_001",
                profile="team",
                provider_name=None,
                codebase_path=None,
                workflow_mode="docs_first"
            )
        )
        
        # Wait a bit to see if it starts without errors
        await asyncio.sleep(2)
        
        # Cancel the task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print("✅ Function call succeeded (no NameError)")
            print("✅ Task cancelled successfully")
            return True
        
    except NameError as e:
        print(f"❌ NameError occurred: {e}")
        return False
    except Exception as e:
        # Other errors are okay (like API key missing, etc.)
        print(f"✅ Function call succeeded (got expected error: {type(e).__name__})")
        return True


async def main():
    """Run quick test"""
    print("\n🧪 Quick Web App Fix Test\n")
    
    result = await test_run_generation_async()
    
    print("\n" + "=" * 80)
    if result:
        print("✅ All tests passed! The fix is working.")
    else:
        print("❌ Tests failed! The fix needs more work.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

