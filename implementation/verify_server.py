import json
import sys
import os

# Append current path to ensure we can import
sys.path.append(os.path.dirname(__file__))

from mcp_server import search, insert, aggregate, database_schema, table_schema
from init_db import create_database

def main():
    print("Initializing Database...")
    db_path = os.path.join(os.path.dirname(__file__), "database.sqlite")
    create_database(db_path)
    print("Database initialized.")

    print("\n1. Testing schema://database resource...")
    schema = json.loads(database_schema())
    print("Length of full schema tables:", len(schema.keys()))
    assert "students" in schema

    print("\n2. Testing schema://table/students resource...")
    students_schema = json.loads(table_schema("students"))
    print(f"Students schema columns: {[col['name'] for col in students_schema]}")
    assert any(col["name"] == "cohort" for col in students_schema)

    print("\n3. Testing search tool...")
    res = json.loads(search(table="students", filters={"cohort": "A1"}))
    print("Search results:", res)
    assert res["status"] == "success"
    assert len(res["data"]) == 2

    print("\n4. Testing insert tool...")
    res = json.loads(insert(table="students", values={"name": "Eve", "cohort": "A1", "score": 99.0}))
    print("Insert result:", res)
    assert res["status"] == "success"

    print("\n5. Testing aggregate tool...")
    res = json.loads(aggregate(table="students", metric="avg", column="score", group_by="cohort"))
    print("Aggregate result:", res)
    assert res["status"] == "success"

    print("\n6. Testing error handling (invalid table)...")
    res = json.loads(search(table="nonexistent"))
    print("Search error result:", res)
    assert res["status"] == "error"
    
    print("\n7. Testing error handling (invalid column)...")
    res = json.loads(search(table="students", filters={"invalid_column": 1}))
    print("Search error result:", res)
    assert res["status"] == "error"

    print("\nVerification completed successfully!")

if __name__ == "__main__":
    main()
