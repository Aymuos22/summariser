import os
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = "your_secret_key_here"

CHAPTERS = {
    ("Mathematics", "Class 10"): [
        "Real Numbers",
        "Polynomials", 
        "Pair of Linear Equations in Two Variables",
        "Quadratic Equations",
        "Arithmetic Progressions",
        "Triangles",
        "Coordinate Geometry", 
        "Introduction to Trigonometry",
        "Some Applications of Trigonometry",
        "Circles",
        "Constructions",
        "Areas Related to Circles",
        "Surface Areas and Volumes",
        "Statistics",
        "Probability"
    ]
}
LANGUAGES = ["english", "hindi", "hinglish"]

def call_groq_llm(subject, chapter, language, class_name):
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY environment variable not set.")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        f"Create a detailed educational summary for the chapter \"{chapter}\" from {subject} "
        f"for {class_name} students in {language} language. Include key points, important formulas, "
        f"and explanations. Format with bullet points and clear sections."
    )
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        subject = request.form.get("subject")
        chapter = request.form.get("chapter") 
        language = request.form.get("language")
        class_name = "Class 10"
        try:
            summary = call_groq_llm(subject, chapter, language, class_name)
            session["summary"] = summary
            session["chapter"] = chapter
            return redirect(url_for("result"))
        except Exception as e:
            session["summary"] = f"Error generating summary: {str(e)}"
            session["chapter"] = chapter
            return redirect(url_for("result"))
    
    subjects = ["Mathematics"]
    chapters = CHAPTERS.get(("Mathematics", "Class 10"), [])
    languages = LANGUAGES
    return render_template("index.html", subjects=subjects, chapters=chapters, languages=languages)

@app.route("/result")
def result():
    summary = session.get("summary", "No summary available")
    chapter = session.get("chapter", "Unknown Chapter")
    return render_template("result.html", summary=summary, chapter=chapter)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/languages')
def languages():
    return jsonify({"languages": LANGUAGES})

@app.route('/chapters')
def chapters():
    subject = request.args.get('subject')
    class_name = request.args.get('class_name')
    chapters = CHAPTERS.get((subject, class_name), [])
    return jsonify({"chapters": chapters})

if __name__ == "__main__":
    app.run(debug=True)
