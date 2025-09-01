# AlloyDB Survey MCP Server

A Model Context Protocol (MCP) server for fetching on-ground survey data from Google Cloud AlloyDB. This server provides a standardized interface for AI assistants and applications to query and analyze survey data stored in AlloyDB.

## Features

- **Secure Connection**: Uses Google Cloud AlloyDB Connector for secure, authenticated connections
- **Flexible Querying**: Support for filtering by survey ID, location, date range, and respondent type
- **Search Capabilities**: Full-text search across survey questions and responses
- **Statistics**: Get comprehensive statistics about your survey data
- **MCP Standard**: Fully compliant with the Model Context Protocol specification

## Installation

1. **Clone and setup the project:**
   ```bash
   cd /path/to/your/project
   pip install -r requirements.txt
   ```

2. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

## Configuration

1. **Copy the example configuration:**
   ```bash
   cp config.env.example .env
   ```

2. **Update the configuration with your AlloyDB details:**
   ```env
   ALLOYDB_PROJECT_ID=your-gcp-project-id
   ALLOYDB_REGION=us-central1
   ALLOYDB_CLUSTER_ID=your-cluster-id
   ALLOYDB_INSTANCE_ID=your-instance-id
   ALLOYDB_DATABASE=survey_db
   ALLOYDB_USER=postgres
   ALLOYDB_PASSWORD=your-password
   ```

3. **Set up authentication:**
   - For local development: `gcloud auth application-default login`
   - For production: Set `GOOGLE_APPLICATION_CREDENTIALS` to your service account key path

## Database Setup

1. **Create the survey table in your AlloyDB instance:**
   ```bash
   psql -h your-alloydb-ip -U postgres -d survey_db -f alloydb_survey_mcp/schema.sql
   ```

2. **Adjust the schema** in `alloydb_survey_mcp/schema.sql` to match your actual survey data structure.

## Usage

### Running the MCP Server

```bash
python -m alloydb_survey_mcp.server
```

### Available Tools

1. **fetch_survey_data**: Retrieve survey data with optional filters
   - `survey_id`: Specific survey ID
   - `location`: Filter by location (partial match)
   - `date_from/date_to`: Date range filter (YYYY-MM-DD)
   - `respondent_type`: Filter by respondent type
   - `limit`: Maximum records to return

2. **get_survey_summary**: Get comprehensive statistics about survey data

3. **search_surveys_by_question**: Search surveys containing specific text in questions or responses

### Available Resources

1. **alloydb://surveys/statistics**: Overall survey statistics
2. **alloydb://surveys/locations**: List of all survey locations
3. **alloydb://surveys/respondent-types**: List of all respondent types

## Integration with AI Clients

### Claude Desktop

Add this configuration to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "alloydb-survey": {
      "command": "python",
      "args": ["-m", "alloydb_survey_mcp.server"],
      "cwd": "/path/to/your/project",
      "env": {
        "ALLOYDB_PROJECT_ID": "your-project-id",
        "ALLOYDB_REGION": "us-central1",
        "ALLOYDB_CLUSTER_ID": "your-cluster-id",
        "ALLOYDB_INSTANCE_ID": "your-instance-id",
        "ALLOYDB_DATABASE": "survey_db",
        "ALLOYDB_USER": "postgres",
        "ALLOYDB_PASSWORD": "your-password"
      }
    }
  }
}
```

### Other MCP Clients

The server follows the standard MCP protocol and can be integrated with any MCP-compatible client.

## Example Queries

Once connected, you can ask natural language questions like:

- "Show me all surveys from New York in the last month"
- "Get survey statistics for urban residents"
- "Find surveys that mention public transportation"
- "What are the most common survey locations?"

## Development

### Project Structure

```
alloydb_survey_mcp/
├── __init__.py          # Package initialization
├── server.py            # Main MCP server implementation
├── database.py          # AlloyDB connection and query utilities
├── config.py            # Configuration management
└── schema.sql           # Database schema and sample data
```

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting

```bash
black alloydb_survey_mcp/
isort alloydb_survey_mcp/
```

## Security Considerations

- Use IAM authentication in production environments
- Implement proper access controls at the database level
- Consider encrypting sensitive survey data
- Use connection pooling for better performance
- Regularly rotate database credentials

## Troubleshooting

### Common Issues

1. **Connection Failed**: Verify your AlloyDB instance is running and accessible
2. **Authentication Error**: Check your GCP credentials and permissions
3. **Query Timeout**: Consider adding connection pooling or increasing timeout values
4. **Schema Mismatch**: Ensure your database schema matches the expected structure

### Logs

The server logs important events and errors. Check the console output for debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
