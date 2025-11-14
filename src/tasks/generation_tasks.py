"""
Celery tasks for document generation
"""
import logging
from typing import Dict, List, Optional

from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager
from src.tasks.celery_app import celery_app
from src.utils.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, name="omnidoc.generate_documents")
def generate_documents_task(
    self,
    project_id: str,
    user_idea: str,
    selected_documents: List[str],
    provider_name: Optional[str] = None,
    codebase_path: Optional[str] = None,
) -> Dict:
    """
    Celery task to generate documents for a project
    
    Args:
        project_id: Project identifier
        user_idea: User's project idea
        selected_documents: List of document IDs to generate
        provider_name: Optional LLM provider name
        codebase_path: Optional codebase path
        
    Returns:
        Dictionary with generation results
    """
    context_manager = ContextManager()
    
    try:
        logger.info(f"Starting document generation task for project {project_id}")
        
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "initializing"})
        
        # Create coordinator
        if provider_name:
            coordinator = WorkflowCoordinator(
                context_manager=context_manager,
                provider_name=provider_name
            )
        else:
            coordinator = WorkflowCoordinator(context_manager=context_manager)
        
        # Run generation asynchronously
        import asyncio
        results = asyncio.run(
            coordinator.async_generate_all_docs(
                user_idea=user_idea,
                project_id=project_id,
                selected_documents=selected_documents,
                codebase_path=codebase_path,
            )
        )
        
        # Update project status
        context_manager.update_project_status(
            project_id=project_id,
            status="complete",
            completed_agents=list(results.get("files", {}).keys()),
            results=results,
            selected_documents=selected_documents,
        )
        
        logger.info(f"✅ Document generation completed for project {project_id}")
        return {
            "status": "complete",
            "project_id": project_id,
            "files_count": len(results.get("files", {})),
        }
        
    except Exception as exc:
        logger.error(f"❌ Document generation failed for project {project_id}: {exc}", exc_info=True)
        
        # Update project status with error
        context_manager.update_project_status(
            project_id=project_id,
            status="failed",
            error=str(exc),
            selected_documents=selected_documents,
        )
        
        # Re-raise to mark task as failed
        raise

