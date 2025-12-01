import keyboard
import os
import time
import threading

class EventHandler:
    """키보드 이벤트 핸들러"""
    
    def __init__(self, core, toggle_key='`'):
        self.core = core
        self.toggle_key = toggle_key
        self.blocked = set()  # 통합 차단 세트
    
    def get_base_key(self, event):
        """shift 조합 제거"""
        key = event.name
        shift_map = {'!':'1','@':'2','#':'3','$':'4','%':'5','^':'6','&':'7','*':'8','(':'9',')':'0'}
        return shift_map.get(key, key)
    
    def handle_press(self, event):
        """키 눌림 - False 반환 시 OS 입력 차단"""
        key = self.get_base_key(event)
        
        if key == self.toggle_key:
            self.core.toggle_macro()
            return False
        
        if not self.core.macro_enabled:
            return True
        
        if self.core.macros.get(key):
            # 이미 차단 중이면 무시
            if key in self.blocked:
                return False
            
            self.blocked.add(key)
            
            # mode 2는 추가 중복 방지
            if self.core.macros[key]['mode'] == 2:
                if key in self.core.mode2_events and not self.core.mode2_events[key].is_set():
                    return False
            
            # 중복 누름 방지
            if key in self.core.pressed_keys:
                return False
            
            self.core.pressed_keys.add(key)
            self.core.start(key)
            
            return False  # OS 입력 차단
        
        return True
    
    def handle_release(self, event):
        """키 떼기 - False 반환 시 OS 입력 차단"""
        key = self.get_base_key(event)
        
        if key == self.toggle_key:
            return False
        
        if not self.core.macro_enabled:
            return True
        
        if self.core.macros.get(key):
            self.core.pressed_keys.discard(key)
            
            mode = self.core.macros[key]['mode']
            
            if mode == 1:
                self.core.stop(key)
                self.blocked.discard(key)
            elif mode == 2:
                threading.Thread(target=lambda: (time.sleep(0.05), self.blocked.discard(key)), daemon=True).start()
            
            return False  # OS 입력 차단
        
        return True
    
    def shutdown(self):
        """종료"""
        self.core.stop_signal.set()
        try:
            keyboard.unhook_all()
        except:
            pass
        os._exit(0)