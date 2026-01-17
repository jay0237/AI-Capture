"""
OCR Processor Module
Handles text extraction from images using Tesseract OCR with optimizations
"""
import cv2
import numpy as np
import pytesseract
from typing import Optional, Tuple, Dict, List
import logging

class OCRProcessor:
    """Handles OCR processing of images with optimizations"""
    
    def __init__(self, lang: str = 'eng', oem: int = 3, psm: int = 6):
        """
        Initialize the OCR processor
        
        Args:
            lang: Language code for Tesseract (default: 'eng')
            oem: OCR Engine Mode (3 = LSTM only)
            psm: Page Segmentation Mode (6 = Assume a single uniform block of text)
        """
        self.logger = logging.getLogger(__name__)
        self.lang = lang
        self.oem = oem
        self.psm = psm
        self._verify_tesseract()
    
    def _verify_tesseract(self):
        """Verify Tesseract is properly installed and accessible"""
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            self.logger.error(
                "Tesseract is not installed or not in system PATH. "
                "Please install it from https://github.com/UB-Mannheim/tesseract/wiki"
            )
            raise
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image in BGR format
            
        Returns:
            Processed grayscale image
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply adaptive thresholding
            processed = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply dilation to connect text components
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.dilate(processed, kernel, iterations=1)
            
            # Apply sharpening
            kernel_sharpening = np.array([
                [-1, -1, -1],
                [-1,  9, -1],
                [-1, -1, -1]
            ])
            processed = cv2.filter2D(processed, -1, kernel_sharpening)
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Image preprocessing failed: {e}")
            return image  # Return original if processing fails
    
    def extract_text(self, image: np.ndarray, 
                    preprocess: bool = True,
                    config: Optional[Dict] = None) -> str:
        """
        Extract text from an image using Tesseract OCR
        
        Args:
            image: Input image (BGR or grayscale)
            preprocess: Whether to preprocess the image
            config: Additional Tesseract config options
            
        Returns:
            Extracted text
        """
        try:
            # Convert to RGB if needed (Tesseract expects RGB)
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            # Preprocess if requested
            processed = self.preprocess_image(rgb_image) if preprocess else rgb_image
            
            # Build config string
            custom_config = f'--oem {self.oem} --psm {self.psm} -l {self.lang}'
            if config:
                custom_config += ' ' + ' '.join(f'-c {k}={v}' for k, v in config.items())
            
            # Run Tesseract OCR
            text = pytesseract.image_to_string(
                processed, 
                config=custom_config
            )
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return ""
    
    def get_text_boxes(self, image: np.ndarray, 
                      preprocess: bool = True) -> List[Dict]:
        """
        Get text boxes with bounding boxes and confidence scores
        
        Args:
            image: Input image (BGR or grayscale)
            preprocess: Whether to preprocess the image
            
        Returns:
            List of dictionaries containing text, bounding box, and confidence
        """
        try:
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            # Preprocess if requested
            processed = self.preprocess_image(rgb_image) if preprocess else rgb_image
            
            # Get OCR data with bounding boxes
            custom_config = f'--oem {self.oem} --psm {self.psm} -l {self.lang}'
            data = pytesseract.image_to_data(
                processed,
                output_type=pytesseract.Output.DICT,
                config=custom_config
            )
            
            # Process the data into a more usable format
            result = []
            n_boxes = len(data['level'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:  # Only include confident detections
                    result.append({
                        'text': data['text'][i],
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': int(data['conf'][i])
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get text boxes: {e}")
            return []
    
    def draw_boxes(self, image: np.ndarray, 
                  boxes: List[Dict], 
                  color: Tuple[int, int, int] = (0, 255, 0),
                  thickness: int = 2) -> np.ndarray:
        """
        Draw bounding boxes on the image
        
        Args:
            image: Input image (BGR format)
            boxes: List of bounding box dictionaries
            color: BGR color tuple
            thickness: Line thickness
            
        Returns:
            Image with drawn boxes
        """
        img_copy = image.copy()
        for box in boxes:
            x, y, w, h = box['left'], box['top'], box['width'], box['height']
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), color, thickness)
            
            # Optional: Add text label with confidence
            label = f"{box['text']} ({box['confidence']}%)"
            cv2.putText(img_copy, label, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return img_copy
