import streamlit as st
import pandas as pd
from db_connection import get_connection

st.set_page_config(page_title="QueryPilot AI", layout="wide")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "query" not in st.session_state:
    st.session_state.query = ""

# ---------------- TITLE ----------------
st.title("🚀 Intelligent SQL Performance Optimizer")

menu = st.sidebar.radio("Navigation", ["SQL Editor", "History", "Profile"])
auth = st.sidebar.radio("Account", ["Guest", "Login", "Signup"])

conn = get_connection()
if not conn:
    st.stop()

cursor = conn.cursor(dictionary=True)

# ---------------- USERS TABLE ----------------
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
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (%s, %s)",
                (email, password)
            )
            conn.commit()
            st.sidebar.success("Account created!")
        except:
            st.sidebar.error("User already exists")

# ---------------- LOGIN ----------------
elif auth == "Login":
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
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
    user_id = "guest"

# ---------------- 🔥 USER TABLE PREFIX ----------------
def modify_query(query, user_id):
    if user_id == "guest":
        return query

    words = query.split()
    keywords = ["from", "into", "update", "table"]

    for i, word in enumerate(words):
        if word.lower() in keywords and i + 1 < len(words):
            table_name = words[i + 1]
            if not table_name.startswith(f"user_{user_id}_"):
                words[i + 1] = f"user_{user_id}_{table_name}"

    return " ".join(words)

# ============================
# SQL EDITOR
# ============================
if menu == "SQL Editor":

    st.subheader("💻 SQL Editor")

    query = st.text_area("Enter SQL Query:", st.session_state.query)
    st.session_state.query = query

    # 🔥 IMPROVED AUTOCOMPLETE
    keywords = [
        "SELECT", "FROM", "WHERE", "JOIN", "GROUP BY",
        "ORDER BY", "INSERT INTO", "UPDATE", "DELETE",
        "CREATE TABLE"
    ]

    if query:
        words = query.split()
        last_word = words[-1].upper() if words else ""

        suggestions = [k for k in keywords if k.startswith(last_word)]

        if suggestions:
            st.write("💡 Suggestions:")
            cols = st.columns(len(suggestions))

            for i, s in enumerate(suggestions):
                with cols[i]:
                    if st.button(s, key=f"sugg_{i}"):
                        if len(words) > 1:
                            new_query = " ".join(words[:-1]) + " " + s
                        else:
                            new_query = s

                        st.session_state.query = new_query
                        st.rerun()

    # 🔥 RUN QUERY
    if st.button("Execute / Analyze"):

        try:
            final_query = modify_query(query, user_id)

            cursor.execute(final_query)

            if query.lower().startswith("select"):
                result = cursor.fetchall()
                df = pd.DataFrame(result)
                st.dataframe(df)
            else:
                conn.commit()
                st.success("Query executed")

            # 🔥 SAVE HISTORY
            if user_id != "guest":
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

                try:
                    final_q = modify_query(q, user_id)
                    cursor.execute(final_q)

                    if q.lower().startswith("select"):
                        result = cursor.fetchall()
                        df = pd.DataFrame(result)
                        st.dataframe(df)

                    st.success("Executed")

                except Exception as e:
                    st.error(e)

# ============================
# HISTORY
# ============================
elif menu == "History":

    st.subheader("📊 Query History")

    if user_id == "guest":
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
        st.write("User ID:", user_id)
    else:
        st.write("Guest User")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()