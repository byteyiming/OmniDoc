"""Agent for configuration-driven document generation."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from prompts.system_prompts import READABILITY_GUIDELINES
from src.agents.base_agent import BaseAgent
from src.config.document_catalog import DocumentDefinition
from src.utils.file_manager import FileManager
from src.utils.logger import get_logger
from src.utils.prompt_registry import get_prompt_for_document

logger = get_logger(__name__)


class GenericDocumentAgent(BaseAgent):
    """Generic prompt-driven document generator using catalog metadata."""

    def __init__(
        self,
        definition: DocumentDefinition,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        base_output_dir: str = "docs/generated",
        **provider_kwargs,
    ) -> None:
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            **provider_kwargs,
        )
        self.definition = definition
        self.output_filename = f"{definition.id}.md"
        self.file_manager = FileManager(base_dir=base_output_dir)

    def _build_prompt(
        self,
        user_idea: str,
        dependency_documents: Dict[str, Dict[str, str]],
    ) -> str:
        # Try to get a specialized prompt from the registry
        specialized_prompt = get_prompt_for_document(
            document_id=self.definition.id,
            user_idea=user_idea,
            dependency_documents=dependency_documents,
        )

        if specialized_prompt:
            logger.debug("Using specialized prompt for document %s", self.definition.id)
            return specialized_prompt

        # Fall back to generic template
        logger.debug("Using generic prompt template for document %s", self.definition.id)
        description = self.definition.description or "Generate the requested project documentation."
        guidance = [
            f"You are responsible for producing the document '{self.definition.name}'.",
            f"Document ID: {self.definition.id}",
            f"Category: {self.definition.category or 'General'}",
            f"Priority: {self.definition.priority or 'Unspecified'}",
            "",
            "### Project Idea",
            user_idea.strip(),
            "",
            "### Document Description",
            description,
        ]

        if self.definition.notes:
            guidance.extend(["", "### Additional Notes", self.definition.notes])

        if dependency_documents:
            guidance.extend(["", "### Reference Materials"])
            for dep_id, dep_data in dependency_documents.items():
                excerpt = dep_data.get("content", "").strip()
                if not excerpt:
                    continue
                excerpt = excerpt[:5000]
                guidance.extend(
                    [
                        f"#### {dep_data.get('name', dep_id)} ({dep_id})",
                        excerpt,
                        "",
                    ]
                )

        guidance.extend(
            [
                "### Requirements",
                "- Produce a comprehensive Markdown document tailored to the project idea.",
                "- Use clear headings, subheadings, bullet lists, and tables when appropriate.",
                "- Incorporate relevant details from the reference materials.",
                "- Provide actionable recommendations, plans, or specifications as appropriate.",
                "- Ensure the content is original; do not copy source text verbatim unless quoting.",
                "",
                READABILITY_GUIDELINES.strip(),
                "",
                "Begin the document now.",
            ]
        )

        return "\n".join(guidance)

    def generate(
        self,
        user_idea: str,
        dependency_documents: Dict[str, Dict[str, str]],
    ) -> str:
        prompt = self._build_prompt(user_idea, dependency_documents)
        return self._call_llm(prompt, temperature=self.default_temperature)

    async def async_generate(
        self,
        user_idea: str,
        dependency_documents: Dict[str, Dict[str, str]],
    ) -> str:
        prompt = self._build_prompt(user_idea, dependency_documents)
        return await self._async_call_llm(prompt, temperature=self.default_temperature)

    async def generate_and_save(
        self,
        user_idea: str,
        dependency_documents: Dict[str, Dict[str, str]],
        output_rel_path: str,
    ) -> Dict[str, str]:
        try:
            content = await self.async_generate(user_idea, dependency_documents)
        except Exception as exc:
            logger.error("Failed to generate document %s: %s", self.definition.id, exc, exc_info=True)
            raise

        file_path = self.file_manager.write_file(output_rel_path, content)
        return {
            "id": self.definition.id,
            "name": self.definition.name,
            "file_path": file_path,
            "content": content,
            "generated_at": datetime.now().isoformat(),
        }

