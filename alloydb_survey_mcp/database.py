"""Database connection and query utilities for Alloy DB"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import asyncpg
from google.cloud.alloydb.connector import Connector
import logging

logger = logging.getLogger(__name__)


class AlloyDBConnection:
    """Manages connection to Alloy DB and provides query methods"""
    
    def __init__(self):
        self.connector = None
        self.pool = None
        self.project_id = os.getenv("ALLOYDB_PROJECT_ID")
        self.region = os.getenv("ALLOYDB_REGION")
        self.cluster_id = os.getenv("ALLOYDB_CLUSTER_ID")
        self.instance_id = os.getenv("ALLOYDB_INSTANCE_ID")
        self.database = os.getenv("ALLOYDB_DATABASE", "postgres")
        self.user = os.getenv("ALLOYDB_USER", "postgres")
        self.password = os.getenv("ALLOYDB_PASSWORD")
        
        if not all([self.project_id, self.region, self.cluster_id, self.instance_id]):
            raise ValueError("Missing required Alloy DB configuration parameters")
    
    async def initialize(self):
        """Initialize the connection pool"""
        try:
            self.connector = Connector()
            
            # Create the instance connection name
            instance_connection_name = f"{self.project_id}:{self.region}:{self.cluster_id}:{self.instance_id}"
            
            # Create connection function
            async def getconn():
                conn = await self.connector.connect_async(
                    instance_connection_name,
                    "asyncpg",
                    user=self.user,
                    password=self.password,
                    db=self.database,
                )
                return conn
            
            # Store the connection function for later use
            self._getconn = getconn
            
            logger.info("Successfully initialized Alloy DB connection pool")
            
        except Exception as e:
            logger.error(f"Failed to initialize Alloy DB connection: {e}")
            raise
    
    async def close(self):
        """Close the connector"""
        if self.connector:
            await self.connector.close_async()
    
    async def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        if not hasattr(self, '_getconn'):
            raise RuntimeError("Database connection not initialized")
        
        conn = await self._getconn()
        try:
            if params:
                rows = await conn.fetch(query, *params)
            else:
                rows = await conn.fetch(query)
            
            # Convert rows to dictionaries
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            await conn.close()
    
    async def get_survey_data(
        self,
        survey_id: Optional[int] = None,
        location: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        respondent_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch survey data with optional filters"""
        
        # Base query - adjust table and column names based on your schema
        base_query = """
        SELECT 
            survey_id,
            respondent_id,
            survey_date,
            location,
            respondent_type,
            questions_responses,
            metadata,
            created_at,
            updated_at
        FROM surveys
        WHERE 1=1
        """
        
        params = []
        param_count = 0
        
        # Add filters based on provided parameters
        if survey_id:
            param_count += 1
            base_query += f" AND survey_id = ${param_count}"
            params.append(survey_id)
        
        if location:
            param_count += 1
            base_query += f" AND location ILIKE ${param_count}"
            params.append(f"%{location}%")
        
        if date_from:
            param_count += 1
            base_query += f" AND survey_date >= ${param_count}"
            params.append(date_from)
        
        if date_to:
            param_count += 1
            base_query += f" AND survey_date <= ${param_count}"
            params.append(date_to)
        
        if respondent_type:
            param_count += 1
            base_query += f" AND respondent_type = ${param_count}"
            params.append(respondent_type)
        
        # Add ordering and limit
        base_query += f" ORDER BY survey_date DESC LIMIT {limit}"
        
        return await self.execute_query(base_query, params)
    
    async def get_survey_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about survey data"""
        
        stats_query = """
        SELECT 
            COUNT(*) as total_surveys,
            COUNT(DISTINCT location) as unique_locations,
            COUNT(DISTINCT respondent_type) as respondent_types,
            MIN(survey_date) as earliest_survey,
            MAX(survey_date) as latest_survey,
            COUNT(DISTINCT DATE(survey_date)) as survey_days
        FROM surveys
        """
        
        result = await self.execute_query(stats_query)
        return result[0] if result else {}
    
    async def get_locations(self) -> List[str]:
        """Get all unique survey locations"""
        
        query = "SELECT DISTINCT location FROM surveys WHERE location IS NOT NULL ORDER BY location"
        result = await self.execute_query(query)
        return [row['location'] for row in result]
    
    async def get_respondent_types(self) -> List[str]:
        """Get all unique respondent types"""
        
        query = "SELECT DISTINCT respondent_type FROM surveys WHERE respondent_type IS NOT NULL ORDER BY respondent_type"
        result = await self.execute_query(query)
        return [row['respondent_type'] for row in result]
