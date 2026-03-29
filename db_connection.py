import mysql.connector
from mysql.connector import Error
import streamlit as st


def get_connection():
    try:
        # ✅ Ensure secrets exist
        if "mysql" not in st.secrets:
            st.error("❌ MySQL secrets not configured")
            return None

        config = st.secrets["mysql"]

        # ✅ Connect to Railway MySQL
        connection = mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            port=int(config["port"]),
            autocommit=True,

            # 🔥 Railway SSL Fix
            ssl_disabled=False,

            # 🔥 Stability
            connection_timeout=10
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # =====================================
            # 👤 USERS TABLE
            # =====================================
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # =====================================
            # 📊 QUERY LOGS
            # =====================================
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query_text TEXT,
                predicted_time FLOAT,
                actual_time FLOAT,
                user_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # =====================================
            # ⚙ OPTIMIZATION RESULTS
            # =====================================
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                original_query TEXT,
                optimized_query TEXT,
                index_suggestions TEXT,
                issues_detected TEXT,
                user_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # =====================================
            # 🔍 SAFE COLUMN CHECK (Better than try/except)
            # =====================================
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'query_logs' 
                AND COLUMN_NAME = 'user_id'
            """)
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE query_logs ADD COLUMN user_id VARCHAR(255)")

            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'optimization_results' 
                AND COLUMN_NAME = 'user_id'
            """)
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE optimization_results ADD COLUMN user_id VARCHAR(255)")

            cursor.close()

        return connection

    except KeyError as e:
        st.error(f"❌ Missing key in secrets: {e}")
        return None

    except Error as e:
        st.error(f"❌ MySQL Error: {e}")
        return None

    except Exception as e:
        st.error(f"❌ Unexpected Error: {e}")
        return None