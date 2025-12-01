import keyboard
import time
import threading

class MacroCore:
    """매크로 핵심 실행 엔진"""
    
    def __init__(self):
        self.is_running = False
        self.current_macro = None
        self.stop_signal = threading.Event()
        self.pressed_keys = set()
        self.mode2_events = {}
        self.macro_enabled = True
        self.macros = {}
        self.timings = {'press': 0.01, 'release': 0.01, 'sequence': 0.001}
    
    def configure(self, macros, timings):
        """매크로 설정 적용"""
        self.macros = macros
        self.timings = timings
        
        for key, info in macros.items():
            if info['mode'] == 2:
                self.mode2_events[key] = threading.Event()
                self.mode2_events[key].set()
    
    def toggle_macro(self):
        """매크로 ON/OFF 토글"""
        self.macro_enabled = not self.macro_enabled
        if not self.macro_enabled and self.is_running:
            self.stop_signal.set()
        return self.macro_enabled
    
    def execute_key(self, key, delay=None, hold=None):
        """단일 키 입력"""
        keyboard.press(key)
        time.sleep(hold if hold else self.timings['press'])
        keyboard.release(key)
        time.sleep(delay if delay else self.timings['release'])
    
    def run_once(self, trigger, keys, delays, holds):
        """모드 2: 1회 실행"""
        if trigger in self.mode2_events:
            self.mode2_events[trigger].clear()
        
        try:
            for i, key in enumerate(keys):
                if not self.macro_enabled:
                    break
                self.execute_key(
                    key,
                    delays[i] if delays else None,
                    holds[i] if holds else None
                )
        finally:
            if trigger in self.mode2_events:
                self.mode2_events[trigger].set()
    
    def run_repeat(self, trigger, keys, delays, holds):
        """모드 1: 연속 반복"""
        try:
            while not self.stop_signal.is_set() and self.macro_enabled and trigger in self.pressed_keys:
                for i, key in enumerate(keys):
                    if trigger not in self.pressed_keys:
                        return
                    self.execute_key(
                        key,
                        delays[i] if delays else None,
                        holds[i] if holds else None
                    )
                time.sleep(self.timings['sequence'])
        finally:
            self.is_running = False
            self.current_macro = None
    
    def start(self, trigger):
        """매크로 시작"""
        if not self.macro_enabled or trigger not in self.macros:
            return False
        
        info = self.macros[trigger]
        mode = info['mode']
        
        if mode == 0:
            return False
        
        keys = info['keys']
        delays = info.get('delays')
        holds = info.get('holds')
        
        if mode == 2:
            if trigger in self.mode2_events and not self.mode2_events[trigger].is_set():
                return False
            threading.Thread(target=self.run_once, args=(trigger, keys, delays, holds), daemon=True).start()
            return True
        
        if self.is_running:
            return False
        
        self.is_running = True
        self.current_macro = trigger
        self.stop_signal.clear()
        
        threading.Thread(target=self.run_repeat, args=(trigger, keys, delays, holds), daemon=True).start()
        return True
    
    def stop(self, trigger):
        """매크로 중단"""
        if self.current_macro == trigger:
            self.stop_signal.set()