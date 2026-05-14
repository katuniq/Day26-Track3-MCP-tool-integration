from fastmcp import FastMCP
import json
import os
from db import SQLiteAdapter, ValidationError

# Create the server object.
mcp = FastMCP("SQLite Lab MCP Server")

# Initialize database adapter
# Will default to database.sqlite in the same directory
db_path = os.path.join(os.path.dirname(__file__), "database.sqlite")
adapter = SQLiteAdapter(db_path)

@mcp.tool()
def search(table: str, filters: dict = None, columns: list[str] = None, limit: int = 20, offset: int = 0, order_by: str = None, descending: bool = False) -> str:
    """
    Search rows in a table with optional filters, ordering, limit and offset.
    filters should be a dictionary mapping column names to values or condition dictionaries.
    Example filters: {"cohort": "A1"} or {"score": {">": 90}}
    """
    try:
        results = adapter.search(table, columns=columns, filters=filters, limit=limit, offset=offset, order_by=order_by, descending=descending)
        return json.dumps({"status": "success", "data": results})
    except ValidationError as e:
        return json.dumps({"status": "error", "error": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "error": f"Internal error: {str(e)}"})

@mcp.tool()
def insert(table: str, values: dict) -> str:
    """
    Insert a new row into a table.
    values should be a dictionary mapping column names to values.
    """
    try:
        result = adapter.insert(table, values)
        return json.dumps({"status": "success", "data": result})
    except ValidationError as e:
        return json.dumps({"status": "error", "error": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "error": f"Internal error: {str(e)}"})

@mcp.tool()
def aggregate(table: str, metric: str, column: str = None, filters: dict = None, group_by: str = None) -> str:
    """
    Compute an aggregate metric on a table.
    Valid metrics: count, avg, sum, min, max.
    Example: aggregate(table="students", metric="avg", column="score", group_by="cohort")
    """
    try:
        results = adapter.aggregate(table, metric, column=column, filters=filters, group_by=group_by)
        return json.dumps({"status": "success", "data": results})
    except ValidationError as e:
        return json.dumps({"status": "error", "error": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "error": f"Internal error: {str(e)}"})


@mcp.resource("schema://database")
def database_schema() -> str:
    """Returns the full schema of the database."""
    tables = adapter.list_tables()
    schema = {}
    for table in tables:
        schema[table] = adapter.get_table_schema(table)
    return json.dumps(schema, indent=2)


@mcp.resource("schema://table/{table_name}")
def table_schema(table_name: str) -> str:
    """Returns the schema for a specific table."""
    try:
        schema = adapter.get_table_schema(table_name)
        return json.dumps(schema, indent=2)
    except ValidationError as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    mcp.run()
