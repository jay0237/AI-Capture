import sys
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import os

def test_tesseract():
    try:
        # Try to find Tesseract executable in common locations
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\\tesseract.exe',
            r'C:\Program Files (x86)\\Tesseract-OCR\\tesseract.exe',
            r'C:\\tesseract\\tesseract.exe',
            'tesseract'  # This will work if it's in PATH
        ]
        
        # Test each path
        for path in tesseract_paths:
            try:
                pytesseract.pytesseract.tesseract_cmd = path
                # Create a simple image with text to test OCR
                img = Image.new('RGB', (400, 100), color=(255, 255, 255))
                d = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("Arial", 24)
                except:
                    font = ImageFont.load_default()
                d.text((10, 40), "Hello, Tesseract!", fill=(0, 0, 0), font=font)
                
                # Save test image
                test_img_path = "test_ocr.png"
                img.save(test_img_path)
                
                # Try to read the text
                text = pytesseract.image_to_string(img)
                text = text.strip()
                
                if text:
                    print("="*50)
                    print("🎉 Tesseract is working correctly!")
                    print(f"Found Tesseract at: {path}")
                    print(f"Test image saved as: {os.path.abspath(test_img_path)}")
                    print(f"Extracted text: '{text}'")
                    print("="*50)
                    return True
                    
            except Exception as e:
                if "is not installed or it's not in your PATH" in str(e):
                    continue
                print(f"Tried {path}: {str(e)}")
        
        print("❌ Could not find or run Tesseract. Please check your installation.")
        print("Make sure Tesseract is installed and added to your system PATH.")
        print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
        
    except Exception as e:
        print(f"❌ Error testing Tesseract: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Tesseract OCR installation...")
    test_tesseract()
