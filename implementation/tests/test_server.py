import pytest
import os
import sys

# Ensure implementation is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import SQLiteAdapter, ValidationError
from init_db import create_database

@pytest.fixture(scope="module")
def adapter():
    db_path = os.path.join(os.path.dirname(__file__), "test_database.sqlite")
    create_database(db_path)
    yield SQLiteAdapter(db_path)
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

def test_list_tables(adapter):
    tables = adapter.list_tables()
    assert "students" in tables
    assert "courses" in tables

def test_search(adapter):
    results = adapter.search("students", limit=2)
    assert len(results) == 2
    assert results[0]["name"] == "Alice"

def test_search_invalid_table(adapter):
    with pytest.raises(ValidationError):
        adapter.search("nonexistent")

def test_insert(adapter):
    new_student = adapter.insert("students", {"name": "David", "cohort": "C1", "score": 85.0})
    assert new_student["name"] == "David"
    assert new_student["cohort"] == "C1"
    
    # Verify it's in the DB
    results = adapter.search("students", filters={"name": "David"})
    assert len(results) == 1

def test_aggregate(adapter):
    results = adapter.aggregate("students", metric="count", column="id")
    assert results[0]["value"] > 0
    
def test_aggregate_invalid_metric(adapter):
    with pytest.raises(ValidationError):
        adapter.aggregate("students", metric="invalid_metric", column="id")
