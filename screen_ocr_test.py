from PIL import ImageGrab
import pytesseract

# Path to Tesseract executable (adjust if installed somewhere else)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Capture a portion of the screen
# bbox = (left, top, right, bottom) - adjust coordinates as needed
screenshot = ImageGrab.grab(bbox=(100, 100, 500, 200))

# Optional: save the screenshot to check what was captured
screenshot.save("screen_capture.png")

# Run OCR on the screenshot
text = pytesseract.image_to_string(screenshot)

print("Extracted text:", text)
