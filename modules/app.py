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
        """프로그램 종료"""
        if self.handler:
            self.handler.shutdown()
    
    def load_config(self, config):
        """설정 로드"""
        timings = {
            'press': config.KEY_PRESS_DURATION,
            'release': config.KEY_RELEASE_DURATION,
            'sequence': config.SEQUENCE_DELAY
        }
        
        self.toggle_key = config.TOGGLE_KEY
        
        self.core.configure(
            macros=config.MACROS,
            timings=timings
        )
        
        self.handler = EventHandler(self.core, self.toggle_key)
    
    def setup_hooks(self):
        """키보드 후킹 설정"""
        keyboard.on_press_key(
            self.toggle_key,
            self.handler.handle_press,
            suppress=True
        )
        keyboard.on_release_key(
            self.toggle_key,
            self.handler.handle_release,
            suppress=True
        )
        
        for macro_key in self.core.macros.keys():
            keyboard.on_press_key(
                macro_key,
                self.handler.handle_press,
                suppress=True
            )
            keyboard.on_release_key(
                macro_key,
                self.handler.handle_release,
                suppress=True
            )
    
    def run(self):
        """애플리케이션 실행"""
        self.tray.run()
        self.setup_hooks()
        
        print("========================================")
        print("GTA 매크로 실행 중")
        print("========================================")
        print(f"토글: [{self.toggle_key}]")
        print(f"상태: {'활성화' if self.core.macro_enabled else '비활성화'}")
        print("종료: 트레이 아이콘 우클릭 - 종료")
        print("========================================")
        
        keyboard.wait()
    
    def validate_config(self, config) -> bool:
        """설정 검증"""
        if not hasattr(config, 'MACROS') or not config.MACROS:
            return False
        
        if not isinstance(config.MACROS, dict):
            return False
        
        if not hasattr(config, 'TOGGLE_KEY'):
            return False
        
        for key, macro_info in config.MACROS.items():
            if not isinstance(macro_info, dict):
                return False
            
            if 'keys' not in macro_info or 'mode' not in macro_info:
                return False
            
            if macro_info['mode'] not in [0, 1, 2]:
                return False
            
            if not isinstance(macro_info['keys'], list) or not macro_info['keys']:
                return False
            
            if 'delays' in macro_info:
                delays = macro_info['delays']
                if not isinstance(delays, list):
                    return False
                if len(delays) != len(macro_info['keys']):
                    return False
            
            if 'holds' in macro_info:
                holds = macro_info['holds']
                if not isinstance(holds, list):
                    return False
                if len(holds) != len(macro_info['keys']):
                    return False
        
        if not hasattr(config, 'KEY_PRESS_DURATION') or config.KEY_PRESS_DURATION < 0:
            return False
        
        if not hasattr(config, 'KEY_RELEASE_DURATION') or config.KEY_RELEASE_DURATION < 0:
            return False
        
        if not hasattr(config, 'SEQUENCE_DELAY') or config.SEQUENCE_DELAY < 0:
            return False
        
        return True