import keyboard
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from core import MacroCore
from handler import EventHandler
from tray import TrayIcon

class MacroApp:
    """매크로"""
    __slots__ = ('core', 'handler', 'tray', 'toggle_key', 'force_quit_keys')

    def __init__(self):
        self.core = MacroCore()
        self.handler = None
        self.tray = TrayIcon(self.on_exit)
        self.toggle_key = '`'
        self.force_quit_keys = ['alt', 'shift', 'delete']

    def on_exit(self):
        if self.handler:
            self.handler.shutdown()
    
    def _normalize_macros(self, raw_macros):
        """복수 트리거를 개별로 변환"""
        normalized = {}
        
        for trigger, info in raw_macros.items():
            if isinstance(trigger, tuple):
                # 튜플 트리거를 각 키로 분리
                for key in trigger:
                    normalized[key] = info  # 복사 없이 참조만
            else:
                normalized[trigger] = info
        
        return normalized
    
    def _parse_action(self, action, is_last, defaults):
        """action을 (hold, key, delay) 형식으로 변환"""
        action_len = len(action)
        
        if action_len == 1:
            # ('key',)
            return (defaults['press'], action[0], 0 if is_last else defaults['release'])
        
        elif action_len == 2:
            # 첫 번째가 숫자면 (hold, 'key'), 문자열이면 ('key', delay)
            if isinstance(action[0], (int, float)):
                return (action[0], action[1], 0 if is_last else defaults['release'])
            else:
                return (defaults['press'], action[0], action[1] if action[1] is not None else (0 if is_last else defaults['release']))
        
        else:  # action_len == 3
            # (hold, key, delay)
            return (
                action[0] if action[0] is not None else defaults['press'],
                action[1],
                action[2] if action[2] is not None else (0 if is_last else defaults['release'])
            )
    
    def _convert_actions(self, macros, defaults):
        """actions를 (hold, key, delay) 튜플 리스트로 변환"""
        converted = {}
        
        for key, info in macros.items():
            raw_actions = info['actions']
            parsed_actions = [
                self._parse_action(action, i == len(raw_actions) - 1, defaults)
                for i, action in enumerate(raw_actions)
            ]
            
            converted[key] = {
                'actions': parsed_actions,
                'mode': info['mode']
            }
        
        return converted
    
    def load_config(self, config):
        """설정 로드"""
        # 1. 복수 트리거 정규화
        normalized = self._normalize_macros(config.MACROS)
        
        # 2. actions 변환
        defaults = {
            'press': config.KEY_PRESS_DURATION,
            'release': config.KEY_RELEASE_DURATION,
            'sequence': config.SEQUENCE_DELAY
        }
        converted = self._convert_actions(normalized, defaults)
        
        # 3. 코어에 적용
        self.core.configure(converted, defaults)
        
        self.toggle_key = config.TOGGLE_KEY
        self.force_quit_keys = getattr(config, 'FORCE_QUIT_KEYS', ['alt', 'shift', 'delete'])
        self.handler = EventHandler(self.core, self.toggle_key, self.force_quit_keys)
    
    def setup_hooks(self):
        """키보드 훅 등록"""
        # 토글 키
        keyboard.on_press_key(self.toggle_key, self.handler.handle_press, suppress=True)
        keyboard.on_release_key(self.toggle_key, self.handler.handle_release, suppress=True)
        
        # 강제 종료 키
        for key in self.force_quit_keys:
            keyboard.on_press_key(key, self.handler.handle_press, suppress=False)
            keyboard.on_release_key(key, self.handler.handle_release, suppress=False)
        
        # 매크로 키
        for key in self.core.macros:
            keyboard.on_press_key(key, self.handler.handle_press, suppress=True)
            keyboard.on_release_key(key, self.handler.handle_release, suppress=True)
    
    def run(self):
        """실행"""
        self.tray.run()
        self.setup_hooks()
        print("=" * 60)
        print("KeyM 실행 중")
        print("=" * 60)
        print(f"토글 키: [{self.toggle_key}]")
        print(f"강제 종료: [{' + '.join(self.force_quit_keys).upper()}]")
        print(f"등록된 매크로: {len(self.core.macros)}개")
        print("=" * 60)
        keyboard.wait()
    
    def validate_config(self, cfg):
        """설정 검증"""
        # 필수 속성 체크
        required = ['MACROS', 'TOGGLE_KEY', 'KEY_PRESS_DURATION', 
                   'KEY_RELEASE_DURATION', 'SEQUENCE_DELAY']
        
        missing = [attr for attr in required if not hasattr(cfg, attr)]
        if missing:
            print(f"[오류] config.py에 필수 속성 누락: {', '.join(missing)}")
            return False
        
        # MACROS 검증
        if not isinstance(cfg.MACROS, dict) or not cfg.MACROS:
            print("[오류] MACROS가 비어있거나 올바르지 않습니다.")
            return False
        
        # 각 매크로 검증 (간소화)
        for trigger, info in cfg.MACROS.items():
            trigger_str = f"({', '.join(trigger)})" if isinstance(trigger, tuple) else f"'{trigger}'"
            
            # 기본 구조 체크
            if not isinstance(info, dict):
                print(f"[오류] {trigger_str}: 딕셔너리 형식 필요")
                return False
            
            # mode 체크
            if 'mode' not in info or info['mode'] not in [0, 1, 2]:
                print(f"[오류] {trigger_str}: mode는 0, 1, 2 중 하나")
                return False
            
            # actions 체크
            if 'actions' not in info:
                print(f"[오류] {trigger_str}: 'actions' 필드 누락")
                return False
            
            actions = info['actions']
            if not isinstance(actions, list) or not actions:
                print(f"[오류] {trigger_str}: actions는 비어있지 않은 리스트")
                return False
            
            # action 형식 간단 체크
            for i, action in enumerate(actions):
                if not isinstance(action, tuple) or not (1 <= len(action) <= 3):
                    print(f"[오류] {trigger_str}: action[{i}]는 1~3개 값의 튜플")
                    return False
        
        # 타이밍 검증
        for attr in ['KEY_PRESS_DURATION', 'KEY_RELEASE_DURATION', 'SEQUENCE_DELAY']:
            if getattr(cfg, attr, -1) < 0:
                print(f"[오류] {attr}는 0 이상이어야 함")
                return False
        
        print("설정 검증 완료")
        return True