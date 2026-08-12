import os
import logging
import mimetypes
from typing import List, Optional, Dict, Any, Union
import json
import csv

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles various file operations including reading multiple formats, chunking, and secure deletion."""

    def __init__(self, secure_mode: bool = True):
        self.secure_mode = secure_mode
        # Set max chunk size to 4000 characters
        self.max_chunk_size = 4000

    def read_file(self, filepath: str) -> str:
        """Read text from various file formats."""
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if ext in ['.txt', '.md', '.py', '.js', '.csv', '.json']:
                return self._read_text_file(filepath)
            elif ext == '.pdf':
                return self._read_pdf(filepath)
            elif ext == '.docx':
                return self._read_docx(filepath)
            elif ext in ['.png', '.jpg', '.jpeg']:
                logger.warning(f"Reading images not fully supported, returning path: {filepath}")
                return f"[Image File]: {filepath}"
            else:
                # Try reading as plain text as fallback
                return self._read_text_file(filepath)
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
            raise

    def _read_text_file(self, filepath: str) -> str:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _read_pdf(self, filepath: str) -> str:
        try:
            import PyPDF2
            text = ""
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            return text
        except ImportError:
            logger.error("PyPDF2 not installed. Cannot read PDF.")
            return "[PDF reading requires PyPDF2 package]"

    def _read_docx(self, filepath: str) -> str:
        try:
            import docx
            doc = docx.Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            logger.error("python-docx not installed. Cannot read DOCX.")
            return "[DOCX reading requires python-docx package]"

    def chunk_text(self, text: str) -> List[str]:
        """Split text into manageable chunks."""
        chunks = []
        for i in range(0, len(text), self.max_chunk_size):
            chunks.append(text[i:i + self.max_chunk_size])
        return chunks

    def list_files(self, directory: str, extension: Optional[str] = None) -> List[str]:
        """List files in a directory, optionally filtered by extension."""
        if not os.path.isdir(directory):
            logger.error(f"Directory not found: {directory}")
            return []
            
        files = []
        try:
            for item in os.listdir(directory):
                path = os.path.join(directory, item)
                if os.path.isfile(path):
                    if extension is None or item.endswith(extension):
                        files.append(path)
            return files
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return []

    def create_file(self, filepath: str, content: str) -> bool:
        """Create a file with given content."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"File created successfully: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error creating file {filepath}: {e}")
            return False

    def delete_file(self, filepath: str) -> bool:
        """Delete a file, strictly observing the security flag."""
        if not os.path.exists(filepath):
            logger.warning(f"File to delete not found: {filepath}")
            return False
            
        if self.secure_mode:
            logger.warning(f"Secure mode is ON. Preventing deletion of {filepath}")
            raise PermissionError("File deletion is disabled in secure mode.")
            
        try:
            os.remove(filepath)
            logger.info(f"Deleted file: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {filepath}: {e}")
            return False

    def summarize_file(self, filepath: str) -> str:
        """Stub for AI summarization of a file."""
        content = self.read_file(filepath)
        chunks = self.chunk_text(content)
        return f"File summary stub: {len(chunks)} chunks, {len(content)} total characters."

    def answer_about_file(self, filepath: str, question: str) -> str:
        """Stub for answering questions based on file content."""
        return f"Stub answer for '{question}' about file {filepath}."
