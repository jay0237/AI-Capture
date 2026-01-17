import cv2
import numpy as np
import pytesseract
from PIL import ImageGrab, ImageEnhance, ImageFilter

def preprocess_image(image):
    """Enhance image for better OCR results"""
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to get binary image
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Apply dilation to connect text components
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.dilate(thresh, kernel, iterations=1)
    
    # Apply sharpening
    kernel_sharpening = np.array([[-1, -1, -1],
                                [-1, 9, -1],
                                [-1, -1, -1]])
    processed = cv2.filter2D(processed, -1, kernel_sharpening)
    
    return processed

def capture_and_ocr(bbox=(100, 100, 800, 400), show_images=False):
    """Capture screen region and perform OCR with enhanced processing"""
    try:
        # Set Tesseract path
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\\tesseract.exe'
        
        # Capture screen
        screenshot = ImageGrab.grab(bbox=bbox)
        original = np.array(screenshot)
        
        # Preprocess image
        processed = preprocess_image(screenshot)
        
        # Save images for debugging
        Image.fromarray(original).save("original_capture.png")
        Image.fromarray(processed).save("processed_capture.png")
        
        # Configure Tesseract parameters
        custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
        
        # Run Tesseract with different configurations
        text_processed = pytesseract.image_to_string(processed, config=custom_config)
        text_original = pytesseract.image_to_string(original, config=custom_config)
        
        # Print results
        print("="*50)
        print("Original OCR Result:")
        print("-"*50)
        print(text_original)
        print("\n" + "="*50)
        print("Enhanced OCR Result:")
        print("-"*50)
        print(text_processed)
        print("="*50)
        
        # Show images if requested
        if show_images:
            cv2.imshow("Original", cv2.cvtColor(original, cv2.COLOR_RGB2BGR))
            cv2.imshow("Processed", processed)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        return text_processed.strip()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return ""

if __name__ == "__main__":
    print("Screen OCR Test - Press Ctrl+C to exit")
    print("Click on the window you want to capture, then press Enter")
    input("Press Enter to continue...")
    
    # Example coordinates - modify these to capture a specific area
    # Format: (left, top, right, bottom)
    bbox = (100, 100, 800, 400)
    
    while True:
        try:
            input("Press Enter to capture screen (or Ctrl+C to exit)...")
            capture_and_ocr(bbox, show_images=True)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
