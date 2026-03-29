import streamlit as st
import sqlite3
import pandas as pd
import uuid

st.set_page_config(page_title="SQL Optimizer", layout="wide")

# ---------------- SIMPLE UI ----------------
st.title("🚀 Intelligent SQL Performance Optimizer")

# ---------------- SESSION ----------------
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

if "query" not in st.session_state:
    st.session_state.query = ""

user_id = st.session_state.user_id

# ---------------- DATABASE ----------------
conn = sqlite3.connect("demo.db", check_same_thread=False)

# ---------------- SIDEBAR ----------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["SQL Editor", "History", "Profile"]
)

# ============================
# SQL EDITOR (OLD STYLE)
# ============================
if menu == "SQL Editor":

    query = st.text_area("Enter SQL Query:", st.session_state.query)
    st.session_state.query = query

    # 🔥 SIMPLE AUTOCOMPLETE
    keywords = ["SELECT", "FROM", "WHERE", "JOIN", "GROUP BY", "ORDER BY", "INSERT", "UPDATE", "DELETE"]

    if query:
        last_word = query.split()[-1].upper()
        suggestions = [k for k in keywords if k.startswith(last_word)]

        if suggestions:
            st.write("💡 Suggestions:")
            for s in suggestions:
                if st.button(s):
                    new_query = " ".join(query.split()[:-1]) + " " + s if len(query.split()) > 1 else s
                    st.session_state.query = new_query
                    st.rerun()

    # 🔥 RUN QUERY
    if st.button("Execute / Analyze"):

        try:
            df = pd.read_sql_query(query, conn)

            st.success("✅ Query executed successfully")
            st.dataframe(df)

            st.session_state.history.append(query)

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # 🔥 FILE UPLOAD
    st.markdown("---")
    file = st.file_uploader("Upload SQL file", type=["sql"])

    if file:
        content = file.read().decode("utf-8")
        st.session_state.query = content
        st.rerun()


# ============================
# HISTORY
# ============================
elif menu == "History":

    st.title("📊 Query History")

    for q in st.session_state.history[::-1]:
        st.code(q, language="sql")


# ============================
# PROFILE (NEW FEATURE)
# ============================
elif menu == "Profile":

    st.title("👤 Profile")

    st.write("🆔 Your Session ID:")
    st.code(user_id)

    st.info("This ID is used to track your query history.")

    if st.button("🔄 Reset Session"):
        st.session_state.user_id = str(uuid.uuid4())
        st.success("New session created!")