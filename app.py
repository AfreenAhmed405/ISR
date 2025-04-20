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
        with open("extracted_testing.json", "r", encoding="utf-8") as f:
            result = json.load(f)
    except FileNotFoundError:
        result = {"tokens": [], "message": "No summary available."}

    return render_template("summary.html", summary=result)

if __name__ == '__main__':
    app.run(debug=True)