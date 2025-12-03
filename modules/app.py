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
                for key in trigger:
                    normalized[key] = info.copy()
            else:
                normalized[trigger] = info.copy()
        
        return normalized
    
    def _parse_action(self, action, is_last):
        """action을 (hold, key, delay) 형식으로 변환
        
        입력:
            ('key',)              → (기본홀드, 'key', 마지막이면 0 아니면 기본딜레이)
            ('key', delay)        → (기본홀드, 'key', delay)
            (hold, 'key')         → (hold, 'key', 마지막이면 0 아니면 기본딜레이)
            (hold, 'key', delay)  → (hold, 'key', delay)
        """
        action_len = len(action)
        
        if action_len == 1:
            # ('key',)
            return (None, action[0], 0 if is_last else None)
        
        elif action_len == 2:
            # 첫 번째가 숫자면 (hold, 'key'), 문자열이면 ('key', delay)
            if isinstance(action[0], (int, float)):
                # (hold, 'key')
                hold = action[0]
                key = action[1]
                delay = 0 if is_last else None
                return (hold, key, delay)
            else:
                # ('key', delay)
                key = action[0]
                delay = action[1] if action[1] is not None else (0 if is_last else None)
                return (None, key, delay)
        
        elif action_len == 3:
            # (hold, 'key', delay)
            hold = action[0]
            key = action[1]
            delay = action[2] if action[2] is not None else (0 if is_last else None)
            return (hold, key, delay)
        
        else:
            raise ValueError(f"잘못된 action 형식: {action}")
    
    def _convert_actions(self, macros, defaults):
        """actions를 (hold, key, delay) 튜플 리스트로 변환"""
        converted = {}
        
        for key, info in macros.items():
            if 'actions' not in info:
                raise ValueError(f"매크로 '{key}': 'actions' 필드 필요")
            
            raw_actions = info['actions']
            parsed_actions = []
            
            for i, action in enumerate(raw_actions):
                is_last = (i == len(raw_actions) - 1)
                hold, key_name, delay = self._parse_action(action, is_last)
                
                # None을 기본값으로 치환
                hold = hold if hold is not None else defaults['press']
                delay = delay if delay is not None else defaults['release']
                
                parsed_actions.append((hold, key_name, delay))
            
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
        required = ['MACROS', 'TOGGLE_KEY', 'KEY_PRESS_DURATION', 
                   'KEY_RELEASE_DURATION', 'SEQUENCE_DELAY']
        
        missing = [attr for attr in required if not hasattr(cfg, attr)]
        if missing:
            print(f"[오류] config.py에 필수 속성 누락: {', '.join(missing)}")
            return False
        
        if not isinstance(cfg.MACROS, dict) or not cfg.MACROS:
            print("[오류] MACROS가 비어있거나 올바르지 않습니다.")
            return False
        
        # 각 매크로 검증
        for trigger, info in cfg.MACROS.items():
            # 트리거 형식
            if isinstance(trigger, tuple):
                trigger_str = f"({', '.join(trigger)})"
                if not all(isinstance(k, str) for k in trigger):
                    print(f"[오류] {trigger_str}: 트리거는 문자열이어야 함")
                    return False
            elif not isinstance(trigger, str):
                print(f"[오류] '{trigger}': 트리거는 문자열 또는 튜플이어야 함")
                return False
            else:
                trigger_str = f"'{trigger}'"
            
            if not isinstance(info, dict):
                print(f"[오류] {trigger_str}: 딕셔너리 형식 필요")
                return False
            
            # mode 체크
            if 'mode' not in info:
                print(f"[오류] {trigger_str}: 'mode' 필드 누락")
                return False
            
            if info['mode'] not in [0, 1, 2]:
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
            
            for i, action in enumerate(actions):
                if not isinstance(action, tuple) or len(action) < 1 or len(action) > 3:
                    print(f"[오류] {trigger_str}: action[{i}]는 1~3개 값의 튜플")
                    return False
                
                # 2개 값: (hold, 'key') 또는 ('key', delay)
                if len(action) == 2:
                    first, second = action
                    
                    # (hold, 'key') 형식
                    if isinstance(first, (int, float)):
                        if not isinstance(second, str):
                            print(f"[오류] {trigger_str}: action[{i}] (hold, 'key') 형식에서 key는 문자열")
                            return False
                        if first < 0:
                            print(f"[오류] {trigger_str}: action[{i}] hold는 0 이상")
                            return False
                    
                    # ('key', delay) 형식
                    else:
                        if not isinstance(first, str):
                            print(f"[오류] {trigger_str}: action[{i}] key는 문자열")
                            return False
                        if second is not None and (not isinstance(second, (int, float)) or second < 0):
                            print(f"[오류] {trigger_str}: action[{i}] delay는 None 또는 0 이상")
                            return False
                
                # 3개 값: (hold, 'key', delay)
                elif len(action) == 3:
                    hold, key, delay = action
                    if not isinstance(key, str):
                        print(f"[오류] {trigger_str}: action[{i}] 키는 문자열")
                        return False
                    if hold is not None and (not isinstance(hold, (int, float)) or hold < 0):
                        print(f"[오류] {trigger_str}: action[{i}] hold는 None 또는 0 이상")
                        return False
                    if delay is not None and (not isinstance(delay, (int, float)) or delay < 0):
                        print(f"[오류] {trigger_str}: action[{i}] delay는 None 또는 0 이상")
                        return False
        
        # 타이밍 검증
        timing_attrs = ['KEY_PRESS_DURATION', 'KEY_RELEASE_DURATION', 'SEQUENCE_DELAY']
        for attr in timing_attrs:
            val = getattr(cfg, attr, -1)
            if val < 0:
                print(f"[오류] {attr}는 0 이상이어야 함")
                return False
        
        print("설정 검증 완료")
        return True