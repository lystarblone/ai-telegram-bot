import PyPDF2
import io

class TextProcessor:
    def extract_text(self, content, mime_type):
        if mime_type == "application/pdf":
            print(f"Обработка PDF, длина контента: {len(content)}")
            return self._extract_pdf(content)
        elif mime_type == "text/plain":
            print(f"Обработка TXT, длина контента: {len(content)}")
            return content.decode("utf-8")
        else:
            raise ValueError("Unsupported file type")

    def _extract_pdf(self, content):
        pdf_file = io.BytesIO(content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text