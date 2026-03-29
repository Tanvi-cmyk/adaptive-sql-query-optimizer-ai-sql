import pickle
import re

model = pickle.load(open('model/optimizer_model.pkl','rb'))

def extract_features(query):
    joins = query.lower().count("join")
    conditions = query.lower().count("where")
    subqueries = query.lower().count("select") - 1
    return [joins, conditions, subqueries]

def predict_time(query):
    features = extract_features(query)
    prediction = model.predict([features])
    return round(prediction[0],4)

# --------------------------
# Optimization Suggestions
# --------------------------

def suggest_basic_optimization(query):
    suggestions = []
    if "select *" in query.lower():
        suggestions.append("Avoid SELECT *; specify required columns.")
    if "where" not in query.lower():
        suggestions.append("Consider adding WHERE clause.")
    if "join" in query.lower():
        suggestions.append("Ensure JOIN columns are indexed.")
    return suggestions


# --------------------------
# Index Recommendation
# --------------------------

def recommend_index(query):
    recommendations = []

    where_columns = re.findall(r'where\s+([a-zA-Z0-9_]+)', query.lower())

    for col in where_columns:
        recommendations.append(f"CREATE INDEX idx_{col} ON table_name({col});")

    if "join" in query.lower():
        recommendations.append("Create index on JOIN columns.")

    return recommendations


# --------------------------
# Query Rewrite
# --------------------------

def rewrite_query(query):
    if "select *" in query.lower():
        query = query.lower().replace("select *", "select id, name")

    if "!=" in query:
        query = query.replace("!=", "<>")

    return query