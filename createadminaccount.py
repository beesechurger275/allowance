import db
import hashlib
import sys

username = sys.argv[1]
password = sys.argv[2]

password = hashlib.sha256(bytes(password, "utf-8")).hexdigest()
database = db.db()
database.connect("data.sql")
query = f"""
INSERT INTO users(name, hash, administrator, birthdate) VALUES ('{username}', '{password}', 1, NULL);
"""
database.execute(query)