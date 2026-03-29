import mysql.connector
from mysql.connector import Error
import streamlit as st


def get_connection():
    try:
        # ✅ Ensure secrets exist
        if "mysql" not in st.secrets:
            st.error("❌ MySQL secrets not found. Please configure secrets.toml")
            return None

        config = st.secrets["mysql"]

        # ✅ Debug (remove later)
        st.write("🔍 Connecting to:", config["host"], ":", config["port"])

        conn = mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            port=int(config["port"]),
            autocommit=True,
            ssl_disabled=True,
            connection_timeout=10
        )

        if conn.is_connected():
            st.success("✅ Connected to Railway MySQL")

            cursor = conn.cursor()

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

        return conn

    except KeyError as e:
        st.error(f"❌ Missing key in secrets: {e}")
        return None

    except Error as e:
        st.error(f"❌ MySQL Error: {e}")
        return None

    except Exception as e:
        st.error(f"❌ Unexpected Error: {e}")
        return None   # ✅ FIXED (you had typo here)