import sys
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

class TrayIcon:
    """시스템 트레이 아이콘 관리"""
    
    def __init__(self, on_exit_callback):
        """
        Args:
            on_exit_callback: 종료 시 호출할 콜백 함수
        """
        self.on_exit = on_exit_callback
        self.icon = None
        self.running = True
    
    def create_image(self):
        """트레이 아이콘 이미지 생성"""
        # 64x64 아이콘 생성
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='black')
        dc = ImageDraw.Draw(image)
        
        # 녹색 원 그리기 (매크로 활성 표시)
        dc.ellipse([8, 8, 56, 56], fill='green', outline='white', width=3)
        
        # 중앙에 'M' 글자
        dc.text((20, 15), 'M', fill='white')
        
        return image
    
    def on_quit(self, icon, item):
        """종료 메뉴 클릭"""
        self.running = False
        icon.stop()
        self.on_exit()
    
    def create_menu(self):
        """트레이 메뉴 생성"""
        return Menu(
            MenuItem('매크로 실행 중', lambda: None, enabled=False),
            MenuItem('종료', self.on_quit)
        )
    
    def run(self):
        """트레이 아이콘 실행"""
        self.icon = Icon(
            "GameMacro",
            self.create_image(),
            "게임 매크로 (실행 중)",
            self.create_menu()
        )
        
        # 별도 스레드에서 실행
        def run_icon():
            self.icon.run()
        
        icon_thread = threading.Thread(target=run_icon, daemon=False)
        icon_thread.start()
    
    def stop(self):
        """트레이 아이콘 중지"""
        if self.icon:
            self.icon.stop()