# Importing necessary libraries
import json
import fitz 
import re  
import os 
from pathlib import Path
from dotenv import load_dotenv 
import google.generativeai as genai
# from Bio import Entrez
# from rank_bm25 import BM25Okapi
# from sentence_transformers import SentenceTransformer

# GENERATE JSON VALUES
def process_pdf(filepath, report_type, notes):
    text = extract_text_from_pdf(filepath)
    tokens = extract_with_LLM(text)
    # generate_descriptions(tokens)

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
    
def extract_with_LLM(text):
    clean_text = "\n".join([line for line in text.splitlines() if line.strip()])

    prompt = f"""
      You are a medical report parser.

      The following text is a blood test report extracted from a PDF. The format is broken across multiple lines — each test's name, value, and unit may appear on separate lines.

      ---

      Your job:
      1. Extract all **test results** that include:
        - `"name"`: the test name (e.g., "Hemoglobin")
        - `"value"`: the actual test value with units, if available (e.g., "11.9 g/dL") and whether it is Optimal, Low or High.

      2. Ignore any metadata (e.g., "Patient Name", "Age", "Note", etc.)

      3. Return the output as a valid **JSON list**, like this:

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

      ---

      Text:
      {clean_text}
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

# # ---------- CONFIG ----------
# Entrez.email = "mail.afreenahmed@gmail.com"
# TOP_K = 5
# SCORE_THRESHOLD = 0.1

# # ---------- LOAD KNOWLEDGE BASE ----------
# with open("medical_kb_full.jsonl", "r", encoding="utf-8") as f:
#     kb_chunks = [json.loads(line)["chunk"] for line in f]

# # ---------- BM25 SETUP ----------
# tokenized_chunks = [chunk.lower().split() for chunk in kb_chunks]
# bm25_index = BM25Okapi(tokenized_chunks)

# def generate_descriptions(tokens):
#     for token in tokens:
#         name = token["name"]
#         context = retrieve_description(name)  # from BM25/FAISS                    
#         # summary = summarize_description_with_gemini(name, context)
#         token["description"] = context 


# # ---------- MAIN RETRIEVAL FUNCTION ----------
# def retrieve_description(test_name, top_k=TOP_K, score_threshold=SCORE_THRESHOLD):
#     query_words = test_name.lower().split()

#     # --- BM25 ---
#     bm25_scores = bm25_index.get_scores(query_words)
#     top_bm25_idx = np.argsort(bm25_scores)[-top_k:]
#     top_bm25_chunks = [kb_chunks[i] for i in top_bm25_idx if bm25_scores[i] > score_threshold]

#     # --- FAISS ---
#     query_vec = embedding_model.encode([test_name])[0]
#     _, top_faiss_idx = faiss_index.search(np.array([query_vec]), top_k)
#     faiss_chunks = [kb_chunks[i] for i in top_faiss_idx[0]]

#     # --- Combine & Deduplicate ---
#     combined = list(dict.fromkeys(top_bm25_chunks + faiss_chunks))

#     if not combined or all(len(chunk.strip()) < 30 for chunk in combined):
#         print(f"⚠️ No strong match for '{test_name}' → using PubMed.")
#         return retrieve_description_from_pubmed(test_name)

#     return combined


# from Bio import Entrez
# Entrez.email = "mail.afreenahmed.com"  # REQUIRED

# def retrieve_description_from_pubmed(query, max_results=3):
#     try:
#         handle = Entrez.esearch(db="pubmed", term=f"{query} blood test", retmax=max_results)
#         record = Entrez.read(handle)
#         ids = record["IdList"]
#         if not ids:
#             return []

#         fetch_handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="text")
#         raw_text = fetch_handle.read()

#         chunks = [chunk.strip() for chunk in raw_text.split("\n\n") if len(chunk.strip()) > 50]
#         return chunks[:max_results]

#     except Exception as e:
#         print(f"❌ PubMed fallback failed for '{query}': {e}")
#         return []
