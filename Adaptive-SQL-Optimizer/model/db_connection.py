import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Tanvi@721",
        database="sql_optimizer_db"
    )