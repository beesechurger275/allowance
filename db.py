import sqlite3
from sqlite3 import Error

class db():
    def __init__(self):
        self.connection = None

    def connect(self, path):
        try:
            self.connection = sqlite3.connect(path)
        except Error as e:
            print(f"Database Connection Error: {e}")
            raise e

    def execute(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
        except Error as e:
            print("Database execute error")
            print(f"Query: {query}")
            raise e

    def read(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            #print("Database read error")
            #print(f"Query: {query}")
            raise e

    def readOne(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Error as e:
            #print("Database readOne Error")
            #print(f"Query: {query}")
            raise e
            

    def close(self):
        self.connection.close()
        return