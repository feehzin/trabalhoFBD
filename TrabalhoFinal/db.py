import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        dbname="SistemaClinico",
        user="postgres",
        password="felipe123", 
        host="localhost"
    )

def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()