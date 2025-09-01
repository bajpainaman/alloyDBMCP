"""MCP Server for Alloy DB Survey Data"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ListResourcesResult,
    ListToolsResult,
    CallToolResult,
    ReadResourceResult,
)
from pydantic import BaseModel
from dotenv import load_dotenv

from .database import AlloyDBConnection

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
app = Server("alloydb-survey-server")

# Global database connection
db_connection: Optional[AlloyDBConnection] = None


class SurveyQueryParams(BaseModel):
    """Parameters for survey data queries"""
    survey_id: Optional[int] = None
    location: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    respondent_type: Optional[str] = None
    limit: int = 100


@app.list_resources()
async def list_resources() -> ListResourcesResult:
    """List available resources"""
    return ListResourcesResult(
        resources=[
            Resource(
                uri="alloydb://surveys/statistics",
                name="Survey Statistics",
                description="Overall statistics about survey data",
                mimeType="application/json",
            ),
            Resource(
                uri="alloydb://surveys/locations",
                name="Survey Locations",
                description="List of all unique survey locations",
                mimeType="application/json",
            ),
            Resource(
                uri="alloydb://surveys/respondent-types",
                name="Respondent Types",
                description="List of all unique respondent types",
                mimeType="application/json",
            ),
        ]
    )


@app.read_resource()
async def read_resource(uri: str) -> ReadResourceResult:
    """Read a specific resource"""
    global db_connection
    
    if not db_connection:
        raise RuntimeError("Database connection not initialized")
    
    try:
        if uri == "alloydb://surveys/statistics":
            stats = await db_connection.get_survey_statistics()
            return ReadResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text=json.dumps(stats, indent=2, default=str)
                    )
                ]
            )
        
        elif uri == "alloydb://surveys/locations":
            locations = await db_connection.get_locations()
            return ReadResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text=json.dumps({"locations": locations}, indent=2)
                    )
                ]
            )
        
        elif uri == "alloydb://surveys/respondent-types":
            types = await db_connection.get_respondent_types()
            return ReadResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text=json.dumps({"respondent_types": types}, indent=2)
                    )
                ]
            )
        
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        return ReadResourceResult(
            contents=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        )


@app.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="fetch_survey_data",
                description="Fetch survey data from Alloy DB with optional filters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "survey_id": {
                            "type": "integer",
                            "description": "Specific survey ID to fetch"
                        },
                        "location": {
                            "type": "string",
                            "description": "Filter by location (partial match supported)"
                        },
                        "date_from": {
                            "type": "string",
                            "description": "Start date filter (YYYY-MM-DD format)"
                        },
                        "date_to": {
                            "type": "string",
                            "description": "End date filter (YYYY-MM-DD format)"
                        },
                        "respondent_type": {
                            "type": "string",
                            "description": "Filter by respondent type"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of records to return (default: 100)",
                            "default": 100
                        }
                    },
                    "additionalProperties": False
                }
            ),
            Tool(
                name="get_survey_summary",
                description="Get a summary of survey data including counts and statistics",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            Tool(
                name="search_surveys_by_question",
                description="Search surveys that contain specific questions or responses",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question_text": {
                            "type": "string",
                            "description": "Text to search for in survey questions"
                        },
                        "response_text": {
                            "type": "string",
                            "description": "Text to search for in survey responses"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of records to return (default: 50)",
                            "default": 50
                        }
                    },
                    "additionalProperties": False
                }
            )
        ]
    )


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls"""
    global db_connection
    
    if not db_connection:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Error: Database connection not initialized"
                )
            ]
        )
    
    try:
        if name == "fetch_survey_data":
            # Validate and extract parameters
            params = SurveyQueryParams(**arguments)
            
            # Fetch data from database
            surveys = await db_connection.get_survey_data(
                survey_id=params.survey_id,
                location=params.location,
                date_from=params.date_from,
                date_to=params.date_to,
                respondent_type=params.respondent_type,
                limit=params.limit
            )
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "count": len(surveys),
                            "surveys": surveys
                        }, indent=2, default=str)
                    )
                ]
            )
        
        elif name == "get_survey_summary":
            # Get statistics
            stats = await db_connection.get_survey_statistics()
            locations = await db_connection.get_locations()
            respondent_types = await db_connection.get_respondent_types()
            
            summary = {
                "statistics": stats,
                "available_locations": locations,
                "available_respondent_types": respondent_types
            }
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(summary, indent=2, default=str)
                    )
                ]
            )
        
        elif name == "search_surveys_by_question":
            question_text = arguments.get("question_text")
            response_text = arguments.get("response_text")
            limit = arguments.get("limit", 50)
            
            # Build search query
            search_conditions = []
            params = []
            param_count = 0
            
            if question_text:
                param_count += 1
                search_conditions.append(f"questions_responses::text ILIKE ${param_count}")
                params.append(f"%{question_text}%")
            
            if response_text:
                param_count += 1
                search_conditions.append(f"questions_responses::text ILIKE ${param_count}")
                params.append(f"%{response_text}%")
            
            if not search_conditions:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: At least one search parameter (question_text or response_text) is required"
                        )
                    ]
                )
            
            query = f"""
            SELECT 
                survey_id,
                respondent_id,
                survey_date,
                location,
                respondent_type,
                questions_responses,
                created_at
            FROM surveys
            WHERE {' AND '.join(search_conditions)}
            ORDER BY survey_date DESC
            LIMIT {limit}
            """
            
            results = await db_connection.execute_query(query, params)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "count": len(results),
                            "matching_surveys": results
                        }, indent=2, default=str)
                    )
                ]
            )
        
        else:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error: Unknown tool '{name}'"
                    )
                ]
            )
    
    except Exception as e:
        logger.error(f"Error executing tool '{name}': {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        )


async def main():
    """Main entry point for the MCP server"""
    global db_connection
    
    try:
        # Initialize database connection
        db_connection = AlloyDBConnection()
        await db_connection.initialize()
        
        logger.info("Starting Alloy DB Survey MCP Server")
        
        # Run the server
        async with stdio_server() as streams:
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )
    
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise
    
    finally:
        # Clean up database connection
        if db_connection:
            await db_connection.close()


if __name__ == "__main__":
    asyncio.run(main())
