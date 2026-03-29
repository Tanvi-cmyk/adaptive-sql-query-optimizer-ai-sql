import mysql.connector
from mysql.connector import Error
import streamlit as st


def get_connection():
    try:
        # Use Streamlit secrets for credentials
        connection = mysql.connector.connect(
            host=st.secrets.get("mysql", {}).get("host", "localhost"),
            user=st.secrets.get("mysql", {}).get("user", "root"),
            password=st.secrets.get("mysql", {}).get("password", ""),
            database=st.secrets.get("mysql", {}).get("database", "sql_optimizer_db"),
            port=st.secrets.get("mysql", {}).get("port", 3306),
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