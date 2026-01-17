"""
Data models for ScreenSense AI
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class WindowInfo:
    """Stores information about a window"""
    title: str
    process_name: str
    process_id: int
    app_type: str
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'process_name': self.process_name,
            'process_id': self.process_id,
            'app_type': self.app_type,
            'url': self.url,
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WindowInfo':
        """Create from dictionary"""
        return cls(
            title=data.get('title', ''),
            process_name=data.get('process_name', ''),
            process_id=data.get('process_id', 0),
            app_type=data.get('app_type', 'unknown'),
            url=data.get('url'),
            metadata=data.get('metadata')
        )
