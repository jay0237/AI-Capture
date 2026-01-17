"""
Context Analyzer Module
Analyzes screen content and window information to understand user context
"""
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum, auto
import json

from .window_detector import WindowDetector
from .ocr_engine import OCREngine
from .models import WindowInfo

class ActivityType(Enum):
    """Types of user activities that can be detected"""
    BROWSING = auto()
    CODING = auto()
    DOCUMENT_EDITING = auto()
    SPREADSHEET = auto()
    SLIDE_PRESENTATION = auto()
    EMAIL = auto()
    MESSAGING = auto()
    MEDIA_VIEWING = auto()
    GAMING = auto()
    UNKNOWN = auto()

@dataclass
class ScreenAnalysis:
    """Stores analysis results of the current screen"""
    window_title: str = ""
    process_name: str = ""
    activity_type: ActivityType = ActivityType.UNKNOWN
    detected_text: str = ""
    detected_elements: List[Dict[str, Any]] = None
    confidence: float = 0.0
    context: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['activity_type'] = self.activity_type.name
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

class ContextAnalyzer:
    """Analyzes screen content and window information to understand user context"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ocr_engine = OCREngine()
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize patterns for context detection"""
        # Application name patterns
        self.app_patterns = {
            ActivityType.BROWSING: [
                r'chrome', r'firefox', r'safari', r'edge', r'browser', r'internet explorer'
            ],
            ActivityType.CODING: [
                r'vs code', r'visual studio', r'pycharm', r'intellij', r'sublime', 
                r'atom', r'vim', r'nano', r'emacs', r'notepad\+\+', r'eclipse', r'xcode'
            ],
            ActivityType.DOCUMENT_EDITING: [
                r'word', r'libreoffice writer', r'pages', r'notepad', r'textedit',
                r'wordpad', r'gedit', r'kate', r'geany', r'texteditor'
            ],
            ActivityType.SPREADSHEET: [
                r'excel', r'libreoffice calc', r'numbers', r'gnumeric', r'google sheets'
            ],
            ActivityType.SLIDE_PRESENTATION: [
                'powerpoint', 'libreoffice impress', 'keynote', 'google slides'
            ],
            ActivityType.EMAIL: [
                r'outlook', r'thunderbird', r'mail', r'gmail', r'sparrow', r'airmail',
                r'apple mail', r'postbox', r'mailspring', r'spark'
            ],
            ActivityType.MESSAGING: [
                r'slack', r'discord', r'teams', r'whatsapp', r'telegram', r'signal',
                r'messenger', r'skype', r'zoom', r'hangouts', r'messages'
            ],
            ActivityType.MEDIA_VIEWING: [
                r'photos', r'preview', r'gallery', r'photoshop', r'gimp', r'paint',
                r'vlc', r'quicktime', r'itunes', r'spotify', r'media player'
            ],
            ActivityType.GAMING: [
                r'steam', r'epic games', r'origin', r'battle.net', r'ubisoft',
                r'minecraft', r'fortnite', r'league of legends', r'rockstar', r'launcher'
            ]
        }
        
        # Content patterns for activity detection
        self.content_patterns = {
            ActivityType.CODING: [
                r'def\s+\w+\s*\(',
                r'function\s+\w+\s*\(',
                r'class\s+\w+',
                r'import\s+',
                r'\b(if|else|for|while|return|try|catch)\b',
                r'[{}()]',
                r'<\?php',
                r'<html',
                r'<div',
                r'\b(public|private|protected)\s+',
                r'\b(var|let|const)\s+'
            ],
            ActivityType.EMAIL: [
                r'^From:\s*',
                r'^To:\s*',
                r'^Subject:\s*',
                r'^Sent:\s*',
                r'^CC:\s*',
                r'^BCC:\s*',
                r'^Reply-To:\s*',
                r'^On\s+\w+\s+\w+\s+wrote:',
                r'\b(regards|sincerely|best|thanks|cheers|br)\b',
                r'@[\w\.-]+\.[a-z]{2,}'
            ],
            ActivityType.DOCUMENT_EDITING: [
                r'\b(abstract|introduction|conclusion|reference|appendix|figure|table)\b',
                r'\b(chapter|section|subsection|paragraph|page|line|word count)\b',
                r'\b(font|size|style|color|bold|italic|underline|align|margin|spacing)\b',
                r'\b(times new roman|arial|helvetica|calibri|cambria|verdana)\b',
                r'\b(header|footer|footnote|endnote|citation|bibliography)\b'
            ]
        }
        
        # Compile all regex patterns for better performance
        self.compiled_patterns = {
            activity_type: [re.compile(pattern, re.IGNORECASE) 
                          for pattern in patterns]
            for activity_type, patterns in {**self.app_patterns, **self.content_patterns}.items()
        }
    
    def analyze_window(self, window_info: WindowInfo, screenshot: Optional[Any] = None) -> ScreenAnalysis:
        """
        Analyze the current window and its content
        
        Args:
            window_info: Window information from WindowDetector
            screenshot: Optional screenshot (PIL Image) for content analysis
            
        Returns:
            ScreenAnalysis: Analysis results
        """
        analysis = ScreenAnalysis(
            window_title=window_info.title,
            process_name=window_info.process_name,
            activity_type=ActivityType.UNKNOWN,
            detected_text="",
            detected_elements=[],
            confidence=0.0,
            context={}
        )
        
        # First, try to determine activity from window title and process name
        self._analyze_window_metadata(window_info, analysis)
        
        # If we have a screenshot, perform OCR and content analysis
        if screenshot is not None:
            self._analyze_screenshot_content(screenshot, analysis)
        
        # Update confidence based on the analysis
        self._update_confidence(analysis)
        
        return analysis
    
    def _analyze_window_metadata(self, window_info: WindowInfo, analysis: ScreenAnalysis):
        """Analyze window title and process name to determine activity"""
        # Check against known application patterns
        matched_activities = set()
        
        for activity_type, patterns in self.app_patterns.items():
            for pattern in patterns:
                if (re.search(pattern, window_info.title, re.IGNORECASE) or 
                    re.search(pattern, window_info.process_name, re.IGNORECASE)):
                    matched_activities.add(activity_type)
                    break
        
        # If we found matches, update the analysis
        if matched_activities:
            # Prefer more specific activities if multiple matches
            if len(matched_activities) == 1:
                analysis.activity_type = matched_activities.pop()
                analysis.confidence = 0.8  # High confidence based on window info
            else:
                # If multiple matches, choose the most specific one
                priority_order = [
                    ActivityType.CODING,  # Most specific
                    ActivityType.EMAIL,
                    ActivityType.MESSAGING,
                    ActivityType.DOCUMENT_EDITING,
                    ActivityType.SPREADSHEET,
                    ActivityType.SLIDE_PRESENTATION,
                    ActivityType.BROWSING,  # More general
                    ActivityType.MEDIA_VIEWING,
                    ActivityType.GAMING
                ]
                
                for activity in priority_order:
                    if activity in matched_activities:
                        analysis.activity_type = activity
                        analysis.confidence = 0.7  # Slightly lower confidence due to ambiguity
                        break
    
    def _analyze_screenshot_content(self, screenshot, analysis: ScreenAnalysis):
        """Analyze screenshot content to refine activity detection"""
        # Extract text from the screenshot
        if self.ocr_engine.is_available():
            analysis.detected_text = self.ocr_engine.extract_text(screenshot)
            
            # If we have text, analyze it for content patterns
            if analysis.detected_text.strip():
                self._analyze_text_content(analysis)
                
                # If we still have low confidence, try to detect language
                if analysis.confidence < 0.5:
                    self._detect_language(analysis)
    
    def _analyze_text_content(self, analysis: ScreenAnalysis):
        """Analyze extracted text to determine activity"""
        text = analysis.detected_text.lower()
        
        # Check for code-like patterns
        code_score = 0
        if analysis.activity_type == ActivityType.CODING:
            code_score += 2  # Boost if we already think it's coding
                
        for pattern in self.content_patterns.get(ActivityType.CODING, []):
            if re.search(pattern, text):
                code_score += 1
        
        # If we found several code patterns, it's likely a code editor
        if code_score >= 2 and analysis.activity_type != ActivityType.CODING:
            analysis.activity_type = ActivityType.CODING
            analysis.confidence = min(0.9, analysis.confidence + 0.3)
        
        # Check for email patterns
        email_score = 0
        if analysis.activity_type == ActivityType.EMAIL:
            email_score += 2  # Boost if we already think it's email
            
        for pattern in self.content_patterns.get(ActivityType.EMAIL, []):
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                email_score += 1
        
        if email_score >= 2 and analysis.activity_type != ActivityType.EMAIL:
            analysis.activity_type = ActivityType.EMAIL
            analysis.confidence = min(0.9, analysis.confidence + 0.3)
        
        # Check for document editing patterns
        doc_score = 0
        if analysis.activity_type in [ActivityType.DOCUMENT_EDITING, 
                                    ActivityType.SPREADSHEET, 
                                    ActivityType.SLIDE_PRESENTATION]:
            doc_score += 1  # Boost if we already think it's a document
            
        for pattern in self.content_patterns.get(ActivityType.DOCUMENT_EDITING, []):
            if re.search(pattern, text, re.IGNORECASE):
                doc_score += 1
        
        if doc_score >= 2 and analysis.activity_type not in [ActivityType.DOCUMENT_EDITING, 
                                                           ActivityType.SPREADSHEET, 
                                                           ActivityType.SLIDE_PRESENTATION]:
            # If we're not sure what type of document, default to DOCUMENT_EDITING
            analysis.activity_type = ActivityType.DOCUMENT_EDITING
            analysis.confidence = min(0.8, analysis.confidence + 0.2)
    
    def _detect_language(self, analysis: ScreenAnalysis):
        """Detect language of the text to help with activity detection"""
        if not analysis.detected_text.strip():
            return
            
        # Simple language detection based on common words
        common_words = {
            'english': ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any'],
            'spanish': ['el', 'la', 'los', 'las', 'que', 'por', 'con', 'para'],
            'french': ['le', 'la', 'les', 'des', 'que', 'est', 'pour', 'dans'],
            'german': ['der', 'die', 'das', 'und', 'ist', 'nicht', 'sind', 'mit'],
            'japanese': ['の', 'に', 'は', 'を', 'た', 'し', 'が', 'で', 'て', 'と'],
            'chinese': ['的', '一', '是', '不', '了', '在', '人', '有', '我', '他'],
            'korean': ['이', '그', '저', '를', '을', '에', '와', '과', '의', '가']
        }
        
        text = analysis.detected_text.lower()
        scores = {lang: 0 for lang in common_words}
        
        for lang, words in common_words.items():
            for word in words:
                if word in text:
                    scores[lang] += 1
        
        # Get the most likely language
        detected_lang = max(scores.items(), key=lambda x: x[1])[0]
        
        # If we have a good confidence in the language, update the context
        if scores[detected_lang] >= 3:  # At least 3 matches
            analysis.context['detected_language'] = detected_lang
            analysis.confidence = max(analysis.confidence, 0.6)
    
    def _update_confidence(self, analysis: ScreenAnalysis):
        """Update confidence score based on available information"""
        # If we have both window info and content analysis, increase confidence
        if analysis.window_title and analysis.detected_text:
            analysis.confidence = min(1.0, analysis.confidence + 0.1)
        
        # If we have a lot of text, increase confidence in our analysis
        if len(analysis.detected_text) > 100:
            analysis.confidence = min(1.0, analysis.confidence + 0.1)
        
        # If we're still not confident, mark as UNKNOWN
        if analysis.confidence < 0.5:
            analysis.activity_type = ActivityType.UNKNOWN
            analysis.confidence = 0.5
        
        # Ensure confidence is within bounds
        analysis.confidence = max(0.0, min(1.0, analysis.confidence))
