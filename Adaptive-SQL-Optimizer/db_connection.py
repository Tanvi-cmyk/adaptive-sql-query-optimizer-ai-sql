import mysql.connector
from mysql.connector import Error


def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Tanvi@721",
            database="sql_optimizer",
            port=3306,
            autocommit=True
        )

        if connection.is_connected():
            print("✅ MySQL Connected Successfully")

            # Create required tables if not exist
            cursor = connection.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query_text TEXT,
                predicted_time FLOAT,
                actual_time FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                original_query TEXT,
                optimized_query TEXT,
                index_suggestions TEXT,
                issues_detected TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.close()

        return connection

    except Error as e:
        print("❌ Connection Error:", e)
        raise