import sys
import os
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

class TrayIcon:
    """시스템 트레이 아이콘"""
    
    def __init__(self, on_exit_callback):
        self.on_exit_callback = on_exit_callback
        self.icon = None
    
    def load_icon_image(self):
        """아이콘 로드"""
        base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, 'icon.ico')
        
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(base), 'icon.ico')
        
        try:
            if os.path.exists(path):
                return Image.open(path).resize((64, 64), Image.Resampling.LANCZOS)
        except:
            pass
        
        # 기본 아이콘
        img = Image.new('RGB', (64, 64), 'black')
        d = ImageDraw.Draw(img)
        d.ellipse([8, 8, 56, 56], fill='green', outline='white', width=3)
        d.text((20, 15), 'M', fill='white')
        return img
    
    def on_quit(self, icon, item):
        """종료"""
        icon.stop()
        if self.on_exit_callback:
            self.on_exit_callback()
        os._exit(0)
    
    def run(self):
        """실행"""
        self.icon = Icon(
            "GThey5M",
            self.load_icon_image(),
            "GThey5M",
            Menu(
                MenuItem('GThey5M', lambda: None, enabled=False),
                MenuItem('종료', self.on_quit)
            )
        )
        threading.Thread(target=lambda: self.icon.run(), daemon=True).start()