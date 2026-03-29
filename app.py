import streamlit as st
import sqlite3
import pandas as pd
import uuid

st.set_page_config(page_title="QueryPilot AI", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("app.db", check_same_thread=False)
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "history" not in st.session_state:
    st.session_state.history = []

if "query" not in st.session_state:
    st.session_state.query = ""

# ---------------- NAVBAR ----------------
st.title("🚀 QueryPilot AI")

menu = st.sidebar.radio(
    "Menu",
    ["SQL Editor", "History", "Profile"]
)

auth = st.sidebar.radio("Account", ["Guest", "Login", "Signup"])

# ---------------- SIGNUP ----------------
if auth == "Signup":
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Register"):
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            st.sidebar.success("Account created! Login now")
        except:
            st.sidebar.error("User already exists")

# ---------------- LOGIN ----------------
elif auth == "Login":
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()

        if user:
            st.session_state.user = user
            st.sidebar.success("Logged in")
        else:
            st.sidebar.error("Invalid credentials")

# ---------------- USER ID ----------------
if st.session_state.user:
    user_id = st.session_state.user[0]
else:
    if "guest_id" not in st.session_state:
        st.session_state.guest_id = str(uuid.uuid4())
    user_id = None  # guest → no save

# ============================
# SQL EDITOR
# ============================
if menu == "SQL Editor":

    st.subheader("💻 SQL Editor")

    query = st.text_area("Enter SQL Query:", st.session_state.query)
    st.session_state.query = query

    # 🔥 AUTOCOMPLETE
    keywords = [
        "SELECT", "FROM", "WHERE", "JOIN",
        "GROUP BY", "ORDER BY", "INSERT INTO",
        "UPDATE", "DELETE"
    ]

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
            df = pd.read_sql_query(query, conn)
            st.dataframe(df)
            st.success("Query executed")

            # SAVE ONLY IF LOGGED IN
            if user_id:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    user_id INTEGER
                )
                """)
                cursor.execute("INSERT INTO history (query, user_id) VALUES (?, ?)", (query, user_id))
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
                st.write("💡 Suggestion: Avoid SELECT * if used")

# ============================
# HISTORY
# ============================
elif menu == "History":

    st.subheader("📊 Query History")

    if not st.session_state.user:
        st.warning("Login to view history")
    else:
        cursor.execute("SELECT query FROM history WHERE user_id=?", (user_id,))
        data = cursor.fetchall()

        for row in data[::-1]:
            st.code(row[0])

# ============================
# PROFILE
# ============================
elif menu == "Profile":

    st.subheader("👤 Profile")

    if st.session_state.user:
        st.write("Email:", st.session_state.user[1])
    else:
        st.write("Guest User")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()