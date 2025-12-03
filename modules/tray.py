import sys
import os
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

class TrayIcon:
    """시스템 트레이 아이콘 (최적화 버전)"""
    __slots__ = ('on_exit_callback', 'icon', '_image_cache')
    
    def __init__(self, on_exit_callback):
        self.on_exit_callback = on_exit_callback
        self.icon = None
        self._image_cache = None
    
    def load_icon_image(self):
        """아이콘 로드 (캐싱)"""
        if self._image_cache:
            return self._image_cache
        
        base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        
        # icon.ico 경로 탐색
        icon_paths = [
            os.path.join(base, 'icon.ico'),
            os.path.join(os.path.dirname(base), 'icon.ico')
        ]
        
        for path in icon_paths:
            try:
                if os.path.exists(path):
                    self._image_cache = Image.open(path).resize((64, 64), Image.Resampling.LANCZOS)
                    return self._image_cache
            except Exception:
                continue
        
        # 기본 아이콘 생성
        img = Image.new('RGB', (64, 64), 'black')
        d = ImageDraw.Draw(img)
        d.ellipse([8, 8, 56, 56], fill='green', outline='white', width=3)
        d.text((20, 15), 'M', fill='white')
        self._image_cache = img
        return img
    
    def on_quit(self, icon, item):
        """종료 처리"""
        icon.stop()
        if self.on_exit_callback:
            self.on_exit_callback()
        os._exit(0)
    
    def run(self):
        """트레이 아이콘 실행"""
        menu = Menu(
            MenuItem('KeyM', lambda: None, enabled=False), 
            MenuItem('종료', self.on_quit)
        )
        self.icon = Icon("KeyM", self.load_icon_image(), "KeyM", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()