import sqlite3

class ValidationError(Exception):
    """Raised when a request cannot be safely executed."""
    pass

class SQLiteAdapter:
    def __init__(self, db_path="database.sqlite"):
        self.db_path = db_path

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def list_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            return [row['name'] for row in cursor.fetchall()]

    def get_table_schema(self, table):
        tables = self.list_tables()
        if table not in tables:
            raise ValidationError(f"Table '{table}' does not exist.")
            
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table})")
            return [dict(row) for row in cursor.fetchall()]

    def get_columns(self, table):
        schema = self.get_table_schema(table)
        return [col['name'] for col in schema]

    def _validate_table_and_columns(self, table, columns=None):
        if table not in self.list_tables():
            raise ValidationError(f"Unknown table: {table}")
        
        valid_cols = self.get_columns(table)
        if columns:
            for col in columns:
                if col not in valid_cols:
                    raise ValidationError(f"Unknown column '{col}' in table '{table}'")
        return valid_cols

    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        valid_cols = self._validate_table_and_columns(table, columns)
        
        select_cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {select_cols} FROM {table}"
        params = []
        
        if filters:
            conditions = []
            for col, value in filters.items():
                if col not in valid_cols:
                    raise ValidationError(f"Unknown filter column '{col}'")
                if isinstance(value, dict):
                    for op, val in value.items():
                        if op not in ['=', '!=', '>', '<', '>=', '<=', 'LIKE']:
                            raise ValidationError(f"Unsupported operator '{op}'")
                        conditions.append(f"{col} {op} ?")
                        params.append(val)
                else:
                    conditions.append(f"{col} = ?")
                    params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
        if order_by:
            if order_by not in valid_cols:
                raise ValidationError(f"Unknown order_by column '{order_by}'")
            query += f" ORDER BY {order_by}"
            if descending:
                query += " DESC"
                
        query += f" LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def insert(self, table, values):
        valid_cols = self._validate_table_and_columns(table, list(values.keys()))
        if not values:
            raise ValidationError("Empty values for insert.")
            
        cols = ", ".join(values.keys())
        placeholders = ", ".join(["?"] * len(values))
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(values.values()))
            conn.commit()
            
            # Fetch the inserted row (assuming id is primary key, simplified)
            lastrowid = cursor.lastrowid
            
            try:
                # Try to fetch by id if it exists
                cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (lastrowid,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
            except Exception:
                pass
            return {"inserted_id": lastrowid, **values}

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        valid_metrics = ['count', 'avg', 'sum', 'min', 'max']
        if metric.lower() not in valid_metrics:
            raise ValidationError(f"Unsupported aggregate metric: {metric}")
            
        valid_cols = self._validate_table_and_columns(table, [column] if column and column != '*' else None)
        if group_by:
            self._validate_table_and_columns(table, [group_by])
            
        metric_expr = f"{metric.upper()}({column if column else '*'})"
        
        query = f"SELECT "
        if group_by:
            query += f"{group_by}, "
        query += f"{metric_expr} as value FROM {table}"
        
        params = []
        if filters:
            conditions = []
            for col, value in filters.items():
                if col not in valid_cols:
                    raise ValidationError(f"Unknown filter column '{col}'")
                conditions.append(f"{col} = ?")
                params.append(value)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
        if group_by:
            query += f" GROUP BY {group_by}"
            
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
