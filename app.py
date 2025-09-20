# app.py
import os
from flask import Flask, render_template, request

app = Flask(__name__)

# -------------------------
# Config (toggle with env vars)
# -------------------------
USE_VERTEX = os.environ.get("USE_VERTEX", "true").lower() in ("1", "true", "yes")
SIMULATE_VERTEX = os.environ.get("SIMULATE_VERTEX", "true").lower() in ("1", "true", "yes")
PROJECT_ID = os.environ.get("PROJECT_ID", "your-project-id")
LOCATION = os.environ.get("LOCATION", "asia-south1")  # Mumbai region (optional)

# -------------------------
# Try to import Vertex SDK (optional)
VERTEX_AVAILABLE = False
try:
    import vertexai
    from vertexai.language_models import TextGenerationModel
    VERTEX_AVAILABLE = True
except Exception:
    VERTEX_AVAILABLE = False

# -------------------------
# Dummy functions (safe fallback)
# -------------------------
def extract_skills(profile_text):
    keywords = ["python", "java", "ai", "ml", "communication", "design", "data", "analysis", "sql"]
    skills = [word for word in keywords if word in profile_text.lower()]
    return skills if skills else ["Problem-solving", "Teamwork"]

def recommend_careers(skills):
    recommendations = []
    if "python" in skills or "ml" in skills or "ai" in skills:
        recommendations.append({
            "career": "Data Scientist",
            "skills_needed": ["Python", "Machine Learning", "Statistics"],
            "resources": [
                {"name": "Coursera: ML by Andrew Ng", "url": "https://www.coursera.org/learn/machine-learning"},
                {"name": "Kaggle Learn", "url": "https://www.kaggle.com/learn"},
                {"name": "DataCamp", "url": "https://www.datacamp.com/"}
            ]
        })
    if "java" in skills or "design" in skills:
        recommendations.append({
            "career": "Software Engineer",
            "skills_needed": ["Java", "System Design", "DSA"],
            "resources": [
                {"name": "GeeksforGeeks DSA", "url": "https://www.geeksforgeeks.org/data-structures/"},
                {"name": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer"},
                {"name": "LeetCode", "url": "https://leetcode.com/"}
            ]
        })
    if "communication" in skills:
        recommendations.append({
            "career": "Business Analyst",
            "skills_needed": ["Excel", "SQL", "Communication"],
            "resources": [
                {"name": "Excel Skills for Business", "url": "https://www.coursera.org/specializations/excel"},
                {"name": "Mode Analytics SQL", "url": "https://mode.com/sql-tutorial/"},
                {"name": "IIBA", "url": "https://www.iiba.org/"}
            ]
        })
    if not recommendations:
        recommendations.append({
            "career": "Generalist Career Path",
            "skills_needed": ["Critical Thinking", "Adaptability"],
            "resources": [
                {"name": "Soft Skills Book", "url": "https://www.goodreads.com/book/show/6552060-soft-skills"},
                {"name": "FutureLearn Career Planning", "url": "https://www.futurelearn.com/subjects/business-and-management-courses/career-development"},
                {"name": "LinkedIn Learning", "url": "https://www.linkedin.com/learning"}
            ]
        })
    return recommendations

# -------------------------
# Simulated Vertex response (formatted for readability)
# -------------------------
def simulate_vertex_response(profile_text):
    simulated = (
        "1) Data Scientist\n"
        "   - Why: Your profile shows interest/experience in Python and data projects.\n"
        "   - Skills: Python, Machine Learning, Data Visualization, Statistics, SQL\n"
        "   - Resources:\n"
        "       * Coursera: ML by Andrew Ng - https://www.coursera.org/learn/machine-learning\n"
        "       * Kaggle Learn - https://www.kaggle.com/learn\n\n"
        "2) Machine Learning Engineer\n"
        "   - Why: Strong hands-on experience with ML/AI projects and programming.\n"
        "   - Skills: Python, ML engineering, Model Deployment, TensorFlow/PyTorch, Cloud basics\n"
        "   - Resources:\n"
        "       * Fast.ai - https://www.fast.ai/\n"
        "       * TensorFlow tutorials - https://www.tensorflow.org/tutorials\n\n"
        "3) Data Analyst\n"
        "   - Why: Analytics & visualization are interest areas.\n"
        "   - Skills: SQL, Excel, Data Visualization (Tableau/PowerBI), Python/R, Communication\n"
        "   - Resources:\n"
        "       * Mode Analytics SQL tutorial - https://mode.com/sql-tutorial/\n"
        "       * Coursera: Excel Skills - https://www.coursera.org/specializations/excel\n"
    )
    return simulated

# -------------------------
# Vertex AI call (optional)
# -------------------------
def get_career_advice_vertex(profile_text):
    if SIMULATE_VERTEX:
        return simulate_vertex_response(profile_text)
    if not VERTEX_AVAILABLE:
        return None
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = TextGenerationModel.from_pretrained("text-bison@001")
        prompt = f"""
You are an expert career advisor for Indian students. Given the following profile:

{profile_text}

Provide 3 personalized career suggestions with:
- One-line rationale.
- Top 5 required skills.
- 2 short learning resources (Name - URL).
"""
        response = model.predict(prompt=prompt, temperature=0.2, max_output_tokens=600)
        return response.text
    except Exception as e:
        print("Vertex AI call failed; falling back. Error:", e)
        return None

# -------------------------
# Flask endpoints
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        profile_text = request.form["profile"]
        skills = extract_skills(profile_text)
        ai_text = None
        vertex_used_live = False
        vertex_simulated = False

        if USE_VERTEX:
            ai_text = get_career_advice_vertex(profile_text)
            if ai_text:
                vertex_simulated = SIMULATE_VERTEX
                vertex_used_live = (not SIMULATE_VERTEX) and VERTEX_AVAILABLE

        if ai_text:
            return render_template("index.html",
                                   skills=skills,
                                   careers=None,
                                   ai_text=ai_text,
                                   profile=profile_text,
                                   vertex_used_live=vertex_used_live,
                                   vertex_simulated=vertex_simulated)
        else:
            careers = recommend_careers(skills)
            return render_template("index.html",
                                   skills=skills,
                                   careers=careers,
                                   ai_text=None,
                                   profile=profile_text,
                                   vertex_used_live=False,
                                   vertex_simulated=False)

    # GET request defaults
    return render_template("index.html",
                           skills=None,
                           careers=None,
                           ai_text=None,
                           profile="",
                           vertex_used_live=False,
                           vertex_simulated=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

