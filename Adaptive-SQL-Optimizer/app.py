import streamlit as st
from optimizer import (
    predict_time,
    suggest_basic_optimization,
    recommend_index,
    rewrite_query
)
from explain_analyzer import get_explain_plan, analyze_plan
from rl_agent import choose_action, update_q
from db_connection import get_connection


# ---------------------------------
# Sidebar Navigation
# ---------------------------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["SQL Optimizer", "Query History Dashboard"]
)


# =============================================
# SQL OPTIMIZER SECTION
# =============================================
if menu == "SQL Optimizer":

    st.title("🚀 Intelligent SQL Performance Optimizer")

    query = st.text_area("Enter SQL Query:")

    if st.button("Execute / Analyze"):

        if query:

            conn = None
            cursor = None
            issues = []
            index_rec = []
            rewritten = ""

            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)

                # ---------------------------------
                # 🔍 Automatic Query Type Detection
                # ---------------------------------
                query_clean = query.strip().lower()

                if query_clean.startswith("select"):
                    query_type = "SELECT"
                elif query_clean.startswith("insert"):
                    query_type = "INSERT"
                elif query_clean.startswith("update"):
                    query_type = "UPDATE"
                elif query_clean.startswith("delete"):
                    query_type = "DELETE"
                elif query_clean.startswith("create"):
                    query_type = "CREATE"
                elif query_clean.startswith("alter"):
                    query_type = "ALTER"
                elif query_clean.startswith("drop"):
                    query_type = "DROP"
                else:
                    query_type = "OTHER"

                st.info(f"🔎 Detected Query Type: {query_type}")

                # ---------------------------------
                # 🚨 Prevent Dangerous Commands
                # ---------------------------------
                if "drop database" in query_clean:
                    st.error("❌ DROP DATABASE is not allowed for safety reasons.")
                    st.stop()

                # ---------------------------------
                # Execute Query
                # ---------------------------------
                cursor.execute(query)

                # SELECT
                if query_type == "SELECT":
                    result = cursor.fetchall()
                    st.subheader("📋 Query Result")
                    st.dataframe(result)

                    # EXPLAIN
                    explain_plan = get_explain_plan(query)
                    st.subheader("📊 MySQL EXPLAIN Plan")
                    st.dataframe(explain_plan)

                    issues = analyze_plan(explain_plan)
                    if issues:
                        st.subheader("⚠️ Issues Detected")
                        for issue in issues:
                            st.write("-", issue)

                # INSERT / UPDATE / DELETE
                elif query_type in ["INSERT", "UPDATE", "DELETE"]:
                    conn.commit()
                    st.success(f"✅ {cursor.rowcount} rows affected.")

                # CREATE / ALTER / DROP
                elif query_type in ["CREATE", "ALTER", "DROP"]:
                    conn.commit()
                    st.success("✅ Query executed successfully.")

                else:
                    conn.commit()
                    st.success("✅ Query executed.")

                # ---------------------------------
                # AI Prediction
                # ---------------------------------
                predicted_time = predict_time(query)
                st.write(f"⏱ Predicted Execution Time: {predicted_time} sec")

                # ---------------------------------
                # Basic Suggestions
                # ---------------------------------
                basic_suggestions = suggest_basic_optimization(query)
                if basic_suggestions:
                    st.subheader("🔧 Optimization Suggestions")
                    for s in basic_suggestions:
                        st.write("-", s)

                # ---------------------------------
                # Index Recommendation
                # ---------------------------------
                index_rec = recommend_index(query)
                if index_rec:
                    st.subheader("📌 Index Recommendations")
                    for rec in index_rec:
                        st.write("-", rec)

                # ---------------------------------
                # Query Rewrite
                # ---------------------------------
                rewritten = rewrite_query(query)
                st.subheader("🧠 Rewritten Optimized Query")
                st.code(rewritten, language='sql')

                # ---------------------------------
                # Reinforcement Learning Update
                # ---------------------------------
                state = str(query)
                action_index = choose_action(state)
                reward = 1
                update_q(state, action_index, reward)

                # ---------------------------------
                # Store Logs in Database
                # ---------------------------------
                cursor.execute("""
                    INSERT INTO query_logs (query_text, predicted_time)
                    VALUES (%s, %s)
                """, (query, predicted_time))

                cursor.execute("""
                    INSERT INTO optimization_results 
                    (original_query, optimized_query, index_suggestions, issues_detected)
                    VALUES (%s, %s, %s, %s)
                """, (
                    query,
                    rewritten,
                    str(index_rec),
                    str(issues)
                ))

                conn.commit()
                st.success("📦 Query & Optimization stored in database!")

            except Exception as e:
                st.error(f"❌ SQL Error: {e}")

            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()


# =============================================
# QUERY HISTORY DASHBOARD
# =============================================
elif menu == "Query History Dashboard":

    st.title("📊 Query History Dashboard")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM query_logs
            ORDER BY created_at DESC
        """)
        logs = cursor.fetchall()

        st.subheader("📝 Executed Queries")
        st.dataframe(logs)

        cursor.execute("""
            SELECT * FROM optimization_results
            ORDER BY created_at DESC
        """)
        results = cursor.fetchall()

        st.subheader("⚙ Optimization History")
        st.dataframe(results)

        cursor.close()
        conn.close()

    except Exception as e:
        st.error(f"Error loading dashboard: {e}")