import os

class EventHandler:
    """키보드 이벤트 핸들러"""
    __slots__ = ('core', 'toggle_key', 'blocked', 'force_quit_keys', 'pressed_force_quit')
    
    # Shift 키 매핑 (중복 제거)
    SHIFT_MAP = {
        # 숫자 키 Shift
        '!': '1', '@': '2', '#': '3', '$': '4', '%': '5',
        '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
        
        # 기호 키 Shift
        '~': '`', '_': '-', '+': '=', '{': '[', '}': ']',
        '|': '\\', ':': ';', '"': "'", '<': ',', '>': '.', '?': '/',
        
        # 대문자 -> 소문자
        'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'E': 'e', 'F': 'f',
        'G': 'g', 'H': 'h', 'I': 'i', 'J': 'j', 'K': 'k', 'L': 'l',
        'M': 'm', 'N': 'n', 'O': 'o', 'P': 'p', 'Q': 'q', 'R': 'r',
        'S': 's', 'T': 't', 'U': 'u', 'V': 'v', 'W': 'w', 'X': 'x',
        'Y': 'y', 'Z': 'z',
    }
    
    # 넘버패드 키 매핑
    NUMPAD_MAP = {
        'keypad 0': 'num0', 'keypad 1': 'num1', 'keypad 2': 'num2',
        'keypad 3': 'num3', 'keypad 4': 'num4', 'keypad 5': 'num5',
        'keypad 6': 'num6', 'keypad 7': 'num7', 'keypad 8': 'num8',
        'keypad 9': 'num9', 'keypad /': 'num/', 'keypad *': 'num*',
        'keypad -': 'num-', 'keypad +': 'num+', 'keypad .': 'num.',
        'keypad enter': 'numenter',
    }
    
    def __init__(self, core, toggle_key='`', force_quit_keys=None):
        self.core = core
        self.toggle_key = toggle_key
        self.blocked = set()
        self.force_quit_keys = set(force_quit_keys or ['alt', 'shift', 'delete'])
        self.pressed_force_quit = set()
    
    def _normalize_key(self, key_name):
        """키 이름 정규화 (간소화)"""
        # 1. 넘버패드 체크
        numpad = self.NUMPAD_MAP.get(key_name)
        if numpad:
            return numpad
        
        # 2. Shift 변환 체크
        shift = self.SHIFT_MAP.get(key_name)
        if shift:
            return shift
        
        # 3. 그대로 반환
        return key_name
    
    def handle_press(self, event):
        """키 눌림"""
        key = self._normalize_key(event.name)
        
        # 1. 강제 종료 체크
        if key in self.force_quit_keys:
            self.pressed_force_quit.add(key)
            if self.pressed_force_quit >= self.force_quit_keys:
                print("강제 종료 중...")
                self.shutdown()
                return False
        
        # 2. 토글 키
        if key == self.toggle_key:
            self.core.toggle_macro()
            return False
        
        # 3. 매크로 비활성 또는 미등록 키
        if not self.core.macro_enabled or key not in self.core.macros:
            return True
        
        # 4. 실행 중인 매크로 차단
        if key in self.core.executing_keys:
            return True
        
        # 5. 이미 차단된 키
        if key in self.blocked:
            return False
        
        # 6. 사용자가 이미 누른 키
        if key in self.core.user_triggers:
            return False
        
        # 7. mode 2 중복 실행 방지
        info = self.core.macros[key]
        if info['mode'] == 2:
            event_obj = self.core.mode2_events.get(key)
            if event_obj and not event_obj.is_set():
                return False
        
        # 8. 중복 눌림 방지
        if key in self.core.pressed_keys:
            return False
        
        # 9. 매크로 시작
        self.core.user_triggers.add(key)
        self.blocked.add(key)
        self.core.pressed_keys.add(key)
        self.core.start(key)
        
        return False
    
    def handle_release(self, event):
        """키 떼기"""
        key = self._normalize_key(event.name)
        
        # 1. 강제 종료 키 해제
        if key in self.force_quit_keys:
            self.pressed_force_quit.discard(key)
        
        # 2. 토글 키
        if key == self.toggle_key:
            return False
        
        # 3. 매크로 비활성 또는 미등록 키
        if not self.core.macro_enabled or key not in self.core.macros:
            return True
        
        # 4. 실행 중인 매크로 차단
        if key in self.core.executing_keys:
            return True
        
        # 5. 사용자가 누른 키가 아님
        if key not in self.core.user_triggers:
            return False
        
        # 6. 상태 정리
        self.core.user_triggers.discard(key)
        self.core.pressed_keys.discard(key)
        
        mode = self.core.macros[key]['mode']
        
        if mode == 1:
            # mode 1: 즉시 중단 및 차단 해제
            self.core.stop(key)
            self.blocked.discard(key)
        else:
            # mode 2: 50ms 후 차단 해제
            import threading
            threading.Timer(0.05, self.blocked.discard, args=(key,)).start()
        
        return False
    
    def shutdown(self):
        """종료"""
        self.core.stop_signal.set()
        
        # 모든 타이머 취소
        for timer in list(self.core._cleanup_timers.values()):
            try:
                timer.cancel()
            except:
                pass
        
        try:
            import keyboard
            keyboard.unhook_all()
        except:
            pass
        finally:
            os._exit(0)