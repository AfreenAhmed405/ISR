from flask import Flask, request, redirect, render_template
import os
import json
from tokenizer import process_pdf

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('pdf-upload')
    report_type = request.form.get('report-type')
    notes = request.form.get('notes')

    if not file:
        return "No file uploaded", 400
    
    filepath = file.filename
    file.save(filepath)

    # Process with tokenizer.py
    result = process_pdf(filepath, report_type, notes)
    print(result)

    # Clean cache
    try:
        os.remove(filepath)
    except Exception as e:
        print(f"Error deleting file: {e}")

    with open("extracted.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return redirect("/summary")


@app.route('/summary')
def summary():
    try:
        with open("extracted.json", "r", encoding="utf-8") as f:
            result = json.load(f)
    except FileNotFoundError:
        result = {"tokens": [], "message": "No summary available."}

    return render_template("summary.html", summary=result, answer=None, question=None)


@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form.get("question")

    with open("extracted.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    # Hardcoded answer
    answer = (
        "Your Total RBC Count is 3.5 million/cumm, which is slightly below the normal range of 3.9 - 4.8. "
        "This may indicate mild anemia or reduced oxygen-carrying capacity of the blood. "
        "Common symptoms of low RBC count include fatigue, dizziness, or shortness of breath. "
    )

    return render_template("summary.html", summary=summary, answer=answer, question=question)

if __name__ == '__main__':
    app.run(debug=True)