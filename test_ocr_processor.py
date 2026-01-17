"""
Test script for OCR Processor functionality
"""
import cv2
import numpy as np
from screensense_ai.core.ocr_processor import OCRProcessor
from screensense_ai.core.screen_capture import ScreenCapture

def test_image_processing():
    """Test image preprocessing and text extraction"""
    print("Testing OCR Processor...")
    
    # Initialize OCR processor
    ocr = OCRProcessor(lang='eng')
    
    # Create a test image with text
    img = np.zeros((200, 400, 3), dtype=np.uint8)
    cv2.putText(img, "Hello, World!", (50, 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Test preprocessing
    processed = ocr.preprocess_image(img)
    cv2.imwrite("test_original.png", img)
    cv2.imwrite("test_processed.png", processed)
    print("Saved test images: test_original.png, test_processed.png")
    
    # Test text extraction
    text = ocr.extract_text(img)
    print(f"Extracted text: {text}")
    
    # Test text boxes
    boxes = ocr.get_text_boxes(img)
    print(f"Found {len(boxes)} text boxes")
    
    # Draw boxes
    debug_img = ocr.draw_boxes(img, boxes)
    cv2.imwrite("test_boxes.png", debug_img)
    print("Saved test_boxes.png with detected text areas")

def test_screen_capture():
    """Test screen capture with OCR"""
    print("\nTesting Screen Capture with OCR...")
    
    # Initialize screen capture and OCR
    capture = ScreenCapture()
    ocr = OCRProcessor(lang='eng')
    
    # Capture active window
    print("Capturing active window...")
    img = capture.capture_active_window()
    
    if img is not None:
        # Save original
        cv2.imwrite("screen_original.png", img)
        
        # Process and save
        text = ocr.extract_text(img)
        with open("screen_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
        
        # Get and draw boxes
        boxes = ocr.get_text_boxes(img)
        debug_img = ocr.draw_boxes(img, boxes)
        cv2.imwrite("screen_boxes.png", debug_img)
        
        print("Saved results to screen_*.{png,txt}")
        print("\nExtracted text preview:")
        print("-" * 50)
        print(text[:500] + ("..." if len(text) > 500 else ""))
        print("-" * 50)
    else:
        print("Failed to capture screen")

if __name__ == "__main__":
    test_image_processing()
    test_screen_capture()
