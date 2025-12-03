import time
import threading
import os

class EventHandler:
    """키보드 이벤트 핸들러 (최적화 버전)"""
    __slots__ = ('core', 'toggle_key', 'blocked', 'shift_map', 
                 'force_quit_keys', 'pressed_force_quit')
    
    def __init__(self, core, toggle_key='`', force_quit_keys=None):
        self.core = core
        self.toggle_key = toggle_key
        self.blocked = set()
        
        # 강제 종료 키 조합
        self.force_quit_keys = set(force_quit_keys or ['alt', 'shift', 'delete'])
        self.pressed_force_quit = set()
        
        # Shift 맵 (캐싱을 위한 frozenset)
        self.shift_map = {
            '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', 
            '&': '7', '*': '8', '(': '9', ')': '0', '~': '`',
            'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'E': 'e', 'F': 'f',
            'G': 'g', 'H': 'h', 'I': 'i', 'J': 'j', 'K': 'k', 'L': 'l',
            'M': 'm', 'N': 'n', 'O': 'o', 'P': 'p', 'Q': 'q', 'R': 'r',
            'S': 's', 'T': 't', 'U': 'u', 'V': 'v', 'W': 'w', 'X': 'x',
            'Y': 'y', 'Z': 'z'
        }
    
    def get_base_key(self, event):
        """Shift 조합 제거 (최적화)"""
        return self.shift_map.get(event.name, event.name)
    
    def check_force_quit(self):
        """강제 종료 키 조합 확인"""
        return self.pressed_force_quit >= self.force_quit_keys
    
    def handle_press(self, event):
        """키 눌림 처리 (최적화)"""
        key = self.get_base_key(event)
        
        # 강제 종료 키 체크
        if key in self.force_quit_keys:
            self.pressed_force_quit.add(key)
            if self.check_force_quit():
                print("강제 종료 키 조합 감지 - 프로그램 종료 중...")
                self.shutdown()
                return False
        
        # 토글 키
        if key == self.toggle_key:
            self.core.toggle_macro()
            return False
        
        # 매크로 비활성화 시 조기 종료
        if not self.core.macro_enabled or key not in self.core.macros:
            return True
        
        # 다른 매크로가 이 키를 실행 중이면 트리거만 차단
        if self.core.should_block_trigger(key):
            return True
        
        # 이미 차단 중이면 무시
        if key in self.blocked:
            return False
        
        # 사용자가 직접 누른 경우 체크
        if key in self.core.user_trigger_keys:
            return False
        
        # mode 2 중복 방지
        info = self.core.macros[key]
        if info['mode'] == 2:
            event_obj = self.core.mode2_events.get(key)
            if event_obj and not event_obj.is_set():
                return False
        
        # 중복 누름 방지
        if key in self.core.pressed_keys:
            return False
        
        # 사용자가 직접 누른 트리거로 표시
        self.core.user_trigger_keys.add(key)
        self.blocked.add(key)
        self.core.pressed_keys.add(key)
        self.core.start(key)
        
        return False
    
    def handle_release(self, event):
        """키 떼기 처리 (최적화)"""
        key = self.get_base_key(event)
        
        # 강제 종료 키 해제
        if key in self.force_quit_keys:
            self.pressed_force_quit.discard(key)
        
        # 토글 키
        if key == self.toggle_key:
            return False
        
        # 매크로 비활성화 시 조기 종료
        if not self.core.macro_enabled or key not in self.core.macros:
            return True
        
        # 다른 매크로가 이 키를 실행 중이면 release도 통과
        if self.core.should_block_trigger(key):
            return True
        
        # 사용자가 직접 누른 키만 처리
        if key not in self.core.user_trigger_keys:
            return False
        
        # 사용자 트리거 기록 제거
        self.core.user_trigger_keys.discard(key)
        self.core.pressed_keys.discard(key)
        
        mode = self.core.macros[key]['mode']
        
        if mode == 1:
            # mode 1: 즉시 중단
            self.core.stop(key)
            self.blocked.discard(key)
        elif mode == 2:
            # mode 2: 지연 후 차단 해제 (최적화된 방식)
            threading.Timer(0.05, lambda: self.blocked.discard(key)).start()
        
        return False
    
    def shutdown(self):
        """종료 (최적화)"""
        self.core.stop_signal.set()
        try:
            import keyboard
            keyboard.unhook_all()
        except:
            pass
        finally:
            os._exit(0)