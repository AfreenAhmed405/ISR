# Importing necessary libraries
import json
import fitz 
import re  
import os 
import numpy as np
from pathlib import Path
from dotenv import load_dotenv 
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi

def process_pdf(filepath, report_type, notes):
    text = extract_text_from_pdf(filepath)

    print(report_type)
    tokens = extract_with_LLM(text, report_type)
    
    if report_type != 'discharge':
        tokens = generate_descriptions(tokens)
    
    print(tokens)

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

# GENERATE K-V FOR NAMES
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
    
def extract_with_LLM(text, report_type):
    clean_text = "\n".join([line for line in text.splitlines() if line.strip()])

    if report_type == 'discharge':
      prompt = f"""
      You are a medical report parser.

      The following text is a discharge summary extracted from a PDF.

      ---

      Your job:
      1. Extract key **clinical sections** from the discharge summary in this **JSON list format**:
      [
        {{
          "name": "Diagnosis",
          "value": "Your foot is broken"
        }},
        {{
          "name": "Advice on Discharge",
          "value": "Ice your foot for 10 minutes daily"
        }}
      ]

      2. **Do NOT include** any of the following:
        - Patient name
        - Dates (e.g., admission date, discharge date)
        - Medical record numbers (MRN)
        - Room numbers or contact details

      Your output should only contain relevant medical insights or instructions useful for understanding the report.

      ---

      Text:
      {text}
      """
    else:
      prompt = f"""
      You are a medical report parser.

      The following text is a medical test report extracted from a PDF. The format is broken across multiple lines — each test's name, value, and unit may appear on separate lines.

      ---

      Your job:
      1. **If test values are present**, extract all test results in this **JSON format**:
      [
        {{
          "name": "Hemoglobin",
          "value": "11.9 g/dL - Low"
        }},
        {{
          "name": "Platelet Count",
          "value": "1.5 lakhs/cumm - High"
        }}
      ]

      Make sure each "value" includes the numeric result, unit, and whether it is **Low**, **Normal**, or **High** based on standard reference ranges.

      ---

      Text:
      {text}
      """

    model = genai.GenerativeModel("models/gemini-1.5-flash")
    load_dotenv(dotenv_path=".env")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)

    try:
      response = model.generate_content(prompt)
      parsed = extract_json_from_text(response.text)
      return parsed
    except Exception as e:
        print("JSON parsing failed:", e)
        return []


# GENERATE DESCRIPTION FOR NAMES
def generate_descriptions(values):
    global bm25_index, faiss_index, embedding_model, kb_chunks 

    # Load knowledge base
    with open("./resources/medical_kb_full.jsonl", "r", encoding="utf-8") as f:
        kb_chunks = [json.loads(line)["chunk"] for line in f]

    tokenized_chunks = [chunk.lower().split() for chunk in kb_chunks]

    # BM25 Setup
    bm25_index = BM25Okapi(tokenized_chunks)

    # FAISS Setup
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = embedding_model.encode(kb_chunks, convert_to_numpy=True)

    dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)

    for token in values:
        name = token["name"]
        matches = retrieve_bm25_faiss(name)
        token["description"] = matches[0] if matches else "No description available."

    return values


def retrieve_bm25_faiss(test_name, top_k=5, score_threshold=0.1):
    query = test_name.lower().split()

    # BM25
    bm25_scores = bm25_index.get_scores(query)
    bm25_top_idxs = np.argsort(bm25_scores)[-top_k:]
    bm25_chunks_top = [kb_chunks[i] for i in bm25_top_idxs if bm25_scores[i] > score_threshold]

    # FAISS
    query_vec = embedding_model.encode([test_name])[0]
    _, faiss_top_idxs = faiss_index.search(np.array([query_vec]), top_k)
    faiss_chunks_top = [kb_chunks[i] for i in faiss_top_idxs[0]]

    # Combine
    combined = list(dict.fromkeys(bm25_chunks_top + faiss_chunks_top))

    if not combined:
        print(f"No match found for '{test_name}'")
    return combined