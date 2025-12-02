import keyboard
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from core import macroCore
from handler import EventHandler
from tray import TrayIcon

class macroApp:
    """매크로 애플리케이션"""
    __slots__ = ('core', 'handler', 'tray', 'toggle_key')

    def __init__(self):
        self.core = macroCore()
        self.handler = None
        self.tray = TrayIcon(self.on_exit)
        self.toggle_key = '`'

    def on_exit(self):
        if self.handler:
            self.handler.shutdown()
    
    def load_config(self, config):
        """설정 로드"""
        self.core.configure(config.MACROS, {
            'press': config.KEY_PRESS_DURATION,
            'release': config.KEY_RELEASE_DURATION,
            'sequence': config.SEQUENCE_DELAY
        })
        self.toggle_key = config.TOGGLE_KEY
        self.handler = EventHandler(self.core, self.toggle_key)
    
    def setup_hooks(self):
        """키보드 훅 등록"""
        # 토글 키
        keyboard.on_press_key(self.toggle_key, self.handler.handle_press, suppress=True)
        keyboard.on_release_key(self.toggle_key, self.handler.handle_release, suppress=True)
        
        # 매크로 키 일괄 등록
        for key in self.core.macros:
            keyboard.on_press_key(key, self.handler.handle_press, suppress=True)
            keyboard.on_release_key(key, self.handler.handle_release, suppress=True)
    
    def run(self):
        """실행"""
        self.tray.run()
        self.setup_hooks()
        print("=" * 60)
        print("GThey5M 실행 중")
        print("=" * 60)
        print(f"토글 키: [{self.toggle_key}]")
        print(f"등록된 매크로: {len(self.core.macros)}개")
        print(f"매크로 연쇄: 허용")
        print(f"DirectInput: 활성화")
        print("=" * 60)
        print("종료: 트레이 아이콘 우클릭")
        print("=" * 60)
        keyboard.wait()
    
    def validate_config(self, cfg):
        """설정 검증"""
        required = ['MACROS', 'TOGGLE_KEY', 'KEY_PRESS_DURATION', 
                   'KEY_RELEASE_DURATION', 'SEQUENCE_DELAY']
        
        # 필수 속성 체크
        if not all(hasattr(cfg, attr) for attr in required):
            print("[오류] config.py에 필수 속성이 없습니다.")
            return False
        
        # MACROS 검증
        if not isinstance(cfg.MACROS, dict) or not cfg.MACROS:
            print("[오류] MACROS가 비어있거나 올바르지 않습니다.")
            return False
        
        # 각 매크로 검증
        for k, v in cfg.MACROS.items():
            if not isinstance(v, dict) or 'keys' not in v or 'mode' not in v:
                print(f"[오류] 매크로 '{k}': 필수 필드 누락 (keys, mode)")
                return False
            
            if v['mode'] not in [0, 1, 2]:
                print(f"[오류] 매크로 '{k}': mode는 0, 1, 2 중 하나여야 함")
                return False
            
            if not isinstance(v['keys'], list) or not v['keys']:
                print(f"[오류] 매크로 '{k}': keys는 비어있지 않은 리스트여야 함")
                return False
            
            # delays/holds 길이 체크
            if 'delays' in v and len(v['delays']) != len(v['keys']):
                print(f"[오류] 매크로 '{k}': delays 길이가 keys와 다름")
                return False
            
            if 'holds' in v and len(v['holds']) != len(v['keys']):
                print(f"[오류] 매크로 '{k}': holds 길이가 keys와 다름")
                return False
        
        # 타이밍 검증
        if any(getattr(cfg, attr) < 0 for attr in ['KEY_PRESS_DURATION', 
                                                     'KEY_RELEASE_DURATION', 
                                                     'SEQUENCE_DELAY']):
            print("[오류] 타이밍 설정은 음수일 수 없습니다.")
            return False
        
        print("설정 검증 완료")
        return True