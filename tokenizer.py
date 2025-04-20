import pdfplumber

def process_pdf(filepath, report_type, notes):
    try:
        with pdfplumber.open(filepath) as pdf:
            text = '\n'.join(page.extract_text() or '' for page in pdf.pages)

        tokens = text.split()

        return {
            "filename": filepath,
            "report_type": report_type,
            "notes": notes,
            "tokens": tokens[:100],
            "message": "Processed successfully"
        }

    except Exception as e:
        return {
            "error": str(e)
        }
