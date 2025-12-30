import asyncio
from langchain_community.document_loaders import PyPDFLoader
from openai import AsyncOpenAI
from app.services.embedding_service import embedding_service
from app.core.config import settings
import tempfile
import os
import PyPDF2

class CVProcessingService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            text = "".join([page.page_content for page in pages])
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def is_pdf_image_based(self, file_path: str) -> bool:
        """Check if PDF is image-based (no text)"""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text.strip():  # If any page has text
                        return False
            return True
        except Exception as e:
            print(f"Error checking PDF type: {e}")
            return True  # Assume image-based if error

    async def process_pdf_with_openai(self, file_path: str) -> str:
        """Process image-based PDF with OpenAI Vision API"""
        # Convert PDF to images and send to OpenAI
        # This is a simplified version - you might need more sophisticated PDF to image conversion
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        extracted_text = ""

        for page_num in range(min(5, len(doc))):  # Limit to first 5 pages
            page = doc[page_num]
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")

            # Upload image to OpenAI
            import base64
            img_base64 = base64.b64encode(img_data).decode('utf-8')

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text from this CV image. Include name, experience, skills, education, and contact information."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_completion_tokens=1000
            )
            extracted_text += response.choices[0].message.content + "\n\n"

        doc.close()
        return extracted_text

    async def process_cv_file(self, file_data: bytes, filename: str) -> tuple[str, list]:
        """Process CV file: extract text and generate embedding"""
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_data)
            temp_file_path = temp_file.name

        try:
            # Check if PDF is image-based
            is_image_based = self.is_pdf_image_based(temp_file_path)

            if is_image_based:
                # Process with OpenAI Vision API
                ocr_text = await self.process_pdf_with_openai(temp_file_path)
            else:
                # Extract text normally
                ocr_text = await self.extract_text_from_pdf(temp_file_path)

            # Generate embedding from the OCR text
            embedding = embedding_service.encode(ocr_text)

            return ocr_text, embedding

        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

cv_processing_service = CVProcessingService()