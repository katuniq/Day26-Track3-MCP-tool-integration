import sqlite3
import os

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cohort TEXT NOT NULL,
    score REAL
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    credits INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
);
"""

SEED_SQL = """
INSERT INTO students (name, cohort, score) VALUES 
('Alice', 'A1', 95.5),
('Bob', 'A1', 88.0),
('Charlie', 'B2', 76.5);

INSERT INTO courses (title, credits) VALUES 
('Math 101', 3),
('History 201', 4);

INSERT INTO enrollments (student_id, course_id) VALUES 
(1, 1),
(2, 1),
(3, 2);
"""

def create_database(db_path="database.sqlite"):
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA_SQL)
    cursor.executescript(SEED_SQL)
    conn.commit()
    conn.close()
    return db_path

if __name__ == "__main__":
    db_path = create_database()
    print(f"Database initialized at {db_path}")
