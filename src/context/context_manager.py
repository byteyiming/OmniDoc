"""
Context Manager
Manages shared context database for agent collaboration
"""
import sqlite3
import json
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
        """Save requirements document"""
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
        """Save agent output"""
        cursor = self.connection.cursor()
        output_id = f"{project_id}_{output.agent_type.value}"
        
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
            json.dumps(output.dependencies),
            output.generated_at.isoformat() if output.generated_at else None
        ))
        
        self.connection.commit()
    
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
        """Save cross-reference"""
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
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

