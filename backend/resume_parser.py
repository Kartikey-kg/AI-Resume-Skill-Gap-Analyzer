import docx2txt
from PyPDF2 import PdfReader

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    elif file_path.endswith(".docx"):
        return docx2txt.process(file_path)

    else:
        return ""
