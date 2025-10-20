"""
Initialize database for the application
"""
import sqlite3
import os
from pathlib import Path

# Get the backend directory
backend_dir = Path(__file__).parent

# Create database file path
db_file = backend_dir / "tictactoe.db"

# Ensure parent directory exists
db_file.parent.mkdir(parents=True, exist_ok=True)

# Create the database file if it doesn't exist
if not db_file.exists():
    conn = sqlite3.connect(str(db_file))
    conn.close()
    print(f"✓ Database file created: {db_file}")
else:
    print(f"✓ Database file already exists: {db_file}")

# Ensure logs directory exists
logs_dir = backend_dir / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)
print(f"✓ Logs directory ready: {logs_dir}")

print("\n✓ Database initialization complete!")
print(f"Database location: {db_file.absolute()}")
