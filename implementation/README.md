# SQLite FastMCP Server

## Setup Instructions

1. Create a Python virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install fastmcp pytest
   ```

3. Initialize the database (this creates `database.sqlite` with the seed data):
   ```bash
   python init_db.py
   ```

## Testing Steps

1. **Unit Testing:**
   Run the pytest test suite to ensure the underlying database operations work correctly:
   ```bash
   pytest tests/test_server.py
   ```

2. **Server Verification Script:**
   Run the built-in headless verification script to test tool outputs and error handling:
   ```bash
   python verify_server.py
   ```

## Client Configuration Example

For Gemini CLI or Antigravity, use the following `mcp_config.json` configuration. Be sure to replace `/ABSOLUTE/PATH/TO/...` with the actual path to the project directory.

```json
{
  "mcpServers": {
    "sqlite-lab": {
      "command": "/ABSOLUTE/PATH/TO/.venv/Scripts/python",
      "args": ["/ABSOLUTE/PATH/TO/implementation/mcp_server.py"],
      "cwd": "/ABSOLUTE/PATH/TO/implementation",
      "timeout": 10000
    }
  }
}
```

For Claude Code, you can add it to `.mcp.json` using absolute paths to the python executable and the `mcp_server.py` script.

## Tool Descriptions

- `search`: Search rows in a table with optional filters, ordering, limit, and offset. Returns JSON data.
- `insert`: Insert a new row into a table by providing a dictionary of column-value pairs.
- `aggregate`: Compute an aggregate metric (`count`, `avg`, `sum`, `min`, `max`) on a specific column with optional filters and grouping.

## Resources

- `schema://database`: Full database schema showing tables and their respective columns.
- `schema://table/{table_name}`: Specific table schema structure.

## Demo Flow

1. Connect the MCP client to the server using the configuration above.
2. Query: "Use the sqlite-lab MCP server to list all students in cohort A1." (Uses `search`)
3. Query: "Add a new student named Eve to cohort A1 with a score of 92.0." (Uses `insert`)
4. Query: "What is the average score by cohort?" (Uses `aggregate`)
5. View schema definitions when prompted by asking "What does the schema for the enrollments table look like?"
