import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class TestPostgres:
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', 5432)
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
        except Exception as e:
            print(f"Failed to connect to database: {e}")

    def close(self):
        if self.connection:
            self.connection.close()

    def test_session(self, subject_name):
        """Insert a new subject into the subjects table."""
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO subjects (subject_name) VALUES (%s) RETURNING subject_id"
            cursor.execute(query, (subject_name,))
            subject_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            print(f"Inserted new subject with ID {subject_id}.")
            return subject_id
        except Exception as e:
            print(f"Failed to insert subject: {e}")
            return None

    def test_round(self, subject_name):
        """Insert a new subject into the subjects table."""
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO subjects (subject_name) VALUES (%s) RETURNING subject_id"
            cursor.execute(query, (subject_name,))
            subject_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            print(f"Inserted new subject with ID {subject_id}.")
            return subject_id
        except Exception as e:
            print(f"Failed to insert subject: {e}")
            return None
