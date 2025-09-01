"""Configuration management for the MCP server"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AlloyDBConfig(BaseModel):
    """Configuration for Alloy DB connection"""
    
    project_id: str = Field(..., description="GCP Project ID")
    region: str = Field(..., description="Alloy DB region")
    cluster_id: str = Field(..., description="Alloy DB cluster ID")
    instance_id: str = Field(..., description="Alloy DB instance ID")
    database: str = Field(default="postgres", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: Optional[str] = Field(default=None, description="Database password")
    
    @classmethod
    def from_env(cls) -> "AlloyDBConfig":
        """Create configuration from environment variables"""
        return cls(
            project_id=os.getenv("ALLOYDB_PROJECT_ID"),
            region=os.getenv("ALLOYDB_REGION"),
            cluster_id=os.getenv("ALLOYDB_CLUSTER_ID"),
            instance_id=os.getenv("ALLOYDB_INSTANCE_ID"),
            database=os.getenv("ALLOYDB_DATABASE", "postgres"),
            user=os.getenv("ALLOYDB_USER", "postgres"),
            password=os.getenv("ALLOYDB_PASSWORD"),
        )
    
    @property
    def instance_connection_name(self) -> str:
        """Get the full instance connection name"""
        return f"{self.project_id}:{self.region}:{self.cluster_id}:{self.instance_id}"


class MCPServerConfig(BaseModel):
    """Configuration for the MCP server"""
    
    name: str = Field(default="alloydb-survey-server", description="Server name")
    version: str = Field(default="1.0.0", description="Server version")
    log_level: str = Field(default="INFO", description="Logging level")
    
    @classmethod
    def from_env(cls) -> "MCPServerConfig":
        """Create configuration from environment variables"""
        return cls(
            name=os.getenv("MCP_SERVER_NAME", "alloydb-survey-server"),
            version=os.getenv("MCP_SERVER_VERSION", "1.0.0"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
