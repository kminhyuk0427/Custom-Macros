import sys
import os
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image

class TrayIcon:
    """시스템 트레이 아이콘"""
    
    def __init__(self, on_exit_callback):
        self.on_exit_callback = on_exit_callback
        self.icon = None
        self.running = True
    
    def load_icon_image(self):
        """아이콘 로드"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_path = os.path.join(base_path, 'icon.ico')
        
        if not os.path.exists(icon_path):
            parent_path = os.path.dirname(base_path)
            icon_path = os.path.join(parent_path, 'icon.ico')
        
        try:
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                image = image.resize((64, 64), Image.Resampling.LANCZOS)
                return image
            else:
                return self.create_default_image()
        except:
            return self.create_default_image()
    
    def create_default_image(self):
        """기본 아이콘 생성"""
        from PIL import ImageDraw
        
        image = Image.new('RGB', (64, 64), color='black')
        dc = ImageDraw.Draw(image)
        dc.ellipse([8, 8, 56, 56], fill='green', outline='white', width=3)
        dc.text((20, 15), 'M', fill='white')
        
        return image
    
    def on_quit(self, icon, item):
        """종료"""
        self.running = False
        icon.stop()
        
        if self.on_exit_callback:
            self.on_exit_callback()
        
        os._exit(0)
    
    def create_menu(self):
        """메뉴 생성"""
        return Menu(
            MenuItem('GTA 매크로', lambda: None, enabled=False),
            MenuItem('종료', self.on_quit)
        )
    
    def run(self):
        """트레이 아이콘 실행"""
        self.icon = Icon(
            "GameMacro",
            self.load_icon_image(),
            "GTA 매크로",
            self.create_menu()
        )
        
        def run_icon():
            try:
                self.icon.run()
            except:
                pass
        
        threading.Thread(target=run_icon, daemon=True).start()
    
    def stop(self):
        """트레이 아이콘 중지"""
        if self.icon:
            self.icon.stop()