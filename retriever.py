import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

# Load retrieval models and indexes once
embedder = SentenceTransformer("all-MiniLM-L6-v2")
faiss_index = faiss.read_index("models/faiss/faiss.index")
with open("models/faiss/texts.pkl", "rb") as f:
    texts = pickle.load(f)
with open("models/faiss/bm25.pkl", "rb") as f:
    tfidf, _ = pickle.load(f)

def retrieve_hybrid(query, top_k=5):
    query_vec = tfidf.transform([query])
    bm25_scores = (query_vec * tfidf.transform(texts).T).toarray().ravel()
    bm25_indices = bm25_scores.argsort()[::-1][:top_k]

    query_embedding = embedder.encode([query])
    _, faiss_indices = faiss_index.search(query_embedding, top_k)

    combined = [texts[i] for i in bm25_indices] + [texts[i] for i in faiss_indices[0]]
    seen = set()
    context_chunks = []
    for chunk in combined:
        chunk = chunk.strip()
        if chunk not in seen and len(chunk) > 30:
            context_chunks.append(chunk)
            seen.add(chunk)

    return context_chunks[:top_k]

def build_hybrid_index(test_data, index_dir="models/faiss"):
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    test_lines = [f"{k}: {v}" for k, v in test_data.items()]

    if os.path.exists("report_text.txt"):
        with open("report_text.txt", "r") as f:
            pdf_lines = f.read().split("\n")
    else:
        pdf_lines = []

    texts = test_lines + pdf_lines

    tfidf = TfidfVectorizer().fit(texts)
    tfidf_matrix = tfidf.transform(texts)
    with open(os.path.join(index_dir, "bm25.pkl"), "wb") as f:
        pickle.dump((tfidf, texts), f)

    embeddings = embedder.encode(texts)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, os.path.join(index_dir, "faiss.index"))
    with open(os.path.join(index_dir, "texts.pkl"), "wb") as f:
        pickle.dump(texts, f)

    print(f"\u2705 Hybrid index built with {len(texts)} chunks.")
