"""
OCR Engine Module
Handles text extraction from images using Tesseract OCR
"""
import logging
import platform
from typing import Optional, Dict, List, Tuple
import numpy as np
from PIL import Image

class OCREngine:
    """Handles OCR operations using Tesseract"""
    
    def __init__(self, lang: str = 'eng'):
        """
        Initialize the OCR engine
        
        Args:
            lang: Language code for OCR (default: 'eng' for English)
        """
        self.logger = logging.getLogger(__name__)
        self.lang = lang
        self._tesseract_available = False
        self._init_tesseract()
    
    def _init_tesseract(self):
        """Initialize Tesseract OCR with proper error handling"""
        try:
            import pytesseract
            self._tesseract_available = True
            
            # Set Tesseract command path if on Windows
            if platform.system() == 'Windows':
                # Common installation paths for Tesseract on Windows
                tesseract_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
                ]
                
                for path in tesseract_paths:
                    try:
                        pytesseract.pytesseract.tesseract_cmd = path
                        # Test if Tesseract is working
                        pytesseract.get_tesseract_version()
                        self.logger.info(f"Tesseract initialized successfully at {path}")
                        break
                    except (pytesseract.TesseractNotFoundError, Exception):
                        continue
                else:
                    self.logger.warning(
                        "Tesseract not found in default locations. "
                        "Please install Tesseract and add it to your PATH or set the path manually."
                    )
                    self._tesseract_available = False
            
        except ImportError:
            self.logger.warning(
                "pytesseract not installed. Install with: pip install pytesseract"
            )
        except Exception as e:
            self.logger.error(f"Error initializing Tesseract: {e}")
            self._tesseract_available = False
    
    def is_available(self) -> bool:
        """Check if OCR functionality is available"""
        return self._tesseract_available
    
    def extract_text(self, image: Image.Image, lang: Optional[str] = None) -> str:
        """
        Extract text from an image
        
        Args:
            image: PIL Image to process
            lang: Language code (overrides default if provided)
            
        Returns:
            str: Extracted text
        """
        if not self._tesseract_available:
            self.logger.warning("Tesseract OCR is not available")
            return ""
            
        try:
            import pytesseract
            
            # Convert image to RGB if it's not
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Use provided language or default
            lang_to_use = lang if lang is not None else self.lang
            
            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=lang_to_use,
                config='--psm 6'  # Assume a single uniform block of text
            )
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error extracting text with Tesseract: {e}")
            return ""
    
    def extract_text_with_boxes(
        self, 
        image: Image.Image, 
        lang: Optional[str] = None
    ) -> Tuple[str, List[Dict]]:
        """
        Extract text with bounding box information
        
        Args:
            image: PIL Image to process
            lang: Language code (overrides default if provided)
            
        Returns:
            tuple: (full_text, boxes)
                - full_text: Combined text from all detections
                - boxes: List of dicts with 'text', 'left', 'top', 'width', 'height'
        """
        if not self._tesseract_available:
            self.logger.warning("Tesseract OCR is not available")
            return "", []
            
        try:
            import pytesseract
            
            # Convert image to RGB if it's not
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Use provided language or default
            lang_to_use = lang if lang is not None else self.lang
            
            # Get OCR data including bounding boxes
            ocr_data = pytesseract.image_to_data(
                image,
                lang=lang_to_use,
                output_type=pytesseract.Output.DICT,
                config='--psm 6'  # Assume a single uniform block of text
            )
            
            # Process the data
            full_text = '\n'.join([t for t in ocr_data['text'] if t.strip()])
            
            # Create list of text boxes with their positions
            boxes = []
            n_boxes = len(ocr_data['text'])
            for i in range(n_boxes):
                if int(ocr_data['conf'][i]) > 60:  # Confidence threshold
                    boxes.append({
                        'text': ocr_data['text'][i],
                        'left': int(ocr_data['left'][i]),
                        'top': int(ocr_data['top'][i]),
                        'width': int(ocr_data['width'][i]),
                        'height': int(ocr_data['height'][i]),
                        'confidence': int(ocr_data['conf'][i])
                    })
            
            return full_text, boxes
            
        except Exception as e:
            self.logger.error(f"Error extracting text with boxes: {e}")
            return "", []
    
    def detect_language(self, image: Image.Image) -> str:
        """
        Detect the language of text in an image
        
        Args:
            image: PIL Image to analyze
            
        Returns:
            str: Detected language code (e.g., 'eng', 'fra', 'spa')
        """
        if not self._tesseract_available:
            self.logger.warning("Tesseract OCR is not available")
            return ""
            
        try:
            import pytesseract
            
            # Convert image to RGB if it's not
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get the script and orientation
            osd = pytesseract.image_to_osd(image)
            
            # Parse the OSD output to get the script (language script, not exact language)
            # This is a simple implementation - for better language detection, consider using langdetect
            # on the extracted text
            script = ""
            for line in osd.split('\n'):
                if 'Script:' in line:
                    script = line.split('Script:')[-1].strip()
                    break
            
            # Map script to language code (simplified)
            script_to_lang = {
                'Latin': 'eng',
                'Cyrillic': 'rus',
                'Greek': 'ell',
                'Han': 'chi_sim',
                'Hangul': 'kor',
                'Hiragana': 'jpn',
                'Katakana': 'jpn',
                'Devanagari': 'hin',
                'Thai': 'tha',
                'Arabic': 'ara',
                'Hebrew': 'heb',
            }
            
            return script_to_lang.get(script, 'eng')
            
        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            return "eng"  # Default to English on error
