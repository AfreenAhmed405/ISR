# generator.py
from llama_cpp import Llama
import os
from transformers import AutoTokenizer

model_path = "/Users/sudheerb/Downloads/mistral-7b-instruct-v0.1.Q4_0.gguf"
llm = Llama(model_path=model_path, n_ctx=256)

# Use a public tokenizer for estimating token lengths
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def generate_answer(question, context, log_file="model_logs.txt"):
    max_ctx_tokens = 256

    question_tokens = tokenizer.encode(question, add_special_tokens=False)
    context_tokens = tokenizer.encode(context, add_special_tokens=False)
    allowed_ctx_tokens = max_ctx_tokens - len(question_tokens) - 50

    if len(context_tokens) > allowed_ctx_tokens:
        print(f"⚠️ Truncating context from {len(context_tokens)} to {allowed_ctx_tokens} tokens.")
        context = tokenizer.decode(context_tokens[:allowed_ctx_tokens])

    prompt = f"""You are a medical assistant. Provide clear and accurate answers.

Context:
{context}

Question:
{question}

Answer:"""

    print("🟡 Prompt size (chars):", len(prompt))
    print("🟡 Generating response...")

    try:
        output = llm(prompt, max_tokens=150, temperature=0.7)
        response = output["choices"][0]["text"].strip()
        print("🟢 Model response received.")
    except Exception as e:
        print("🔴 Model failed:", e)
        response = "⚠️ Unable to generate response due to internal model error."

    with open(log_file, "a", encoding="utf-8") as f:
        f.write("=== New Interaction ===\n")
        f.write(f"Prompt:\n{prompt}\n")
        f.write(f"Model Output:\n{response}\n\n")

    return response