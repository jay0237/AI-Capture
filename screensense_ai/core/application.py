""
ScreenSense AI - Main Application Class
"""
import os
import json
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from ..utils.config import load_config, save_config
from ..core.window_detector import WindowDetector
from ..core.screen_capture import ScreenCapture
from ..core.ocr_engine import OCREngine
from ..core.context_analyzer import ContextAnalyzer
from ..ui.main_window import MainWindow

class ScreenSenseApp(QObject):
    """Main application class for ScreenSense AI"""
    
    # Signals
    context_updated = pyqtSignal(dict)  # Emitted when context changes
    suggestion_ready = pyqtSignal(dict)  # Emitted when a suggestion is ready
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.config = self._load_or_create_config()
        
        # Initialize core components
        self.window_detector = WindowDetector()
        self.screen_capture = ScreenCapture()
        self.ocr_engine = OCREngine()
        self.context_analyzer = ContextAnalyzer()
        
        # Initialize UI
        self.main_window = MainWindow()
        self._setup_connections()
        
        # Start monitoring
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self.update_context)
        self.set_monitoring_interval(self.config.get('monitoring_interval', 5))
    
    def _load_or_create_config(self) -> dict:
        """Load or create the application configuration"""
        config_path = Path.home() / '.screensense' / 'config.json'
        default_config = {
            'monitoring_enabled': False,
            'monitoring_interval': 5,  # seconds
            'privacy_mode': 'high',  # high, medium, low
            'allow_remote_ai': False,
            'recent_contexts': []
        }
        
        return load_config(config_path, default_config)
    
    def _setup_connections(self):
        """Set up signal connections"""
        self.context_updated.connect(self.main_window.update_context)
        self.suggestion_ready.connect(self.main_window.show_suggestion)
        
        # Connect UI signals
        self.main_window.toggle_monitoring.connect(self.toggle_monitoring)
        self.main_window.update_preferences.connect(self.update_preferences)
    
    def start_monitoring(self):
        """Start monitoring the active window"""
        if not self.config['monitoring_enabled']:
            self.config['monitoring_enabled'] = True
            self.monitoring_timer.start()
            self.logger.info("Monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring the active window"""
        self.monitoring_timer.stop()
        self.config['monitoring_enabled'] = False
        self.logger.info("Monitoring stopped")
    
    def toggle_monitoring(self, enabled: bool):
        """Toggle monitoring on/off"""
        if enabled:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def set_monitoring_interval(self, seconds: int):
        """Set the monitoring interval in seconds"""
        self.monitoring_timer.setInterval(seconds * 1000)  # Convert to milliseconds
        self.config['monitoring_interval'] = seconds
    
    def update_context(self):
        """Update the current context based on active window and content"""
        try:
            # Get active window info
            window_info = self.window_detector.get_active_window_info()
            
            # Capture screen content if monitoring is enabled
            screenshot = None
            if self.config['monitoring_enabled']:
                screenshot = self.screen_capture.capture_active_window()
                
                # Extract text using OCR
                ocr_text = self.ocr_engine.extract_text(screenshot)
                
                # Analyze context
                context = self.context_analyzer.analyze(window_info, ocr_text)
                
                # Update recent contexts
                self._update_recent_contexts(context)
                
                # Emit updated context
                self.context_updated.emit(context)
                
                # Get suggestions based on context
                self.get_suggestions(context)
                
        except Exception as e:
            self.logger.error(f"Error updating context: {e}")
    
    def get_suggestions(self, context: dict):
        """Get suggestions based on current context"""
        try:
            # Get suggestions from context analyzer
            suggestions = self.context_analyzer.get_suggestions(context)
            
            # Emit suggestions
            for suggestion in suggestions:
                self.suggestion_ready.emit(suggestion)
                
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {e}")
    
    def update_preferences(self, preferences: dict):
        """Update application preferences"""
        self.config.update(preferences)
        self.save_config()
        
        # Apply preference changes
        if 'monitoring_interval' in preferences:
            self.set_monitoring_interval(preferences['monitoring_interval'])
    
    def save_config(self):
        """Save the current configuration"""
        config_path = Path.home() / '.screensense' / 'config.json'
        save_config(config_path, self.config)
    
    def _update_recent_contexts(self, context: dict):
        """Update the list of recent contexts"""
        recent = self.config.get('recent_contexts', [])
        recent.insert(0, context)
        self.config['recent_contexts'] = recent[:10]  # Keep only the 10 most recent
    
    def show(self):
        """Show the main window"""
        self.main_window.show()
    
    def close(self):
        """Clean up resources"""
        self.save_config()
        self.stop_monitoring()
        self.main_window.close()
