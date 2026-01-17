"""
Test script for ScreenCapture functionality
"""
import cv2
import time
# Use relative import since we're in the project root
from screensense_ai.core.screen_capture import ScreenCapture
# If the above doesn't work, try uncommenting the line below:
# from .screensense_ai.core.screen_capture import ScreenCapture

def main():
    print("Testing ScreenCapture...")
    
    # Initialize screen capture
    capture = ScreenCapture()
    
    # Test full screen capture
    print("Capturing full screen...")
    img = capture.capture_screen()
    if img is not None:
        cv2.imwrite("full_screen.png", img)
        print("Saved full screen capture as 'full_screen.png'")
    
    # Test active window capture
    print("Capturing active window...")
    img = capture.capture_active_window()
    if img is not None:
        cv2.imwrite("active_window.png", img)
        print("Saved active window capture as 'active_window.png'")
    
    # Test region capture (top-left 800x600)
    print("Capturing region (0, 0, 800, 600)...")
    img = capture.capture_screen((0, 0, 800, 600))
    if img is not None:
        cv2.imwrite("region.png", img)
        print("Saved region capture as 'region.png'")
    
    print("Done!")

if __name__ == "__main__":
    main()
