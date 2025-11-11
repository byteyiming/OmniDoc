"""
Context Manager
Manages shared context database for agent collaboration
"""
import sqlite3
import json
import threading
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from src.context.shared_context import (
    SharedContext,
    RequirementsDocument,
    AgentOutput,
    CrossReference,
    AgentType,
    DocumentStatus
)


class ContextManager:
    """Manages shared context in SQLite database"""
    
    def __init__(self, db_path: str = "context.db"):
        """
        Initialize context manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()  # Thread lock for database operations
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable column access by name
        
        cursor = self.connection.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                user_idea TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Requirements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requirements (
                project_id TEXT PRIMARY KEY,
                user_idea TEXT NOT NULL,
                project_overview TEXT,
                core_features TEXT,  -- JSON array
                technical_requirements TEXT,  -- JSON object
                user_personas TEXT,  -- JSON array
                business_objectives TEXT,  -- JSON array
                constraints TEXT,  -- JSON array
                assumptions TEXT,  -- JSON array
                generated_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)
        
        # Agent outputs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_outputs (
                output_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                document_type TEXT NOT NULL,
                content TEXT NOT NULL,
                file_path TEXT NOT NULL,
                quality_score REAL,
                status TEXT NOT NULL,
                dependencies TEXT,  -- JSON array
                generated_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)
        
        # Cross-references table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cross_references (
                ref_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                from_document TEXT NOT NULL,
                to_document TEXT NOT NULL,
                reference_type TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)
        
        # Project status table for workflow state management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_status (
                project_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                user_idea TEXT NOT NULL,
                profile TEXT,
                provider_name TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                failed_at TEXT,
                error TEXT,
                completed_agents TEXT,  -- JSON array
                results TEXT,  -- JSON object (serialized results)
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)
        
        self.connection.commit()
    
    def create_project(self, project_id: str, user_idea: str) -> str:
        """
        Create a new project context
        
        Args:
            project_id: Unique project identifier
            user_idea: Original user idea
            
        Returns:
            project_id
        """
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO projects (project_id, user_idea, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (project_id, user_idea, now, now))
        
        self.connection.commit()
        return project_id
    
    def save_requirements(self, project_id: str, requirements: RequirementsDocument):
        """Save requirements document (thread-safe)"""
        with self._lock:
            try:
                cursor = self.connection.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO requirements (
                        project_id, user_idea, project_overview, core_features,
                        technical_requirements, user_personas, business_objectives,
                        constraints, assumptions, generated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_id,
                    requirements.user_idea,
                    requirements.project_overview,
                    json.dumps(requirements.core_features),
                    json.dumps(requirements.technical_requirements),
                    json.dumps(requirements.user_personas),
                    json.dumps(requirements.business_objectives),
                    json.dumps(requirements.constraints),
                    json.dumps(requirements.assumptions),
                    requirements.generated_at.isoformat()
                ))
                
                self.connection.commit()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error saving requirements for {project_id}: {e}", exc_info=True)
                raise
    
    def get_requirements(self, project_id: str) -> Optional[RequirementsDocument]:
        """Get requirements for a project"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM requirements WHERE project_id = ?", (project_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return RequirementsDocument(
            user_idea=row["user_idea"],
            project_overview=row["project_overview"] or "",
            core_features=json.loads(row["core_features"] or "[]"),
            technical_requirements=json.loads(row["technical_requirements"] or "{}"),
            user_personas=json.loads(row["user_personas"] or "[]"),
            business_objectives=json.loads(row["business_objectives"] or "[]"),
            constraints=json.loads(row["constraints"] or "[]"),
            assumptions=json.loads(row["assumptions"] or "[]"),
            generated_at=datetime.fromisoformat(row["generated_at"])
        )
    
    def save_agent_output(self, project_id: str, output: AgentOutput):
        """
        Save agent output (thread-safe)
        
        Args:
            project_id: Project identifier
            output: AgentOutput to save
        """
        with self._lock:
            try:
                cursor = self.connection.cursor()
                output_id = f"{project_id}_{output.agent_type.value}"
                
                # Ensure dependencies is a list (handle None or other types)
                dependencies = output.dependencies
                if dependencies is None:
                    dependencies = []
                elif not isinstance(dependencies, list):
                    # Try to convert to list if possible
                    dependencies = list(dependencies) if hasattr(dependencies, '__iter__') else []
                
                # Ensure all values are properly formatted
                generated_at_str = None
                if output.generated_at:
                    if isinstance(output.generated_at, datetime):
                        generated_at_str = output.generated_at.isoformat()
                    elif isinstance(output.generated_at, str):
                        generated_at_str = output.generated_at
                
                cursor.execute("""
                    INSERT OR REPLACE INTO agent_outputs (
                        output_id, project_id, agent_type, document_type,
                        content, file_path, quality_score, status,
                        dependencies, generated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    output_id,
                    project_id,
                    output.agent_type.value,
                    output.document_type,
                    output.content,
                    output.file_path,
                    output.quality_score,
                    output.status.value,
                    json.dumps(dependencies),
                    generated_at_str
                ))
                
                self.connection.commit()
            except Exception as e:
                # Log error and re-raise
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error saving agent output for {project_id}/{output.agent_type.value}: {e}", exc_info=True)
                raise
    
    def get_agent_output(self, project_id: str, agent_type: AgentType) -> Optional[AgentOutput]:
        """Get agent output for a project"""
        cursor = self.connection.cursor()
        output_id = f"{project_id}_{agent_type.value}"
        
        cursor.execute("SELECT * FROM agent_outputs WHERE output_id = ?", (output_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return AgentOutput(
            agent_type=AgentType(row["agent_type"]),
            document_type=row["document_type"],
            content=row["content"],
            file_path=row["file_path"],
            quality_score=row["quality_score"],
            status=DocumentStatus(row["status"]),
            generated_at=datetime.fromisoformat(row["generated_at"]) if row["generated_at"] else None,
            dependencies=json.loads(row["dependencies"] or "[]")
        )
    
    def get_all_agent_outputs(self, project_id: str) -> Dict[AgentType, AgentOutput]:
        """Get all agent outputs for a project"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM agent_outputs 
            WHERE project_id = ? AND status = ?
        """, (project_id, DocumentStatus.COMPLETE.value))
        
        outputs = {}
        for row in cursor.fetchall():
            agent_type = AgentType(row["agent_type"])
            outputs[agent_type] = AgentOutput(
                agent_type=agent_type,
                document_type=row["document_type"],
                content=row["content"],
                file_path=row["file_path"],
                quality_score=row["quality_score"],
                status=DocumentStatus(row["status"]),
                generated_at=datetime.fromisoformat(row["generated_at"]) if row["generated_at"] else None,
                dependencies=json.loads(row["dependencies"] or "[]")
            )
        
        return outputs
    
    def save_cross_reference(self, project_id: str, ref: CrossReference):
        """Save cross-reference (thread-safe)"""
        with self._lock:
            try:
                cursor = self.connection.cursor()
                ref_id = f"{project_id}_{ref.from_document}_{ref.to_document}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO cross_references (
                        ref_id, project_id, from_document, to_document,
                        reference_type, description
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    ref_id,
                    project_id,
                    ref.from_document,
                    ref.to_document,
                    ref.reference_type,
                    ref.description
                ))
                
                self.connection.commit()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error saving cross-reference for {project_id}: {e}", exc_info=True)
                raise
    
    def get_shared_context(self, project_id: str) -> SharedContext:
        """Get complete shared context for a project"""
        cursor = self.connection.cursor()
        
        # Get project
        cursor.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
        project_row = cursor.fetchone()
        
        if not project_row:
            raise ValueError(f"Project {project_id} not found")
        
        # Get requirements
        requirements = self.get_requirements(project_id)
        
        # Get all agent outputs
        agent_outputs = self.get_all_agent_outputs(project_id)
        
        # Get workflow status
        cursor.execute("""
            SELECT agent_type, status FROM agent_outputs WHERE project_id = ?
        """, (project_id,))
        
        workflow_status = {
            AgentType(row["agent_type"]): DocumentStatus(row["status"])
            for row in cursor.fetchall()
        }
        
        # Get cross-references
        cursor.execute("SELECT * FROM cross_references WHERE project_id = ?", (project_id,))
        cross_references = [
            CrossReference(
                from_document=row["from_document"],
                to_document=row["to_document"],
                reference_type=row["reference_type"],
                description=row["description"]
            )
            for row in cursor.fetchall()
        ]
        
        return SharedContext(
            project_id=project_id,
            user_idea=project_row["user_idea"],
            requirements=requirements,
            agent_outputs=agent_outputs,
            cross_references=cross_references,
            workflow_status=workflow_status,
            created_at=datetime.fromisoformat(project_row["created_at"]),
            updated_at=datetime.fromisoformat(project_row["updated_at"])
        )
    
    def update_project_status(
        self,
        project_id: str,
        status: str,
        user_idea: Optional[str] = None,
        profile: Optional[str] = None,
        provider_name: Optional[str] = None,
        completed_agents: Optional[List[str]] = None,
        results: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """
        Update project workflow status in database (thread-safe)
        
        Args:
            project_id: Project identifier
            status: Workflow status ("in_progress", "complete", "failed")
            user_idea: User idea (required for initial status creation)
            profile: Project profile ("team" or "individual")
            provider_name: LLM provider name
            completed_agents: List of completed agent names
            results: Generation results dictionary
            error: Error message (if status is "failed")
        """
        with self._lock:
            try:
                cursor = self.connection.cursor()
                now = datetime.now().isoformat()
                
                # Check if status record exists
                cursor.execute("SELECT status, started_at FROM project_status WHERE project_id = ?", (project_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing status
                    update_fields = ["status = ?"]
                    update_values = [status]
                    
                    if completed_agents is not None:
                        update_fields.append("completed_agents = ?")
                        update_values.append(json.dumps(completed_agents) if completed_agents else "[]")
                    
                    if results is not None:
                        update_fields.append("results = ?")
                        update_values.append(json.dumps(results) if results else "{}")
                    
                    if error is not None:
                        update_fields.append("error = ?")
                        update_fields.append("failed_at = ?")
                        update_values.append(error)
                        update_values.append(now)
                    elif status == "complete":
                        update_fields.append("completed_at = ?")
                        update_values.append(now)
                    
                    update_values.append(project_id)
                    cursor.execute(f"""
                        UPDATE project_status 
                        SET {', '.join(update_fields)}
                        WHERE project_id = ?
                    """, update_values)
                    
                    # Also update projects table updated_at
                    cursor.execute("""
                        UPDATE projects 
                        SET updated_at = ?
                        WHERE project_id = ?
                    """, (now, project_id))
                else:
                    # Create new status record
                    if not user_idea:
                        raise ValueError("user_idea is required when creating new project status")
                    
                    cursor.execute("""
                        INSERT INTO project_status (
                            project_id, status, user_idea, profile, provider_name,
                            started_at, completed_agents, results, error
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        project_id,
                        status,
                        user_idea,
                        profile,
                        provider_name or "default",
                        now,
                        json.dumps(completed_agents or []),
                        json.dumps(results or {}),
                        error
                    ))
                
                self.connection.commit()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error updating project status for {project_id}: {e}", exc_info=True)
                raise
    
    def get_project_status(self, project_id: str) -> Optional[Dict]:
        """
        Get project workflow status from database
        
        Args:
            project_id: Project identifier
            
        Returns:
            Status dictionary or None if not found
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM project_status WHERE project_id = ?", (project_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            "project_id": row["project_id"],
            "status": row["status"],
            "user_idea": row["user_idea"],
            "profile": row["profile"],
            "provider_name": row["provider_name"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
            "failed_at": row["failed_at"],
            "error": row["error"],
            "completed_agents": json.loads(row["completed_agents"] or "[]"),
            "results": json.loads(row["results"] or "{}") if row["results"] else {}
        }
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

