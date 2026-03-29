import streamlit as st
import pandas as pd
import uuid
from db_connection import get_connection

st.set_page_config(page_title="QueryPilot AI", layout="wide")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "query" not in st.session_state:
    st.session_state.query = ""

# ---------------- TITLE ----------------
st.title("🚀 QueryPilot AI")

menu = st.sidebar.radio("Menu", ["SQL Editor", "History", "Profile"])
auth = st.sidebar.radio("Account", ["Guest", "Login", "Signup"])

conn = get_connection()
if not conn:
    st.stop()

cursor = conn.cursor(dictionary=True)

# ---------------- CREATE USERS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100),
    password VARCHAR(100)
)
""")

# ---------------- SIGNUP ----------------
if auth == "Signup":
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Register"):
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
            conn.commit()
            st.sidebar.success("Account created!")
        except:
            st.sidebar.error("User already exists")

# ---------------- LOGIN ----------------
elif auth == "Login":
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()

        if user:
            st.session_state.user = user
            st.sidebar.success("Logged in")
        else:
            st.sidebar.error("Invalid credentials")

# ---------------- USER ----------------
if st.session_state.user:
    user_id = st.session_state.user["id"]
else:
    user_id = None

# ============================
# SQL EDITOR
# ============================
if menu == "SQL Editor":

    st.subheader("💻 SQL Editor")

    query = st.text_area("Enter SQL Query:", st.session_state.query)
    st.session_state.query = query

    # 🔥 AUTOCOMPLETE
    keywords = ["SELECT", "FROM", "WHERE", "JOIN", "GROUP BY", "ORDER BY", "INSERT", "UPDATE", "DELETE"]

    if query:
        last_word = query.split()[-1].upper()
        suggestions = [k for k in keywords if k.startswith(last_word)]

        if suggestions:
            st.write("💡 Suggestions:")
            cols = st.columns(len(suggestions))
            for i, s in enumerate(suggestions):
                with cols[i]:
                    if st.button(s, key=f"sugg_{i}"):
                        new_query = " ".join(query.split()[:-1]) + " " + s if len(query.split()) > 1 else s
                        st.session_state.query = new_query
                        st.rerun()

    # 🔥 RUN QUERY
    if st.button("Execute"):

        try:
            cursor.execute(query)

            if query.lower().startswith("select"):
                result = cursor.fetchall()
                df = pd.DataFrame(result)
                st.dataframe(df)
            else:
                conn.commit()
                st.success("Query executed")

            # SAVE ONLY IF LOGGED IN
            if user_id:
                cursor.execute("""
                    INSERT INTO query_logs (query_text, predicted_time, user_id)
                    VALUES (%s, %s, %s)
                """, (query, 0.0, user_id))
                conn.commit()

        except Exception as e:
            st.error(e)

    # 🔥 FILE UPLOAD
    st.markdown("---")
    file = st.file_uploader("Upload .sql file", type=["sql"])

    if file:
        content = file.read().decode("utf-8")
        queries = content.split(";")

        st.subheader("📂 File Analysis")

        for q in queries:
            if q.strip():
                st.code(q)
                st.write("💡 Suggestion: Avoid SELECT *")

# ============================
# HISTORY
# ============================
elif menu == "History":

    st.subheader("📊 Query History")

    if not user_id:
        st.warning("Login to view history")
    else:
        cursor.execute("""
            SELECT query_text FROM query_logs
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))

        rows = cursor.fetchall()

        for row in rows:
            st.code(row["query_text"])

# ============================
# PROFILE
# ============================
elif menu == "Profile":

    st.subheader("👤 Profile")

    if st.session_state.user:
        st.write("Email:", st.session_state.user["email"])
    else:
        st.write("Guest User")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()