"""
Document Processor
==================
Handles PDF, DOCX, and TXT file processing with text extraction,
summarization, and genuineness verification.
"""

import os
from typing import Tuple, Dict, Optional
from PyPDF2 import PdfReader
from docx import Document
import magic
from langchain_groq import ChatGroq


class DocumentProcessor:
    """Process uploaded documents and extract information."""
    
    def __init__(self, llm):
        """
        Initialize document processor.
        
        Args:
            llm: Language model for summarization and analysis
        """
        self.llm = llm
        self.supported_types = {
            'application/pdf': self._extract_pdf,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._extract_docx,
            'text/plain': self._extract_txt
        }
    
    def process_document(self, file_path: str) -> Dict:
        """
        Process a document and extract information.
        
        Args:
            file_path: Path to the uploaded file
            
        Returns:
            Dict containing extracted text, summary, and analysis
        """
        # Detect file type
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        
        if file_type not in self.supported_types:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Extract text
        text = self.supported_types[file_type](file_path)
        
        if not text or len(text.strip()) < 50:
            raise ValueError("Document appears to be empty or too short")
        
        # Generate summary
        summary = self._generate_summary(text)
        
        # Verify genuineness
        genuineness_report = self._verify_genuineness(text, summary)
        
        return {
            'text': text,
            'summary': summary,
            'genuineness': genuineness_report,
            'word_count': len(text.split()),
            'char_count': len(text)
        }
    
    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract PDF text: {str(e)}")
    
    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract DOCX text: {str(e)}")
    
    def _extract_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read().strip()
    
    def _generate_summary(self, text: str) -> str:
        """
        Generate a concise summary of the document.
        
        Args:
            text: Full document text
            
        Returns:
            Summary string
        """
        # Limit text to first 4000 characters to avoid token limits
        text_preview = text[:4000] if len(text) > 4000 else text
        
        prompt = f"""Analyze this document and provide a concise summary (3-5 sentences) covering:
1. Main topic/subject
2. Key findings or arguments
3. Document type (research paper, article, report, etc.)

Document text:
{text_preview}

Summary:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    def _verify_genuineness(self, text: str, summary: str) -> Dict:
        """
        Verify document genuineness and check for potential issues.
        
        Args:
            text: Full document text
            summary: Generated summary
            
        Returns:
            Dict with genuineness analysis
        """
        # Limit text for analysis
        text_preview = text[:3000] if len(text) > 3000 else text
        
        prompt = f"""Analyze this document for authenticity and quality. Provide:

1. **Authenticity Score** (1-10): How genuine/legitimate does this document appear?
2. **Quality Assessment**: Is this a proper academic/professional document?
3. **Red Flags**: Any signs of:
   - Plagiarism indicators
   - AI-generated content
   - Fake citations
   - Poor formatting
   - Inconsistencies
4. **Recommendations**: Should this document be trusted for research?

Document Summary: {summary}

Document Text (preview):
{text_preview}

Provide analysis in this format:
**Authenticity Score**: [1-10]
**Quality**: [High/Medium/Low]
**Red Flags**: [List any concerns or "None detected"]
**Recommendation**: [Trust/Verify/Reject]
**Reasoning**: [Brief explanation]
"""
        
        try:
            response = self.llm.invoke(prompt)
            analysis_text = response.content.strip()
            
            # Parse the response
            score = 0
            if "Authenticity Score" in analysis_text:
                try:
                    score_line = [line for line in analysis_text.split('\n') if 'Authenticity Score' in line][0]
                    score = int(''.join(filter(str.isdigit, score_line)))
                except:
                    score = 5  # Default to neutral
            
            return {
                'score': score,
                'analysis': analysis_text,
                'is_genuine': score >= 6,
                'confidence': 'High' if score >= 8 or score <= 3 else 'Medium'
            }
        except Exception as e:
            return {
                'score': 0,
                'analysis': f"Verification failed: {str(e)}",
                'is_genuine': False,
                'confidence': 'Low'
            }
