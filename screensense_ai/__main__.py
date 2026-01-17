"""
ScreenSense AI - Main Entry Point
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication
from .core.application import ScreenSenseApp

def main():
    """Main entry point for the application"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('screensense.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("ScreenSense AI")
        app.setApplicationVersion("0.1.0")
        
        # Initialize and show the main application
        screensense = ScreenSenseApp()
        screensense.show()
        
        sys.exit(app.exec())
    except Exception as e:
        logger.exception("Fatal error in main application:")
        sys.exit(1)

if __name__ == "__main__":
    main()
