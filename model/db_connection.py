import mysql.connector
import streamlit as st

def get_connection():
    return mysql.connector.connect(
        host=st.secrets.get("mysql", {}).get("host", "localhost"),
        user=st.secrets.get("mysql", {}).get("user", "root"),
        password=st.secrets.get("mysql", {}).get("password", ""),
        database=st.secrets.get("mysql", {}).get("database", "sql_optimizer_db"),
        port=st.secrets.get("mysql", {}).get("port", 3306)
    )