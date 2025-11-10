"""
Workflow Coordinator
Orchestrates multi-agent documentation generation workflow
"""
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path
import uuid
import os
import re

from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, SharedContext
from src.utils.logger import get_logger
from src.config.settings import get_settings, get_environment

logger = get_logger(__name__)
from src.agents.requirements_analyst import RequirementsAnalyst
from src.agents.pm_documentation_agent import PMDocumentationAgent
from src.agents.technical_documentation_agent import TechnicalDocumentationAgent
from src.agents.api_documentation_agent import APIDocumentationAgent
from src.agents.developer_documentation_agent import DeveloperDocumentationAgent
from src.agents.stakeholder_communication_agent import StakeholderCommunicationAgent
from src.agents.user_documentation_agent import UserDocumentationAgent
from src.agents.test_documentation_agent import TestDocumentationAgent
from src.agents.quality_reviewer_agent import QualityReviewerAgent
from src.agents.format_converter_agent import FormatConverterAgent
from src.agents.claude_cli_documentation_agent import ClaudeCLIDocumentationAgent
from src.agents.project_charter_agent import ProjectCharterAgent
from src.agents.user_stories_agent import UserStoriesAgent
from src.agents.database_schema_agent import DatabaseSchemaAgent
from src.agents.setup_guide_agent import SetupGuideAgent
from src.agents.marketing_plan_agent import MarketingPlanAgent
from src.agents.business_model_agent import BusinessModelAgent
from src.agents.support_playbook_agent import SupportPlaybookAgent
from src.agents.legal_compliance_agent import LegalComplianceAgent
from src.agents.document_improver_agent import DocumentImproverAgent
from src.utils.file_manager import FileManager
from src.utils.cross_referencer import CrossReferencer
from src.utils.parallel_executor import ParallelExecutor, TaskStatus
from src.rate_limit.queue_manager import RequestQueue
from src.utils.document_organizer import format_documents_by_level, get_documents_summary, get_document_level, get_document_display_name


class WorkflowCoordinator:
    """
    Coordinates the multi-agent documentation generation workflow
    
    Workflow:
    1. Requirements Analyst → Requirements Doc
    2. PM Agent → Project Management Docs
    3. (Future: Technical, API, Developer, Stakeholder agents)
    """
    
    def __init__(
        self,
        context_manager: Optional[ContextManager] = None,
        rate_limiter: Optional[RequestQueue] = None,
        provider_name: Optional[str] = None,
        provider_config: Optional[Dict[str, str]] = None
    ):
        """
        Initialize workflow coordinator
        
        Args:
            context_manager: Context manager instance
            rate_limiter: Shared rate limiter for all agents
            provider_name: Default provider name for all agents (uses env var if None)
                          Options: "ollama", "gemini", "openai"
            provider_config: Dict mapping agent attribute names to provider names
                           (overrides default provider_name for specific agents)
                           Example: {"requirements_analyst": "gemini", "technical_agent": "ollama"}
        """
        settings = get_settings()
        self.context_manager = context_manager or ContextManager()
        # Use rate limit from settings
        self.rate_limiter = rate_limiter or RequestQueue(
            max_rate=settings.rate_limit_per_minute, 
            period=60
        )
        self.file_manager = FileManager(base_dir=settings.docs_dir)
        logger.info(f"WorkflowCoordinator initialized (environment: {settings.environment.value})")
        
        # Determine default provider (from parameter or env var)
        default_provider = provider_name or os.getenv("LLM_PROVIDER")
        provider_config = provider_config or {}
        
        # Hybrid Mode: Key agents use Gemini for better quality, others use default (Ollama)
        # This ensures critical/complex documents get high quality while saving costs
        # Only apply hybrid mode if:
        # 1. No explicit provider_config is provided (user wants auto-config)
        # 2. Default provider is Ollama (or None, which defaults to Ollama via env)
        # 3. Gemini API key is available (can actually use Gemini)
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        should_enable_hybrid = (
            not provider_config and  # No explicit config
            (default_provider is None or default_provider.lower() == "ollama") and  # Using Ollama
            gemini_api_key and gemini_api_key != ""  # Gemini API key available
        )
        
        if should_enable_hybrid:
            # Key agents that require high quality (complex prompts, technical accuracy)
            # These agents handle the most complex documentation tasks
            hybrid_config = {
                "technical_agent": "gemini",           # Technical specs are complex
                "api_agent": "gemini",                 # API docs need precision
                "database_schema_agent": "gemini",     # Database design is critical
                "requirements_analyst": "gemini",      # Requirements are foundational
            }
            # Merge with user-provided config (user config takes precedence)
            provider_config = {**hybrid_config, **provider_config}
            logger.info("🔀 Hybrid mode enabled: Key agents (technical, API, database, requirements) use Gemini, others use Ollama")
            logger.info("   This balances quality (Gemini for complex docs) with cost (Ollama for others)")
        
        # Helper function to get provider for an agent
        def get_agent_provider(agent_key: str) -> Optional[str]:
            """Get provider for a specific agent"""
            return provider_config.get(agent_key, default_provider)
        
        # Initialize agents (shared rate limiter, with optional provider override)
        self.requirements_analyst = RequirementsAnalyst(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("requirements_analyst")
        )
        self.pm_agent = PMDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("pm_agent")
        )
        self.technical_agent = TechnicalDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("technical_agent")
        )
        self.api_agent = APIDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("api_agent")
        )
        self.developer_agent = DeveloperDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("developer_agent")
        )
        self.stakeholder_agent = StakeholderCommunicationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("stakeholder_agent")
        )
        self.user_agent = UserDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("user_agent")
        )
        self.test_agent = TestDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("test_agent")
        )
        self.quality_reviewer = QualityReviewerAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("quality_reviewer")
        )
        self.format_converter = FormatConverterAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("format_converter")
        )
        self.claude_cli_agent = ClaudeCLIDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("claude_cli_agent")
        )
        self.cross_referencer = CrossReferencer()
        
        # Level 1: Strategic (Entrepreneur) - New agents
        self.project_charter_agent = ProjectCharterAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("project_charter_agent")
        )
        
        # Level 2: Product (Product Manager) - New agents
        self.user_stories_agent = UserStoriesAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("user_stories_agent")
        )
        
        # Level 3: Technical (Programmer) - New agents
        self.database_schema_agent = DatabaseSchemaAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("database_schema_agent")
        )
        self.setup_guide_agent = SetupGuideAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("setup_guide_agent")
        )
        
        # Business & Marketing agents
        self.marketing_plan_agent = MarketingPlanAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("marketing_plan_agent")
        )
        self.business_model_agent = BusinessModelAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("business_model_agent")
        )
        self.support_playbook_agent = SupportPlaybookAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("support_playbook_agent")
        )
        self.legal_compliance_agent = LegalComplianceAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("legal_compliance_agent")
        )
        
        # Document improvement agent (for auto-fix loop)
        self.document_improver = DocumentImproverAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("document_improver")
        )
        
        # Log provider configuration
        if default_provider:
            logger.info(f"WorkflowCoordinator using default provider: {default_provider}")
        if provider_config:
            # Log which agents use which provider
            gemini_agents = [k for k, v in provider_config.items() if v and v.lower() == "gemini"]
            ollama_agents = [k for k, v in provider_config.items() if v and v.lower() == "ollama"]
            if gemini_agents:
                logger.info(f"Agents using Gemini: {', '.join(gemini_agents)}")
            if ollama_agents:
                logger.info(f"Agents using Ollama: {', '.join(ollama_agents)}")
            if len(provider_config) > len(gemini_agents) + len(ollama_agents):
                logger.info(f"WorkflowCoordinator using custom provider config: {provider_config}")
        
        logger.info("WorkflowCoordinator initialized with all agents (including business/marketing agents and auto-fix)")
    
    def _generate_technical_doc(self, req_summary, project_id):
        """Helper for parallel technical doc generation"""
        return self.technical_agent.generate_and_save(
            requirements_summary=req_summary,
            output_filename="technical_spec.md",
            project_id=project_id,
            context_manager=self.context_manager
        )
    
    def _generate_stakeholder_doc(self, req_summary, pm_path, project_id):
        """Helper for parallel stakeholder doc generation"""
        pm_summary = self._get_summary_from_file(pm_path)
        return self.stakeholder_agent.generate_and_save(
            requirements_summary=req_summary,
            pm_summary=pm_summary,
            output_filename="stakeholder_summary.md",
            project_id=project_id,
            context_manager=self.context_manager
        )
    
    def _generate_user_doc(self, req_summary, project_id):
        """Helper for parallel user doc generation"""
        return self.user_agent.generate_and_save(
            requirements_summary=req_summary,
            output_filename="user_guide.md",
            project_id=project_id,
            context_manager=self.context_manager
        )
    
    def generate_all_docs(self, user_idea: str, project_id: Optional[str] = None, profile: str = "team") -> Dict:
        """
        Generate all documentation types from a user idea
        
        Args:
            user_idea: User's project idea
            project_id: Optional project ID (generates one if not provided)
            profile: "team" or "individual" - determines which docs to generate
        
        Returns:
            Dict with generated file paths and status
        """
        # Generate project ID if not provided
        if not project_id:
            project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            logger.info(f"Generated new project_id: {project_id}")
        else:
            logger.info(f"Using provided project_id: {project_id}")
        
        logger.info(f"Starting multi-agent documentation generation workflow (project: {project_id}, idea length: {len(user_idea)} characters, profile: {profile})")
        logger.info(f"🚀 Starting Multi-Agent Documentation Generation - Project ID: {project_id}, Profile: {profile}, User Idea: {user_idea}")
        
        results = {
            "project_id": project_id,
            "user_idea": user_idea,
            "profile": profile,
            "files": {},
            "status": {}
        }
        
        try:
            # Step 1: Requirements Analyst
            doc_level = get_document_level("requirements")
            logger.info(f"Step 1: Starting Requirements Analyst ({doc_level.value})")
            req_path = self.requirements_analyst.generate_and_save(
                user_idea=user_idea,
                output_filename="requirements.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["requirements"] = req_path
            results["status"]["requirements"] = "complete"
            logger.info(f"Step 1 completed: Requirements saved to {req_path}")
            
            # Step 2: Get requirements from context
            logger.info("Step 2: Retrieving requirements from context")
            context = self.context_manager.get_shared_context(project_id)
            if not context.requirements:
                logger.error("Requirements not found in context after generation")
                raise ValueError("Requirements not found in context")
            logger.debug(f"Requirements retrieved from context: {len(context.requirements.core_features)} features")
            
            # Build requirements summary
            req_summary = {
                "user_idea": context.requirements.user_idea,
                "project_overview": context.requirements.project_overview,
                "core_features": context.requirements.core_features,
                "technical_requirements": context.requirements.technical_requirements
            }
            
            charter_summary = None  # Initialize for use in later steps
            
            # Step 3 & 4: Project Charter and PM Documentation (Team only)
            if profile == "team":
                # Step 3: Project Charter Agent (Level 1: Strategic)
                doc_level = get_document_level("project_charter")
                logger.info(f"Step 3 (Team): Starting Project Charter Agent ({doc_level.value})")
                charter_path = self.project_charter_agent.generate_and_save(
                    requirements_summary=req_summary,
                    output_filename="project_charter.md",
                    project_id=project_id,
                    context_manager=self.context_manager
                )
                results["files"]["project_charter"] = charter_path
                results["status"]["project_charter"] = "complete"
                logger.info(f"Step 3 (Team) completed: Project Charter saved to {charter_path}")
                
                # Step 4: PM Documentation Agent (Level 2 - uses Level 1 output)
                doc_level = get_document_level("pm_documentation")
                logger.info(f"Step 4 (Team): Starting PM Documentation Agent ({doc_level.value})")
                # Get Project Charter from context
                charter_output = self.context_manager.get_agent_output(project_id, AgentType.PROJECT_CHARTER)
                charter_summary = charter_output.content if charter_output else None
                if charter_summary:
                    logger.debug(f"Using Project Charter ({len(charter_summary)} chars) for PM documentation")
                pm_path = self.pm_agent.generate_and_save(
                    requirements_summary=req_summary,
                    project_charter_summary=charter_summary,
                    output_filename="project_plan.md",
                    project_id=project_id,
                    context_manager=self.context_manager
                )
                results["files"]["pm_documentation"] = pm_path
                results["status"]["pm_documentation"] = "complete"
                logger.info(f"Step 4 (Team) completed: PM documentation saved to {pm_path}")
            else:
                logger.info(f"Step 3 & 4 (Individual): Skipping Project Charter and PM Documentation")
                results["status"]["project_charter"] = "skipped"
                results["status"]["pm_documentation"] = "skipped"
            
            # Step 5: User Stories Agent (Level 2 - uses Level 1 output if available)
            doc_level = get_document_level("user_stories")
            logger.info(f"Step 5: Starting User Stories Agent ({doc_level.value})")
            # Get Project Charter from context (if team mode, already available; if individual, will be None)
            if charter_summary is None:
                charter_output = self.context_manager.get_agent_output(project_id, AgentType.PROJECT_CHARTER)
                charter_summary = charter_output.content if charter_output else None
            if charter_summary:
                logger.debug(f"Using Project Charter ({len(charter_summary)} chars) for User Stories")
            user_stories_path = self.user_stories_agent.generate_and_save(
                requirements_summary=req_summary,
                project_charter_summary=charter_summary,
                output_filename="user_stories.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["user_stories"] = user_stories_path
            results["status"]["user_stories"] = "complete"
            logger.info(f"Step 5 completed: User Stories saved to {user_stories_path}")
            
            # Step 6: Technical Documentation Agent (Level 3 - uses Level 1 + Level 2 outputs)
            doc_level = get_document_level("technical_documentation")
            logger.info(f"Step 6: Starting Technical Documentation Agent ({doc_level.value})")
            # Get Level 2 outputs
            user_stories_output = self.context_manager.get_agent_output(project_id, AgentType.USER_STORIES)
            user_stories_summary = user_stories_output.content if user_stories_output else None
            pm_summary_for_tech = None  # Default to None for individual profile
            if profile == "team":  # Only get PM summary in team mode
                pm_output_for_tech = self.context_manager.get_agent_output(project_id, AgentType.PM_DOCUMENTATION)
                pm_summary_for_tech = pm_output_for_tech.content if pm_output_for_tech else None
            if user_stories_summary:
                logger.debug(f"Using User Stories ({len(user_stories_summary)} chars) for Technical documentation")
            if pm_summary_for_tech:
                logger.debug(f"Using PM Plan ({len(pm_summary_for_tech)} chars) for Technical documentation")
            technical_path = self.technical_agent.generate_and_save(
                requirements_summary=req_summary,
                user_stories_summary=user_stories_summary,
                pm_summary=pm_summary_for_tech,
                output_filename="technical_spec.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["technical_documentation"] = technical_path
            results["status"]["technical_documentation"] = "complete"
            logger.info(f"Step 6 completed: Technical documentation saved to {technical_path}")
            
            # Step 7: Database Schema Agent (Level 3: Technical)
            doc_level = get_document_level("database_schema")
            logger.info(f"Step 7: Starting Database Schema Agent ({doc_level.value})")
            technical_output = self.context_manager.get_agent_output(project_id, AgentType.TECHNICAL_DOCUMENTATION)
            technical_summary = technical_output.content if technical_output else None
            database_path = self.database_schema_agent.generate_and_save(
                requirements_summary=req_summary,
                technical_summary=technical_summary,
                output_filename="database_schema.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["database_schema"] = database_path
            results["status"]["database_schema"] = "complete"
            logger.info(f"Step 7 completed: Database Schema saved to {database_path}")
            
            # Step 8: API Documentation Agent (uses technical_summary from Step 7)
            doc_level = get_document_level("api_documentation")
            logger.info(f"Step 8: Starting API Documentation Agent ({doc_level.value})")
            api_path = self.api_agent.generate_and_save(
                requirements_summary=req_summary,
                technical_summary=technical_summary,
                output_filename="api_documentation.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["api_documentation"] = api_path
            results["status"]["api_documentation"] = "complete"
            
            # Step 9: Get API documentation for setup guide and developer agents
            logger.info("Step 9: Retrieving API documentation")
            api_output = self.context_manager.get_agent_output(project_id, AgentType.API_DOCUMENTATION)
            api_summary = api_output.content if api_output else None
            
            # Step 10: Setup Guide Agent (Level 3: Technical)
            doc_level = get_document_level("setup_guide")
            logger.info(f"Step 10: Starting Setup Guide Agent ({doc_level.value})")
            setup_path = self.setup_guide_agent.generate_and_save(
                requirements_summary=req_summary,
                technical_summary=technical_summary,
                api_summary=api_summary,
                output_filename="setup_guide.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["setup_guide"] = setup_path
            results["status"]["setup_guide"] = "complete"
            logger.info(f"Step 10 completed: Setup Guide saved to {setup_path}")
            
            # Step 11: Developer Documentation Agent
            doc_level = get_document_level("developer_documentation")
            logger.info(f"Step 11: Starting Developer Documentation Agent ({doc_level.value})")
            developer_path = self.developer_agent.generate_and_save(
                requirements_summary=req_summary,
                technical_summary=technical_summary,
                api_summary=api_summary,
                output_filename="developer_guide.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["developer_documentation"] = developer_path
            results["status"]["developer_documentation"] = "complete"
            
            # Step 12 & 13: Stakeholder Communication Agent (Team only)
            if profile == "team":
                # Step 12: Get PM documentation for stakeholder agent
                logger.info("Step 12 (Team): Retrieving PM documentation for stakeholder agent")
                pm_output = self.context_manager.get_agent_output(project_id, AgentType.PM_DOCUMENTATION)
                pm_summary = pm_output.content if pm_output else None
                
                # Step 13: Stakeholder Communication Agent
                doc_level = get_document_level("stakeholder_communication")
                logger.info(f"Step 13 (Team): Starting Stakeholder Communication Agent ({doc_level.value})")
                stakeholder_path = self.stakeholder_agent.generate_and_save(
                    requirements_summary=req_summary,
                    pm_summary=pm_summary,
                    output_filename="stakeholder_summary.md",
                    project_id=project_id,
                    context_manager=self.context_manager
                )
                results["files"]["stakeholder_documentation"] = stakeholder_path
                results["status"]["stakeholder_documentation"] = "complete"
                logger.info(f"Step 13 (Team) completed: Stakeholder documentation saved to {stakeholder_path}")
            else:
                logger.info(f"Step 12 & 13 (Individual): Skipping Stakeholder Communication")
                results["status"]["stakeholder_documentation"] = "skipped"
            
            
            # Step 14: Test Documentation Agent
            doc_level = get_document_level("test_documentation")
            logger.info(f"Step 14: Starting Test Documentation Agent ({doc_level.value})")
            test_path = self.test_agent.generate_and_save(
                requirements_summary=req_summary,
                technical_summary=technical_summary,
                output_filename="test_plan.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["test_documentation"] = test_path
            results["status"]["test_documentation"] = "complete"
            
            # Step 15: User Documentation Agent (Cross-Level)
            doc_level = get_document_level("user_documentation")
            logger.info(f"Step 15: Starting User Documentation Agent ({doc_level.value})")
            user_doc_path = self.user_agent.generate_and_save(
                requirements_summary=req_summary,
                output_filename="user_guide.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["user_documentation"] = user_doc_path
            results["status"]["user_documentation"] = "complete"
            logger.info(f"Step 15 completed: User documentation saved to {user_doc_path}")
            
            # Step 16: Business Model Agent (uses Project Charter)
            if profile == "team":
                doc_level = get_document_level("business_model")
                logger.info(f"Step 16 (Team): Starting Business Model Agent ({doc_level.value})")
                business_model_path = self.business_model_agent.generate_and_save(
                    requirements_summary=req_summary,
                    project_charter_summary=charter_summary,
                    output_filename="business_model.md",
                    project_id=project_id,
                    context_manager=self.context_manager
                )
                results["files"]["business_model"] = business_model_path
                results["status"]["business_model"] = "complete"
                logger.info(f"Step 16 (Team) completed: Business Model saved to {business_model_path}")
            else:
                logger.info(f"Step 16 (Individual): Skipping Business Model")
                results["status"]["business_model"] = "skipped"
            
            # Step 17: Marketing Plan Agent (uses Business Model and Project Charter)
            if profile == "team":
                doc_level = get_document_level("marketing_plan")
                logger.info(f"Step 17 (Team): Starting Marketing Plan Agent ({doc_level.value})")
                business_model_output = self.context_manager.get_agent_output(project_id, AgentType.BUSINESS_MODEL)
                business_model_summary = business_model_output.content if business_model_output else None
                marketing_path = self.marketing_plan_agent.generate_and_save(
                    requirements_summary=req_summary,
                    project_charter_summary=charter_summary,
                    business_model_summary=business_model_summary,
                    output_filename="marketing_plan.md",
                    project_id=project_id,
                    context_manager=self.context_manager
                )
                results["files"]["marketing_plan"] = marketing_path
                results["status"]["marketing_plan"] = "complete"
                logger.info(f"Step 17 (Team) completed: Marketing Plan saved to {marketing_path}")
            else:
                logger.info(f"Step 17 (Individual): Skipping Marketing Plan")
                results["status"]["marketing_plan"] = "skipped"
            
            # Step 18: Support Playbook Agent (uses User Documentation)
            doc_level = get_document_level("support_playbook")
            logger.info(f"Step 18: Starting Support Playbook Agent ({doc_level.value})")
            user_doc_output = self.context_manager.get_agent_output(project_id, AgentType.USER_DOCUMENTATION)
            user_doc_summary = user_doc_output.content if user_doc_output else None
            support_path = self.support_playbook_agent.generate_and_save(
                requirements_summary=req_summary,
                user_documentation_summary=user_doc_summary,
                output_filename="support_playbook.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["support_playbook"] = support_path
            results["status"]["support_playbook"] = "complete"
            logger.info(f"Step 18 completed: Support Playbook saved to {support_path}")
            
            # Step 19: Legal & Compliance Agent (uses Technical Documentation)
            doc_level = get_document_level("legal_compliance")
            logger.info(f"Step 19: Starting Legal & Compliance Agent ({doc_level.value})")
            legal_path = self.legal_compliance_agent.generate_and_save(
                requirements_summary=req_summary,
                technical_summary=technical_summary,
                output_filename="legal_compliance.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["legal_compliance"] = legal_path
            results["status"]["legal_compliance"] = "complete"
            logger.info(f"Step 19 completed: Legal & Compliance saved to {legal_path}")
            
            # Step 20: Collect all documentation for cross-referencing and quality review
            all_documentation = {}
            document_agent_types = {}
            document_file_paths = {}
            
            # Map document types to agent types (include all new agents)
            doc_type_to_agent = {
                "requirements": AgentType.REQUIREMENTS_ANALYST,
                "project_charter": AgentType.PROJECT_CHARTER,
                "pm_documentation": AgentType.PM_DOCUMENTATION,
                "user_stories": AgentType.USER_STORIES,
                "technical_documentation": AgentType.TECHNICAL_DOCUMENTATION,
                "database_schema": AgentType.DATABASE_SCHEMA,
                "api_documentation": AgentType.API_DOCUMENTATION,
                "setup_guide": AgentType.SETUP_GUIDE,
                "developer_documentation": AgentType.DEVELOPER_DOCUMENTATION,
                "stakeholder_documentation": AgentType.STAKEHOLDER_COMMUNICATION,
                "user_documentation": AgentType.USER_DOCUMENTATION,
                "test_documentation": AgentType.TEST_DOCUMENTATION,
                "business_model": AgentType.BUSINESS_MODEL,
                "marketing_plan": AgentType.MARKETING_PLAN,
                "support_playbook": AgentType.SUPPORT_PLAYBOOK,
                "legal_compliance": AgentType.LEGAL_COMPLIANCE
            }
            
            for doc_type, file_path in results["files"].items():
                if file_path and doc_type != "quality_review" and doc_type != "format_conversions":
                    try:
                        from src.utils.file_manager import FileManager
                        file_manager = FileManager()
                        content = file_manager.read_file(file_path)
                        
                        # Map to agent type if available
                        agent_type = doc_type_to_agent.get(doc_type)
                        if agent_type:
                            all_documentation[agent_type] = content
                            document_agent_types[doc_type] = agent_type
                            document_file_paths[agent_type] = file_path
                    except Exception as e:
                        logger.warning(f"Could not read {doc_type}: {e}")
            
            logger.info(f"Collected {len(all_documentation)} documents for cross-referencing")
            
            # Step 13.5: Add cross-references to all documents
            try:
                referenced_docs = self.cross_referencer.create_cross_references(
                    all_documentation,
                    document_file_paths
                )
                
                # Save cross-referenced documents back to files (preserve original paths)
                updated_count = 0
                for agent_type, referenced_content in referenced_docs.items():
                    original_content = all_documentation.get(agent_type)
                    if referenced_content != original_content:
                        original_file_path = document_file_paths[agent_type]
                        # Write directly to original absolute path to preserve folder structure
                        if Path(original_file_path).is_absolute():
                            # Write directly to the absolute path
                            Path(original_file_path).write_text(referenced_content, encoding='utf-8')
                            logger.debug(f"Updated cross-referenced file at original path: {original_file_path}")
                        else:
                            # Relative path - write using file manager
                            self.file_manager.write_file(original_file_path, referenced_content)
                        # Update all_documentation for quality review
                        all_documentation[agent_type] = referenced_content
                        updated_count += 1
                
                logger.info(f"Added cross-references to {updated_count} documents")
                
                # Generate document index
                try:
                    index_content = self.cross_referencer.generate_document_index(
                        all_documentation,
                        document_file_paths,
                        project_name=req_summary.get('project_overview', 'Project')[:50]
                    )
                    
                    index_path = self.file_manager.write_file("index.md", index_content)
                    results["files"]["document_index"] = index_path
                    logger.info(f"Document index created: {index_path}")
                except Exception as e:
                    logger.warning(f"Could not generate index: {e}")
                    
            except Exception as e:
                logger.warning(f"Cross-referencing failed: {e}")
            
            # Step 17: Quality Reviewer Agent
            logger.info("Running Quality Review")
            quality_review_path = self.quality_reviewer.generate_and_save(
                all_documentation=all_documentation,
                output_filename="quality_review.md",
                project_id=project_id,
                context_manager=self.context_manager
            )
            results["files"]["quality_review"] = quality_review_path
            results["status"]["quality_review"] = "complete"
            
            # Step 17.25: Auto-Fix Loop (Self-Correction System)
            # Automatically improve documents with low quality scores based on quality review feedback
            # This allows local models (like mixtral) to iteratively improve their output
            try:
                from src.config.settings import get_settings
                settings = get_settings()
                
                # Enable auto-fix via environment variable or settings
                # Default: false (can be enabled with ENABLE_AUTO_FIX=true)
                enable_auto_fix = getattr(settings, 'enable_auto_fix', False) or os.getenv("ENABLE_AUTO_FIX", "false").lower() == "true"
                # Quality threshold for triggering auto-fix (default: 70)
                fix_threshold = float(os.getenv("AUTO_FIX_THRESHOLD", "70.0"))
                
                if enable_auto_fix:
                    logger.info("🔧 Auto-Fix Loop: Analyzing quality review and improving documents with low scores")
                    quality_review_content = self.file_manager.read_file(quality_review_path)
                    
                    # Extract overall quality score
                    overall_score_pattern = r'Overall Quality Score:\s*(\d+)/100'
                    overall_scores = re.findall(overall_score_pattern, quality_review_content)
                    overall_score = int(overall_scores[0]) if overall_scores else 100
                    
                    # Extract individual document scores
                    # Pattern: "## Document Name" followed by score or "Quality Score: X/100"
                    document_scores = {}
                    
                    # Map document names to AgentType
                    doc_name_to_agent_type = {
                        "Technical Specification": AgentType.TECHNICAL_DOCUMENTATION,
                        "Technical Documentation": AgentType.TECHNICAL_DOCUMENTATION,
                        "API Documentation": AgentType.API_DOCUMENTATION,
                        "Database Schema": AgentType.DATABASE_SCHEMA,
                        "Developer Documentation": AgentType.DEVELOPER_DOCUMENTATION,
                        "Test Documentation": AgentType.TEST_DOCUMENTATION,
                        "User Documentation": AgentType.USER_DOCUMENTATION,
                        "Requirements": AgentType.REQUIREMENTS_ANALYST,
                        "Project Charter": AgentType.PROJECT_CHARTER,
                        "User Stories": AgentType.USER_STORIES,
                        "PM Documentation": AgentType.PM_DOCUMENTATION,
                    }
                    
                    # Extract document-specific scores
                    # Look for patterns like "Quality Score: 45/100" or "Score: 45" within document sections
                    doc_section_pattern = r'##\s+([^\n]+)\s*\n(?:.*?\n)*?Quality Score:\s*(\d+)/100'
                    doc_matches = re.findall(doc_section_pattern, quality_review_content, re.MULTILINE | re.DOTALL)
                    
                    for doc_name, score_str in doc_matches:
                        doc_name = doc_name.strip()
                        score = int(score_str)
                        document_scores[doc_name] = score
                        logger.debug(f"Found document score: {doc_name} = {score}/100")
                    
                    # Also try alternative pattern: "Score: X" or "Overall Score: X"
                    alt_pattern = r'##\s+([^\n]+)\s*\n(?:.*?\n)*?(?:Score|Overall Score):\s*(\d+)'
                    alt_matches = re.findall(alt_pattern, quality_review_content, re.MULTILINE | re.DOTALL)
                    for doc_name, score_str in alt_matches:
                        doc_name = doc_name.strip()
                        if doc_name not in document_scores:
                            score = int(score_str)
                            # Assume it's out of 100 if not specified
                            if score < 100:
                                document_scores[doc_name] = score
                    
                    logger.info(f"📊 Quality Analysis: Overall score = {overall_score}/100, Found {len(document_scores)} document scores")
                    
                    # Determine which documents need improvement
                    documents_to_improve = []
                    
                    # If overall score is below threshold, improve all key documents
                    if overall_score < fix_threshold:
                        logger.info(f"⚠️  Overall quality score ({overall_score}/100) is below threshold ({fix_threshold}), triggering auto-fix")
                        
                        # Priority list: Most critical documents first
                        priority_docs = [
                            (AgentType.TECHNICAL_DOCUMENTATION, "technical_documentation", "Technical Specification", "Technical Documentation"),
                            (AgentType.API_DOCUMENTATION, "api_documentation", "API Documentation"),
                            (AgentType.DATABASE_SCHEMA, "database_schema", "Database Schema"),
                            (AgentType.DEVELOPER_DOCUMENTATION, "developer_documentation", "Developer Documentation"),
                            (AgentType.REQUIREMENTS_ANALYST, "requirements", "Requirements"),
                        ]
                        
                        for agent_type, doc_key, *doc_names in priority_docs:
                            if agent_type in all_documentation:
                                # Check if this document has a specific score
                                doc_score = None
                                for doc_name in doc_names:
                                    if doc_name in document_scores:
                                        doc_score = document_scores[doc_name]
                                        break
                                
                                # Include if: 1) has specific score < threshold, or 2) overall score < threshold
                                if (doc_score is not None and doc_score < fix_threshold) or (doc_score is None and overall_score < fix_threshold):
                                    documents_to_improve.append((agent_type, doc_key, doc_names[0], doc_score))
                                    logger.info(f"  📝 Will improve: {doc_names[0]} (score: {doc_score if doc_score else 'N/A'}/100)")
                    
                    # Improve documents
                    improved_count = 0
                    improved_docs = []
                    
                    for agent_type, doc_key, doc_name, doc_score in documents_to_improve:
                        if agent_type in all_documentation:
                            try:
                                original_doc = all_documentation[agent_type]
                                original_file_path = document_file_paths.get(agent_type)
                                
                                if original_file_path:
                                    logger.info(f"🔧 Auto-improving {doc_name}...")
                                    
                                    # Extract document-specific feedback from quality review
                                    # Try to find the section for this document
                                    doc_feedback = quality_review_content
                                    doc_section_pattern = rf'##\s+{re.escape(doc_name)}\s*\n(.*?)(?=##\s+|$)'
                                    doc_section_match = re.search(doc_section_pattern, quality_review_content, re.MULTILINE | re.DOTALL)
                                    if doc_section_match:
                                        doc_feedback = doc_section_match.group(1)
                                        logger.debug(f"Found specific feedback section for {doc_name}")
                                    
                                    improved_path = self.document_improver.improve_and_save(
                                        original_document=original_doc,
                                        document_type=doc_key,
                                        quality_feedback=doc_feedback if doc_section_match else quality_review_content,
                                        output_filename=Path(original_file_path).name,
                                        project_id=project_id,
                                        context_manager=self.context_manager,
                                        agent_type=agent_type
                                    )
                                    
                                    # Update all_documentation with improved version
                                    improved_content = self.file_manager.read_file(improved_path)
                                    all_documentation[agent_type] = improved_content
                                    document_file_paths[agent_type] = improved_path
                                    improved_count += 1
                                    improved_docs.append(doc_name)
                                    logger.info(f"✅ Improved {doc_name} (score: {doc_score if doc_score else 'N/A'}/100 → improved)")
                                else:
                                    logger.warning(f"⚠️  Could not find file path for {doc_name}")
                            except Exception as e:
                                logger.warning(f"⚠️  Could not improve {doc_name}: {e}", exc_info=True)
                    
                    if improved_count > 0:
                        logger.info(f"🎉 Auto-Fix Loop: Successfully improved {improved_count} document(s): {', '.join(improved_docs)}")
                        results["status"]["auto_fix"] = f"improved {improved_count} documents: {', '.join(improved_docs)}"
                        results["auto_fix_details"] = {
                            "improved_count": improved_count,
                            "improved_documents": improved_docs,
                            "overall_score": overall_score,
                            "threshold": fix_threshold
                        }
                    else:
                        logger.info("✅ Auto-Fix Loop: No documents needed improvement (all scores above threshold)")
                        results["status"]["auto_fix"] = "no improvement needed"
                else:
                    logger.debug(f"Auto-Fix Loop disabled (ENABLE_AUTO_FIX=false). Overall quality score: {overall_score if 'overall_score' in locals() else 'N/A'}/100")
            except Exception as e:
                logger.warning(f"⚠️  Auto-Fix Loop failed: {e}, continuing with workflow", exc_info=True)
                results["status"]["auto_fix"] = f"failed: {str(e)}"
            
            # Step 17.5: Generate Claude CLI Documentation
            logger.info("Generating Claude CLI Documentation")
            try:
                claude_md_path = self.claude_cli_agent.generate_and_save(
                    all_documentation=all_documentation,
                    project_id=project_id,
                    context_manager=self.context_manager
                )
                results["files"]["claude_cli_documentation"] = claude_md_path
                results["status"]["claude_cli_documentation"] = "complete"
            except Exception as e:
                logger.warning(f"Claude CLI documentation generation failed: {e}")
            
            # Step 18: Format Conversion (convert to HTML, PDF, DOCX)
            logger.info("Converting documentation to multiple formats")
            try:
                # Prepare documents dict with proper names for format converter
                # Use AgentType.value as key for proper folder mapping
                documents_for_conversion = {}
                for agent_type, content in all_documentation.items():
                    # Use the agent type value as the document name
                    # Format converter will map this to the correct folder via AGENT_TYPE_TO_FOLDER
                    documents_for_conversion[agent_type.value] = content
                
                logger.debug(f"Preparing to convert {len(documents_for_conversion)} documents: {list(documents_for_conversion.keys())}")
                
                # Convert to all supported formats
                format_results = self.format_converter.convert_all_documents(
                    documents=documents_for_conversion,
                    formats=["html", "pdf", "docx"],
                    project_id=project_id,
                    context_manager=self.context_manager
                )
                results["files"]["format_conversions"] = format_results
                results["status"]["format_conversions"] = "complete"
                
                total_conversions = sum(len(fmts) for fmts in format_results.values())
                logger.info(f"Converted {len(format_results)} documents to {total_conversions} files (HTML, PDF, DOCX)")
                
            except Exception as e:
                logger.warning(f"Format conversion partially failed: {e}, trying HTML-only conversion as fallback")
                try:
                    # Prepare documents dict again for fallback
                    documents_for_conversion = {agent_type.value: content for agent_type, content in all_documentation.items()}
                    format_results = self.format_converter.convert_all_documents(
                        documents=documents_for_conversion,
                        formats=["html"],
                        project_id=project_id,
                        context_manager=self.context_manager
                    )
                    results["files"]["format_conversions"] = format_results
                    results["status"]["format_conversions"] = "partial (HTML only)"
                    logger.info(f"Converted {len(format_results)} documents to HTML")
                except Exception as e2:
                    logger.warning(f"Format conversion failed: {e2}")
                    results["status"]["format_conversions"] = "skipped"
            
            # Summary - Organized by Level
            logger.info(f"Workflow completed successfully: {len(results['files'])} documents generated for project {project_id}")
            
            # Also log the organized structure
            summary = get_documents_summary(results["files"])
            logger.info(f"Documents organized by level: Level 1: {len(summary['level_1_strategic']['documents'])}, "
                       f"Level 2: {len(summary['level_2_product']['documents'])}, "
                       f"Level 3: {len(summary['level_3_technical']['documents'])}, "
                       f"Cross-Level: {len(summary['cross_level']['documents'])}")
            
            # Add organized summary to results
            results["documents_by_level"] = summary
            
            return results
            
        except Exception as e:
            logger.error(f"Error in workflow (profile: {profile}): {str(e)}", exc_info=True)
            results["error"] = str(e)
            return results
    
    def get_workflow_status(self, project_id: str) -> Dict:
        """Get current workflow status for a project"""
        context = self.context_manager.get_shared_context(project_id)
        
        return {
            "project_id": project_id,
            "workflow_status": {
                agent_type.value: status.value
                for agent_type, status in context.workflow_status.items()
            },
            "completed_agents": [
                agent_type.value
                for agent_type, status in context.workflow_status.items()
                if status == DocumentStatus.COMPLETE
            ],
            "total_outputs": len(context.agent_outputs)
        }

