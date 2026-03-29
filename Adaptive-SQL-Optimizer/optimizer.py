import pickle
import re

# =============================================
# 🔮 LOAD MODEL
# =============================================
model = pickle.load(open('model/optimizer_model.pkl', 'rb'))


# =============================================
# 📊 FEATURE EXTRACTION
# =============================================
def extract_features(query):
    query_lower = query.lower()

    joins = query_lower.count("join")
    conditions = query_lower.count("where")
    subqueries = query_lower.count("select") - 1
    order_by = query_lower.count("order by")
    group_by = query_lower.count("group by")

    return [joins, conditions, subqueries, order_by, group_by]


# =============================================
# ⏱ PREDICT EXECUTION TIME
# =============================================
def predict_time(query):
    try:
        features = extract_features(query)
        prediction = model.predict([features])
        return round(float(prediction[0]), 4)
    except:
        return 0.0


# =============================================
# 🔧 SMART OPTIMIZATION SUGGESTIONS
# =============================================
def suggest_basic_optimization(query):
    query_lower = query.lower()
    suggestions = []

    if "select *" in query_lower:
        suggestions.append("Avoid SELECT *. Fetch only required columns.")

    if "where" not in query_lower and "select" in query_lower:
        suggestions.append("Use WHERE clause to limit rows.")

    if "join" in query_lower:
        suggestions.append("Ensure JOIN columns are indexed.")

    if "order by" in query_lower:
        suggestions.append("Use indexing on ORDER BY columns.")

    if "group by" in query_lower:
        suggestions.append("Avoid unnecessary GROUP BY operations.")

    if "like '%" in query_lower:
        suggestions.append("Avoid leading wildcard in LIKE for better performance.")

    return suggestions


# =============================================
# 📌 INDEX RECOMMENDATION (IMPROVED)
# =============================================
def recommend_index(query):
    query_lower = query.lower()
    recommendations = []

    # Extract WHERE columns
    where_columns = re.findall(r'where\s+([a-zA-Z0-9_]+)', query_lower)

    # Extract JOIN columns
    join_columns = re.findall(r'on\s+([a-zA-Z0-9_]+)', query_lower)

    for col in where_columns:
        recommendations.append(f"CREATE INDEX idx_{col} ON table_name({col});")

    for col in join_columns:
        recommendations.append(f"CREATE INDEX idx_{col} ON table_name({col});")

    if not recommendations:
        recommendations.append("Consider indexing frequently queried columns.")

    return list(set(recommendations))  # remove duplicates


# =============================================
# 🧠 QUERY REWRITE (SMART)
# =============================================
def rewrite_query(query):
    query_lower = query.lower()

    # Replace SELECT *
    if "select *" in query_lower:
        query = re.sub(r"select\s+\*", "SELECT id, name", query, flags=re.IGNORECASE)

    # Replace != with <>
    query = query.replace("!=", "<>")

    # Optimize LIKE
    query = query.replace("LIKE '%", "LIKE '")

    return query


# =============================================
# ⚡ AUTO SUGGESTIONS (FOR TEXT INPUT)
# =============================================
def get_sql_suggestions(query):
    keywords = [
        "SELECT", "FROM", "WHERE", "JOIN", "INNER JOIN",
        "LEFT JOIN", "RIGHT JOIN", "GROUP BY",
        "ORDER BY", "INSERT INTO", "UPDATE", "DELETE"
    ]

    query_upper = query.upper()

    suggestions = [k for k in keywords if k.startswith(query_upper)]

    return suggestions