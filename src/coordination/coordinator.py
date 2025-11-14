"""Configuration-driven workflow coordinator for OmniDoc."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from src.agents.generic_document_agent import GenericDocumentAgent
from src.agents.special_agent_adapter import SpecialAgentAdapter
from src.agents.special_agent_registry import get_special_agent_class
from src.config.document_catalog import (
    DocumentDefinition,
    load_document_definitions,
    resolve_dependencies,
)
from src.config.settings import get_settings
from src.context.context_manager import ContextManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

ProgressCallback = Callable[[Dict[str, Any]], Awaitable[None]]


class WorkflowCoordinator:
    """Coordinates configuration-driven document generation."""
    
    def __init__(
        self,
        context_manager: Optional[ContextManager] = None,
        provider_name: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self.context_manager = context_manager or ContextManager()
        self.definitions: Dict[str, DocumentDefinition] = load_document_definitions()
        self.provider_name = (provider_name or settings.default_llm_provider or "gemini").lower()
        self.output_root = Path(settings.docs_dir) / "projects"
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.agents = self._build_agents()

    def _build_agents(self) -> Dict[str, Union[GenericDocumentAgent, SpecialAgentAdapter]]:
        """Build agents dictionary, using special agents when configured."""
        agents: Dict[str, Union[GenericDocumentAgent, SpecialAgentAdapter]] = {}
        for definition in self.definitions.values():
            if definition.agent_class == "special":
                # Try to get special agent class
                special_agent_class = get_special_agent_class(definition.id, definition.special_key)
                if special_agent_class:
                    logger.info("Using special agent %s for document %s", special_agent_class.__name__, definition.id)
                    special_agent = special_agent_class(provider_name=self.provider_name)
                    agents[definition.id] = SpecialAgentAdapter(
                        agent=special_agent,
                        definition=definition,
                        base_output_dir=str(self.output_root),
                        context_manager=self.context_manager,
                    )
                else:
                    logger.warning(
                        "Document %s marked as special but no special agent found, falling back to generic",
                        definition.id,
                    )
                    agents[definition.id] = GenericDocumentAgent(
                        definition=definition,
                        provider_name=self.provider_name,
                        base_output_dir=str(self.output_root),
                    )
            else:
                # Use generic agent
                agents[definition.id] = GenericDocumentAgent(
                    definition=definition,
                    provider_name=self.provider_name,
                    base_output_dir=str(self.output_root),
                )
        return agents

    async def async_generate_all_docs(
        self,
        user_idea: str,
        project_id: str,
        selected_documents: List[str],
        codebase_path: Optional[str] = None,  # Reserved for future use
        progress_callback: Optional[ProgressCallback] = None,
    ) -> Dict[str, Dict]:
        del codebase_path  # Currently unused; keep signature for future enhancements

        if not selected_documents:
            raise ValueError("No documents selected for generation.")

        try:
            execution_plan = resolve_dependencies(selected_documents)
        except ValueError as exc:
            logger.error("Invalid dependency graph: %s", exc)
            raise
        
        total = len(execution_plan)
        completed: List[str] = []
        generated_docs: Dict[str, Dict[str, str]] = {}
        results: Dict[str, Dict] = {"files": {}, "documents": []}

        if progress_callback:
            await progress_callback(
                {
                    "type": "plan",
            "project_id": project_id,
                    "documents": ",".join(execution_plan),
                    "total": str(total),
                }
            )

        for index, document_id in enumerate(execution_plan, start=1):
            definition = self.definitions.get(document_id)
            if not definition:
                raise ValueError(f"Unknown document id '{document_id}' in execution plan.")

            agent = self.agents.get(document_id)
            if not agent:
                raise ValueError(f"No agent available for document '{document_id}'.")

            dependency_payload = {
                dependency: generated_docs[dependency]
                for dependency in definition.dependencies
                if dependency in generated_docs
            }

            if progress_callback:
                await progress_callback(
                    {
                        "type": "document_started",
            "project_id": project_id,
                        "document_id": document_id,
                        "name": definition.name,
                        "index": str(index),
                        "total": str(total),
                    }
                )

            output_rel_path = f"{project_id}/{document_id}.md"
            
            # Update adapter's project_id if it's a SpecialAgentAdapter
            if isinstance(agent, SpecialAgentAdapter):
                agent.project_id = project_id
                agent.context_manager = self.context_manager
            
            document_result = await agent.generate_and_save(
                user_idea=user_idea,
                dependency_documents=dependency_payload,
                output_rel_path=output_rel_path,
            )

            generated_docs[document_id] = document_result
            completed.append(document_id)

            results["files"][document_id] = document_result["file_path"]
            results["documents"].append(
                {
                    "id": document_id,
                    "name": definition.name,
                    "category": definition.category,
                    "file_path": document_result["file_path"],
                    "generated_at": document_result["generated_at"],
                    "dependencies": definition.dependencies,
                }
            )

            self.context_manager.update_project_status(
                project_id=project_id,
                status="in_progress",
                completed_agents=completed,
                results=results,
                selected_documents=selected_documents,
            )

            if progress_callback:
                await progress_callback(
                    {
                        "type": "document_completed",
                        "project_id": project_id,
                        "document_id": document_id,
                        "name": definition.name,
                        "index": str(index),
                        "total": str(total),
                    }
                )

        results["summary"] = {
            "project_id": project_id,
            "generated_at": datetime.now().isoformat(),
            "total_documents": len(completed),
            "selected_documents": selected_documents,
        }

        self.context_manager.update_project_status(
            project_id=project_id,
            status="complete",
            completed_agents=completed,
            results=results,
            selected_documents=selected_documents,
        )
            
        return results

