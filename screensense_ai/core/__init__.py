"""
ScreenSense AI Core Module
Provides the core functionality for the ScreenSense AI application
"""

from .window_detector import WindowDetector
from .screen_capture import ScreenCapture
from .ocr_engine import OCREngine
from .context_analyzer import ContextAnalyzer, ActivityType, ScreenAnalysis
from .models import WindowInfo

__all__ = [
    'WindowDetector',
    'ScreenCapture',
    'OCREngine',
    'ContextAnalyzer',
    'ActivityType',
    'ScreenAnalysis',
    'WindowInfo'
]
