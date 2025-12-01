import keyboard
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from core import MacroCore
from handler import EventHandler
from tray import TrayIcon

class MacroApp:
    """매크로 애플리케이션"""
    
    def __init__(self):
        self.core = MacroCore()
        self.handler = None
        self.tray = TrayIcon(self.on_exit)
        self.toggle_key = '`'
    
    def on_exit(self):
        if self.handler:
            self.handler.shutdown()
    
    def load_config(self, config):
        """설정 로드"""
        self.core.configure(
            config.MACROS,
            {
                'press': config.KEY_PRESS_DURATION,
                'release': config.KEY_RELEASE_DURATION,
                'sequence': config.SEQUENCE_DELAY
            }
        )
        self.toggle_key = config.TOGGLE_KEY
        self.handler = EventHandler(self.core, self.toggle_key)
    
    def setup_hooks(self):
        """키보드 후킹"""
        # 토글 키
        keyboard.on_press_key(self.toggle_key, self.handler.handle_press, suppress=True)
        keyboard.on_release_key(self.toggle_key, self.handler.handle_release, suppress=True)
        
        # 매크로 키
        for key in self.core.macros:
            keyboard.on_press_key(key, self.handler.handle_press, suppress=True)
            keyboard.on_release_key(key, self.handler.handle_release, suppress=True)
    
    def run(self):
        """실행"""
        self.tray.run()
        self.setup_hooks()
        print("GTA 매크로 실행 중")
        print(f"토글: [{self.toggle_key}] | 종료: 트레이 우클릭")
        keyboard.wait()
    
    def validate_config(self, cfg):
        """설정 검증"""
        if not hasattr(cfg, 'MACROS') or not isinstance(cfg.MACROS, dict) or not cfg.MACROS:
            return False
        if not hasattr(cfg, 'TOGGLE_KEY') or not isinstance(cfg.TOGGLE_KEY, str):
            return False
        
        for k, v in cfg.MACROS.items():
            if not isinstance(v, dict) or 'keys' not in v or 'mode' not in v:
                return False
            if v['mode'] not in [0,1,2]:
                return False
            if not isinstance(v['keys'], list) or not v['keys']:
                return False
            if 'delays' in v and len(v['delays']) != len(v['keys']):
                return False
            if 'holds' in v and len(v['holds']) != len(v['keys']):
                return False
        
        return (hasattr(cfg, 'KEY_PRESS_DURATION') and cfg.KEY_PRESS_DURATION >= 0 and
                hasattr(cfg, 'KEY_RELEASE_DURATION') and cfg.KEY_RELEASE_DURATION >= 0 and
                hasattr(cfg, 'SEQUENCE_DELAY') and cfg.SEQUENCE_DELAY >= 0)