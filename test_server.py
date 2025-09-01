#!/usr/bin/env python3
"""
Test script for the AlloyDB Survey MCP Server
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alloydb_survey_mcp.database import AlloyDBConnection


async def test_database_connection():
    """Test the database connection and basic queries"""
    print("Testing AlloyDB connection...")
    
    try:
        # Initialize connection
        db = AlloyDBConnection()
        await db.initialize()
        print("✅ Database connection successful")
        
        # Test basic query
        try:
            stats = await db.get_survey_statistics()
            print(f"✅ Statistics query successful: {stats}")
        except Exception as e:
            print(f"❌ Statistics query failed: {e}")
        
        # Test locations query
        try:
            locations = await db.get_locations()
            print(f"✅ Locations query successful: Found {len(locations)} locations")
        except Exception as e:
            print(f"❌ Locations query failed: {e}")
        
        # Test survey data query
        try:
            surveys = await db.get_survey_data(limit=5)
            print(f"✅ Survey data query successful: Found {len(surveys)} surveys")
        except Exception as e:
            print(f"❌ Survey data query failed: {e}")
        
        # Close connection
        await db.close()
        print("✅ Connection closed successfully")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return True


async def test_mcp_server():
    """Test the MCP server functionality"""
    print("\nTesting MCP server functionality...")
    
    try:
        from alloydb_survey_mcp.server import app, db_connection
        
        # Initialize database connection
        global db_connection
        db_connection = AlloyDBConnection()
        await db_connection.initialize()
        
        # Test list_resources
        try:
            resources = await app.list_resources()
            print(f"✅ List resources successful: Found {len(resources.resources)} resources")
        except Exception as e:
            print(f"❌ List resources failed: {e}")
        
        # Test list_tools
        try:
            tools = await app.list_tools()
            print(f"✅ List tools successful: Found {len(tools.tools)} tools")
        except Exception as e:
            print(f"❌ List tools failed: {e}")
        
        # Clean up
        await db_connection.close()
        print("✅ MCP server tests completed")
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False
    
    return True


async def main():
    """Main test function"""
    print("=== AlloyDB Survey MCP Server Test ===\n")
    
    # Check environment variables
    required_vars = [
        "ALLOYDB_PROJECT_ID",
        "ALLOYDB_REGION", 
        "ALLOYDB_CLUSTER_ID",
        "ALLOYDB_INSTANCE_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or environment configuration")
        return
    
    print("✅ Environment variables configured")
    
    # Run tests
    db_test = await test_database_connection()
    mcp_test = await test_mcp_server()
    
    print(f"\n=== Test Results ===")
    print(f"Database Connection: {'✅ PASS' if db_test else '❌ FAIL'}")
    print(f"MCP Server: {'✅ PASS' if mcp_test else '❌ FAIL'}")
    
    if db_test and mcp_test:
        print("\n🎉 All tests passed! Your MCP server is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main())
