"""
Screen Capture Module
Handles high-performance screen capturing with Windows-specific optimizations
"""
import logging
import platform
from typing import Optional, Tuple
import numpy as np
from PIL import ImageGrab, Image
import cv2

# Try to import Windows-specific libraries
try:
    import mss
    import mss.windows
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    
try:
    import win32gui
    import win32ui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

class ScreenCapture:
    """Handles screen capture functionality with platform-specific optimizations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system()
        self._sct = None
        self._init_platform()
    
    def _init_platform(self):
        """Initialize platform-specific capture methods"""
        if self.system == 'Windows' and MSS_AVAILABLE:
            try:
                self._sct = mss.mss()
                self.logger.info("Initialized MSS for screen capture")
            except Exception as e:
                self.logger.warning(f"Failed to initialize MSS: {e}")
    
    def __del__(self):
        """Clean up resources"""
        if self._sct:
            self._sct.close()
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Capture the screen or a specific region with optimal method for the platform.
        
        Args:
            region: Optional (left, top, right, bottom) coordinates
            
        Returns:
            numpy.ndarray: Captured image in BGR format, or None if capture failed
        """
        try:
            if self.system == 'Windows':
                return self._capture_windows(region)
            return self._capture_fallback(region)
        except Exception as e:
            self.logger.error(f"Screen capture failed: {e}")
            return None
    
    def _capture_windows(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """Windows-specific screen capture with multiple fallback methods"""
        # Try MSS first (fastest for full screen)
        if self._sct and (region is None or (region[2] - region[0]) >= 800):
            try:
                monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
                if region:
                    monitor = {
                        "top": region[1],
                        "left": region[0],
                        "width": region[2] - region[0],
                        "height": region[3] - region[1]
                    }
                sct_img = self._sct.grab(monitor)
                return np.array(sct_img)[:, :, :3]  # Remove alpha channel
            except Exception as e:
                self.logger.debug(f"MSS capture failed, falling back to GDI: {e}")
        
        # Fall back to GDI for window capture or small regions
        if WIN32_AVAILABLE:
            return self._capture_windows_gdi(region)
            
        # Final fallback to PIL
        return self._capture_fallback(region)
    
    def _capture_windows_gdi(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """Windows GDI-based screen capture"""
        try:
            if region is None:
                left, top = 0, 0
                width = win32api.GetSystemMetrics(0)
                height = win32api.GetSystemMetrics(1)
            else:
                left, top, right, bottom = region
                width = right - left
                height = bottom - top
            
            hwnd = win32gui.GetDesktopWindow()
            hwindc = win32gui.GetWindowDC(hwnd)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, width, height)
            memdc.SelectObject(bmp)
            memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
            
            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img = img.reshape((bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4))
            
            # Clean up
            win32gui.DeleteObject(bmp.GetHandle())
            memdc.DeleteDC()
            srcdc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwindc)
            
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
        except Exception as e:
            self.logger.error(f"Windows GDI capture failed: {e}")
            return None
    
    def _capture_fallback(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """Fallback method using PIL's ImageGrab"""
        try:
            screenshot = ImageGrab.grab(bbox=region) if region else ImageGrab.grab()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            self.logger.error(f"Fallback screen capture failed: {e}")
            return None
    
    def capture_active_window(self) -> Optional[np.ndarray]:
        """Capture the currently active window"""
        if not WIN32_AVAILABLE:
            return self.capture_screen()
            
        try:
            hwnd = win32gui.GetForegroundWindow()
            rect = win32gui.GetWindowRect(hwnd)
            return self.capture_screen(rect)
        except Exception as e:
            self.logger.error(f"Failed to capture active window: {e}")
            return self.capture_screen()
