import psycopg2
from psycopg2.extras import RealDictCursor
import random

class RandomNumberDB:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.db_config = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
            print("Database connection established.")
        except Exception as e:
            print(f"Failed to connect to database: {e}")

    def close(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def insert_random_number(self):
        """Insert a random number into the table."""
        try:
            cursor = self.connection.cursor()
            random_number = random.uniform(0, 100)  # Generate a random number
            query = "INSERT INTO random_num (random_number) VALUES (%s)"
            cursor.execute(query, (random_number,))
            self.connection.commit()
            cursor.close()
            print(f"Inserted random number: {random_number}")
        except Exception as e:
            print(f"Failed to insert random number: {e}")

    def get_last_entry(self):
        """Fetch the last entry from the table."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM random_num ORDER BY id DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Last Entry:", result)
                return result
            else:
                print("The table is empty.")
                return None
        except Exception as e:
            print(f"Failed to fetch the last entry: {e}")
            return None
        
db = RandomNumberDB(dbname='postgres', user='postgres', password='pigeon123!')
db.connect()
db.insert_random_number()
last_entry = db.get_last_entry()
print("Fetched Last Entry:", last_entry)
db.close()
