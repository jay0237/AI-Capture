"""
Window Detection Module
Handles detection of the active window and its properties
"""
import logging
import platform
import re
from typing import Dict, Any, Optional, Tuple, List

from .models import WindowInfo

class WindowDetector:
    """Detects and provides information about the active window"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system()
        self._init_platform_specific()
    
    def _init_platform_specific(self):
        """Initialize platform-specific window detection"""
        if self.system == 'Windows':
            import win32gui
            import win32process
            self._get_active_window = self._get_active_window_windows
        elif self.system == 'Darwin':  # macOS
            from AppKit import NSWorkspace
            self._get_active_window = self._get_active_window_macos
        else:  # Linux
            try:
                import Xlib.display
                self._get_active_window = self._get_active_window_linux
            except ImportError:
                self.logger.warning("Xlib not available. Window detection will be limited.")
                self._get_active_window = self._get_active_window_fallback
    
    def get_active_window_info(self) -> WindowInfo:
        """
        Get information about the currently active window
        
        Returns:
            WindowInfo: Object containing window information
        """
        try:
            return self._get_active_window()
        except Exception as e:
            self.logger.error(f"Error getting active window info: {e}")
            return WindowInfo(
                title='Unknown',
                process_name='unknown',
                process_id=0,
                app_type='other',
                url=None
            )
    
    def _get_active_window_windows(self) -> WindowInfo:
        """Get active window info on Windows"""
        import win32gui
        import win32process
        
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        
        # Get process name and ID
        _, pid = win32process.GetWindowThreadProcessId(window)
        process_name = self._get_process_name_windows(pid) if pid else 'unknown'
        
        # Determine app type
        app_type = self._classify_app_type(process_name, title)
        
        # Get URL if it's a browser
        url = self._get_browser_url(window) if 'browser' in app_type else None
        
        return WindowInfo(
            title=title,
            process_name=process_name,
            process_id=pid or 0,
            app_type=app_type,
            url=url,
            metadata={
                'window_handle': window,
                'platform': 'windows'
            }
        )
    
    def _get_active_window_macos(self) -> WindowInfo:
        """Get active window info on macOS"""
        try:
            from AppKit import NSWorkspace, NSApplication, NSAutoreleasePool
            
            pool = NSAutoreleasePool.alloc().init()
            
            # Get the frontmost application
            app = NSWorkspace.sharedWorkspace().frontmostApplication()
            process_name = app.localizedName()
            pid = app.processIdentifier()
            
            # Get window title (this is a simplified approach)
            title = self._get_macos_window_title() or process_name
            
            # Determine app type
            app_type = self._classify_app_type(process_name, title)
            
            # Get URL if it's a browser
            url = self._get_browser_url_macos() if 'browser' in app_type else None
            
            return WindowInfo(
                title=title,
                process_name=process_name,
                process_id=pid,
                app_type=app_type,
                url=url,
                metadata={
                    'bundle_identifier': app.bundleIdentifier(),
                    'platform': 'darwin'
                }
            )
        except Exception as e:
            self.logger.error(f"Error getting macOS window info: {e}")
            return self._get_active_window_fallback()
        finally:
            if 'pool' in locals():
                pool.drain()
    
    def _get_active_window_linux(self) -> WindowInfo:
        """Get active window info on Linux"""
        try:
            from Xlib import display, X, Xatom
            
            d = display.Display()
            root = d.screen().root
            window = root.get_full_property(
                d.intern_atom('_NET_ACTIVE_WINDOW'),
                X.AnyPropertyType
            ).value[0]
            
            # Get window title
            title = self._get_linux_window_title(d, window)
            
            # Get process name
            process_name = self._get_process_name_linux(d, window)
            
            # Get PID
            pid = self._get_linux_window_pid(d, window)
            
            # Determine app type
            app_type = self._classify_app_type(process_name, title)
            
            # Get URL if it's a browser
            url = self._get_browser_url_linux(d, window) if 'browser' in app_type else None
            
            return WindowInfo(
                title=title,
                process_name=process_name,
                process_id=pid or 0,
                app_type=app_type,
                url=url,
                metadata={
                    'window_id': window,
                    'platform': 'linux'
                }
            )
        except Exception as e:
            self.logger.error(f"Error getting Linux window info: {e}")
            return self._get_active_window_fallback()
        from Xlib import display, X
        
        d = display.Display()
        window = d.get_input_focus().focus
        
        # Get window title
        title = window.get_wm_name()
        
        # Get process name (this is a simplified version)
        process_name = self._get_process_name_linux(window)
        
        # Determine app type
        app_type = self._classify_app_type(process_name, title)
        
        return {
            'title': title,
            'process': process_name,
            'app_type': app_type,
            'url': None  # Browser URL detection on Linux requires additional work
        }
    
    def _get_active_window_fallback(self) -> Dict[str, Any]:
        """Fallback method for unsupported platforms"""
        return {
            'title': 'Unknown',
            'process': 'unknown',
            'app_type': 'other',
            'url': None
        }
    
    def _get_process_name_windows(self, pid: int) -> str:
        """Get process name from PID on Windows"""
        import psutil
        try:
            process = psutil.Process(pid)
            return process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return 'unknown'
    
    def _get_process_name_linux(self, window) -> str:
        """Get process name from window on Linux"""
        # This is a simplified version and might need adjustment
        try:
            from Xlib import Xatom
            net_wm_pid = window.get_full_property(
                window.display.intern_atom('_NET_WM_PID'),
                Xatom.CARDINAL
            )
            if net_wm_pid:
                import psutil
                process = psutil.Process(net_wm_pid.value[0])
                return process.name()
        except Exception:
            pass
        return 'unknown'
    
    def _classify_app_type(self, process_name: str, title: str) -> str:
        """Classify the application type based on process name and title"""
        process_name = process_name.lower()
        
        # Check for browsers
        browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera', 'brave']
        if any(browser in process_name for browser in browsers):
            return 'browser'
            
        # Check for text editors and IDEs
        editors = ['code', 'pycharm', 'sublime', 'atom', 'notepad', 'gedit', 'vim', 'nano']
        if any(editor in process_name for editor in editors):
            return 'editor'
            
        # Check for office applications
        office = ['excel', 'word', 'powerpoint', 'libreoffice', 'calc', 'writer']
        if any(app in process_name for app in office):
            return 'office'
            
        # Check for terminals
        terminals = ['cmd', 'powershell', 'terminal', 'iterm', 'gnome-terminal', 'konsole']
        if any(term in process_name for term in terminals):
            return 'terminal'
            
        # Check for PDF viewers
        if 'acrobat' in process_name or 'pdf' in process_name:
            return 'pdf_reader'
            
        return 'other'
    
    def _get_browser_url(self, window) -> Optional[str]:
        """Get the current URL from a browser window (Windows only)"""
        try:
            import win32gui
            import win32con
            import win32process
            import ctypes
            
            # Get the process ID
            _, pid = win32process.GetWindowThreadProcessId(window)
            
            # Get process handle
            PROCESS_VM_READ = 0x0010
            process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_VM_READ, False, pid)
            
            if not process_handle:
                return None
                
            # This is a simplified version - actual implementation would need
            # to read the browser's memory to find the URL
            # For a production app, consider using browser extensions or APIs
            
            ctypes.windll.kernel32.CloseHandle(process_handle)
            return None
            
        except Exception as e:
            self.logger.debug(f"Could not get browser URL: {e}")
            return None
