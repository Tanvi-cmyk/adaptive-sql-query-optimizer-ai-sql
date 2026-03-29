import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="QueryPilot AI", layout="wide")

# ---------------- CUSTOM CSS (PREMIUM UI) ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.stApp {
    background: linear-gradient(135deg, #0e1117, #1c1f26);
    color: white;
}
textarea {
    background-color: #1c1f26 !important;
    color: white !important;
}
div.stButton > button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "query" not in st.session_state:
    st.session_state.query = ""
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- DATABASE (DEMO) ----------------
conn = sqlite3.connect("demo.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER
)
""")

# sample data
cursor.execute("INSERT OR IGNORE INTO students VALUES (1,'Tanvi',20)")
cursor.execute("INSERT OR IGNORE INTO students VALUES (2,'Rahul',22)")
conn.commit()

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.title("🔐 QueryPilot AI Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email == "tanvibarve21@gmail.com" and password == "Tanvi@721":
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("✅ Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------------- MAIN APP ----------------
else:
    # -------- TOP NAVBAR --------
    col1, col2 = st.columns([8,2])
    with col1:
        st.markdown("## 🚀 QueryPilot AI")
    with col2:
        st.markdown(f"👤 {st.session_state.user_email}")

    # -------- SIDEBAR --------
    st.sidebar.title("⚙️ Menu")
    page = st.sidebar.radio("", ["SQL Editor", "History", "Profile", "Logout"])

    # -------- LOGOUT --------
    if page == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    # -------- PROFILE --------
    elif page == "Profile":
        st.title("👤 Profile")
        st.write("Email:", st.session_state.user_email)

    # -------- HISTORY --------
    elif page == "History":
        st.title("🕘 Query History")
        for q in st.session_state.history[::-1]:
            st.code(q, language="sql")

    # -------- SQL EDITOR --------
    elif page == "SQL Editor":
        st.title("💻 SQL Editor (AI Assisted)")

        # Input
        query = st.text_area("Write your SQL query:", st.session_state.query, height=150)
        st.session_state.query = query

        # -------- AUTOCOMPLETE --------
        sql_keywords = [
            "SELECT", "FROM", "WHERE", "JOIN",
            "GROUP BY", "ORDER BY", "INSERT INTO",
            "UPDATE", "DELETE", "CREATE TABLE"
        ]

        if query:
            last_word = query.split()[-1].upper()
            suggestions = [kw for kw in sql_keywords if kw.startswith(last_word)]

            if suggestions:
                st.markdown("### 💡 Suggestions")
                for s in suggestions:
                    if st.button(s):
                        st.session_state.query += " " + s
                        st.rerun()

        # -------- RUN QUERY --------
        if st.button("🚀 Run Query"):
            try:
                df = pd.read_sql_query(query, conn)

                st.success("✅ Query Executed Successfully")
                st.dataframe(df)

                # Save history
                st.session_state.history.append(query)

            except Exception as e:
                st.error(f"❌ Error: {e}")

        # -------- FILE UPLOAD --------
        st.markdown("---")
        file = st.file_uploader("Upload SQL file", type=["sql"])

        if file:
            content = file.read().decode("utf-8")
            st.session_state.query = content
            st.rerun()