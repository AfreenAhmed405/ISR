import pandas as pd
import numpy as np
import json
import fitz     
import httpx

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def extract_with_ollama(prompt, url = "http://localhost:11434/api/generate"): 
    
    data = {
        "model": "mistral",
        "prompt": prompt
    }

    response = httpx.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, timeout=300)
    response_lines = [line for line in response.text.strip().split('\n') if line]
    response_dicts = [json.loads(line) for line in response_lines]
    result = ''.join(response_dict.get('response', '') for response_dict in response_dicts)
    return result

def create_df(text, items, pdf_name):
    prompt = f"""
        Extract the **value (with units, if applicable)** and the **exact relevant text** for the specified items from the veterinary medical report. 
        Return the output in **JSON format** with no additional text or explanations.

        ### Instructions:
        2. **Items in `items_details`**: Extract both **value** and **exact text** for the item.
        3. **If an item is not found**: Return `"N/A"` for both `"results"` and `"details"`.

        ### Output Format (JSON):
        {{
            "item_name": {{
                "results": "value with units (if applicable)",
                "details": "exact relevant text (if applicable, or N/A)"
            }}
        }}

        ### Input Variables:
        - **items**: {items}
        - **text**: {text}
    """
        
    str_data = extract_with_ollama(prompt)
    data = json.loads(str_data)
    df = pd.DataFrame([(key, value["results"], value["details"]) for key, value in data.items()], 
                        columns=['items', 'results', 'details'])
    df["filename"] = pdf_name
    df = df[['filename', 'items', 'results', 'details']]
    return df



def process_pdf(filepath, report_type, notes):
    pdf_text = extract_text_from_pdf(filepath)