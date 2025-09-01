"""Setup script for AlloyDB Survey MCP Server"""

from setuptools import setup, find_packages

setup(
    name="alloydb-survey-mcp-server",
    version="1.0.0",
    description="MCP server for fetching on-ground survey data from Alloy DB",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "google-cloud-alloydb-connectors>=1.0.0",
        "psycopg2-binary>=2.9.0",
        "asyncpg>=0.29.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "alloydb-survey-server=alloydb_survey_mcp.server:main",
        ],
    },
)
