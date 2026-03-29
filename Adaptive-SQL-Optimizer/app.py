import streamlit as st
import uuid
import hashlib

from optimizer import (
    predict_time,
    suggest_basic_optimization,
    recommend_index,
    rewrite_query
)
from explain_analyzer import get_explain_plan, analyze_plan
from rl_agent import choose_action, update_q
from db_connection import get_connection


# =============================================
# 🔐 CONFIG
# =============================================
st.set_page_config(page_title="QueryPilot AI", page_icon="🚀", layout="wide")

st.title("🚀 QueryPilot AI")
st.caption("Optimize SQL queries using AI + Cloud Intelligence")


# =============================================
# 🔐 AUTH SYSTEM
# =============================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


auth_mode = st.sidebar.radio("Account", ["Login", "Signup", "Guest"])

user = st.session_state.get("user", None)

if auth_mode == "Signup":
    st.sidebar.subheader("Create Account")
    username = st.sidebar.text_input("Username")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Register"):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
        """, (username, email, hash_password(password)))

        conn.commit()
        st.sidebar.success("✅ Account created! Login now")


elif auth_mode == "Login":
    st.sidebar.subheader("Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM users 
            WHERE email=%s AND password=%s
        """, (email, hash_password(password)))

        user = cursor.fetchone()

        if user:
            st.session_state.user = user
            st.sidebar.success("✅ Logged in")
        else:
            st.sidebar.error("❌ Invalid credentials")


# =============================================
# USER IDENTIFICATION
# =============================================
if user:
    user_id = user["id"]
else:
    if "guest_id" not in st.session_state:
        st.session_state.guest_id = str(uuid.uuid4())
    user_id = st.session_state.guest_id


# ---------------------------------
# Navigation
# ---------------------------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["SQL Optimizer", "Query History Dashboard"]
)


# =============================================
# SQL OPTIMIZER
# =============================================
if menu == "SQL Optimizer":

    query = st.text_area("Enter SQL Query:")

    # 🔥 AUTO SUGGESTIONS
    keywords = ["SELECT", "FROM", "WHERE", "JOIN", "GROUP BY", "ORDER BY", "INSERT", "UPDATE", "DELETE"]
    suggestions = [k for k in keywords if query.upper() in k]

    if suggestions:
        st.write("💡 Suggestions:", suggestions)

    # 📂 FILE UPLOAD
    uploaded_file = st.file_uploader("Upload .sql file", type=["sql"])

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        st.code(content)

        queries = content.split(";")

        for q in queries:
            if q.strip():
                st.write("🔍 Analyzing:", q)
                st.write("⏱", predict_time(q))

    if st.button("Execute / Analyze"):

        if query:

            conn = get_connection()
            if not conn:
                st.stop()

            cursor = conn.cursor(dictionary=True)

            try:
                cursor.execute(query)

                if query.lower().startswith("select"):
                    st.dataframe(cursor.fetchall())
                else:
                    conn.commit()
                    st.success("✅ Query executed")

                # AI
                predicted_time = predict_time(query)
                st.write(f"⏱ Predicted Time: {predicted_time}")

                suggestions = suggest_basic_optimization(query)
                for s in suggestions:
                    st.write("-", s)

                rewritten = rewrite_query(query)
                st.code(rewritten, language="sql")

                # SAVE ONLY IF LOGGED IN
                if user:
                    cursor.execute("""
                        INSERT INTO query_logs (query_text, predicted_time, user_id)
                        VALUES (%s, %s, %s)
                    """, (query, predicted_time, user_id))

                    conn.commit()

            except Exception as e:
                st.error(e)

            finally:
                cursor.close()
                conn.close()


# =============================================
# DASHBOARD
# =============================================
elif menu == "Query History Dashboard":

    if not user:
        st.warning("⚠️ Login to view your history")
        st.stop()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM query_logs 
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))

    st.dataframe(cursor.fetchall())

    cursor.close()
    conn.close()