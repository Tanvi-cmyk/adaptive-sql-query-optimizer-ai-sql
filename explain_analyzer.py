from db_connection import get_connection
import pandas as pd

def get_explain_plan(query):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(f"EXPLAIN {query}")
    result = cursor.fetchall()

    df = pd.DataFrame(result)

    cursor.close()
    conn.close()

    return df


def analyze_plan(df):
    issues = []

    for _, row in df.iterrows():
        if row['type'] == 'ALL':
            issues.append("⚠ Full table scan detected.")
        if row['key'] is None:
            issues.append("⚠ No index is being used.")
        if row['rows'] > 1000:
            issues.append("⚠ High row scan count.")

    if not issues:
        issues.append("✅ Query execution plan looks optimized.")

    return issues