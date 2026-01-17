"""
Real-time OCR Demo
Demonstrates real-time text extraction from screen using ScreenCapture and OCRProcessor
"""
import cv2
import time
import argparse
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from screensense_ai.core.screen_capture import ScreenCapture
from screensense_ai.core.ocr_processor import OCRProcessor

class RealTimeOCR:
    """Real-time OCR processing from screen capture"""
    
    def __init__(self, lang: str = 'eng', mode: str = 'active_window', 
                 region: Optional[Tuple[int, int, int, int]] = None,
                 show_processed: bool = True):
        """
        Initialize the real-time OCR processor
        
        Args:
            lang: Language code for Tesseract
            mode: Capture mode ('full_screen', 'active_window', or 'region')
            region: Bounding box (left, top, right, bottom) for region mode
            show_processed: Whether to show the processed image
        """
        self.screen_capture = ScreenCapture()
        self.ocr = OCRProcessor(lang=lang)
        self.mode = mode
        self.region = region
        self.show_processed = show_processed
        self.running = False
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        self.avg_fps = 0
    
    def process_frame(self, frame: np.ndarray) -> Tuple[str, np.ndarray]:
        """
        Process a single frame with OCR
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            Tuple of (extracted_text, processed_frame)
        """
        # Get text boxes
        boxes = self.ocr.get_text_boxes(frame)
        
        # Draw boxes on original image
        debug_frame = self.ocr.draw_boxes(frame.copy(), boxes)
        
        # Get full text
        text = self.ocr.extract_text(frame)
        
        return text, debug_frame
    
    def run(self):
        """Run the real-time OCR loop"""
        self.running = True
        
        print("Starting real-time OCR. Press 'q' to quit.")
        print(f"Mode: {self.mode}")
        if self.region:
            print(f"Region: {self.region}")
        
        try:
            while self.running:
                start_time = time.time()
                
                # Capture screen based on mode
                if self.mode == 'full_screen':
                    frame = self.screen_capture.capture_screen()
                elif self.mode == 'active_window':
                    frame = self.screen_capture.capture_active_window()
                elif self.mode == 'region' and self.region:
                    frame = self.screen_capture.capture_screen(self.region)
                else:
                    print(f"Invalid mode or region: {self.mode}")
                    break
                
                if frame is None:
                    print("Failed to capture frame")
                    time.sleep(0.5)
                    continue
                
                # Process frame
                text, debug_frame = self.process_frame(frame)
                
                # Display results
                if text.strip():
                    print("-" * 50)
                    print(text)
                
                # Calculate FPS
                self.frame_count += 1
                if self.frame_count % 10 == 0:
                    elapsed = time.time() - self.start_time
                    self.avg_fps = self.frame_count / elapsed
                    print(f"FPS: {self.avg_fps:.1f}")
                
                # Display images
                cv2.putText(debug_frame, f"FPS: {self.avg_fps:.1f}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow("Screen Capture", debug_frame)
                
                # Check for quit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                # Small delay to prevent 100% CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            cv2.destroyAllWindows()
            self.running = False

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Real-time OCR from screen capture')
    parser.add_argument('--mode', type=str, default='active_window',
                       choices=['full_screen', 'active_window', 'region'],
                       help='Capture mode (default: active_window)')
    parser.add_argument('--region', type=int, nargs=4,
                       metavar=('LEFT', 'TOP', 'RIGHT', 'BOTTOM'),
                       help='Region coordinates (for region mode)')
    parser.add_argument('--lang', type=str, default='eng',
                       help='Language code for OCR (default: eng)')
    parser.add_argument('--show-processed', action='store_true',
                       help='Show processed image for debugging')
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_args()
    
    # Create and run the OCR processor
    ocr = RealTimeOCR(
        lang=args.lang,
        mode=args.mode,
        region=tuple(args.region) if args.region else None,
        show_processed=args.show_processed
    )
    
    try:
        ocr.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
