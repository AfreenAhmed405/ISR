# Importing necessary libraries
import json
import fitz 
import re  
import os 
from pathlib import Path
from dotenv import load_dotenv 
import google.generativeai as genai

def process_pdf(filepath, report_type, notes):
    text = extract_text_from_pdf(filepath)
    tokens = extract_with_gemini(text)
    generate_descriptions(tokens)

    return {
        "filename": Path(filepath).name,
        "report_type": report_type,
        "notes": notes,
        "tokens": tokens
    }

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text


def extract_json_from_text(text):
    try:
        match = re.search(r"\[\s*{.*?}\s*]", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            raise ValueError("No JSON array found")
    except Exception as e:
        print("JSON parsing failed:", e)
        return []
    

def extract_with_gemini(text):
    clean_text = "\n".join([line for line in text.splitlines() if line.strip()])

    prompt = f"""
      You are a medical report parser.

      The following text is a blood test report extracted from a PDF. The format is broken across multiple lines — each test's name, value, and unit may appear on separate lines.

      ---

      Your job:
      1. Extract all **test results** that include:
        - `"name"`: the test name (e.g., "Hemoglobin")
        - `"value"`: the actual test value with units, if available (e.g., "11.9 g/dL")

      2. Ignore any metadata (e.g., "Patient Name", "Age", "Note", etc.)

      3. Return the output as a valid **JSON list**, like this:

      [
        {{
          "name": "Hemoglobin",
          "value": "11.9 g/dL"
        }},
        {{
          "name": "Platelet Count",
          "value": "1.5 lakhs/cumm"
        }}
      ]

      ---

      Text:
      {clean_text}
    """

    model = genai.GenerativeModel("models/gemini-1.5-flash")
    load_dotenv(dotenv_path="keys.env")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)

    try:
      response = model.generate_content(prompt)
      parsed = extract_json_from_text(response.text)
      return parsed
    except Exception as e:
        print("JSON parsing failed:", e)
        return []

def generate_descriptions(tokens):
    for token in tokens:
        name = token["name"]
        context = retrieve_description(name)  # from BM25/FAISS                    
        summary = summarize_description_with_gemini(name, context)
        token["description"] = summary 