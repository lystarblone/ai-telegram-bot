import PyPDF2
import io
import docx
from config import config

class TextProcessor:
    def extract_text(self, content: bytes, mime_type: str) -> str:
        """Извлечение текста из файла в зависимости от его MIME-типа."""
        try:
            if mime_type == "application/pdf":
                return self._extract_pdf(content)
            elif mime_type == "text/plain":
                return content.decode("utf-8", errors="ignore")
            elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return self._extract_docx(content)
            else:
                raise ValueError(f"Неподдерживаемый тип файла: {mime_type}")
        except Exception as e:
            raise ValueError(f"Ошибка обработки файла: {str(e)}")

    def _extract_pdf(self, content: bytes) -> str:
        """Извлечение текста из PDF."""
        pdf_file = io.BytesIO(content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()

    def _extract_docx(self, content: bytes) -> str:
        """Извлечение текста из DOCX."""
        doc_file = io.BytesIO(content)
        doc = docx.Document(doc_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()