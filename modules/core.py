import keyboard
import time
import threading
from typing import List, Dict, Optional

class MacroCore:
    """매크로 핵심 실행 엔진"""
    
    def __init__(self):
        self.is_running = False
        self.current_macro = None
        self.stop_signal = threading.Event()
        self.lock = threading.Lock()
        self.pressed_keys = set()
        self.mode2_events = {}
        self.macro_enabled = True
        self.macros = {}
        self.timings = {
            'press': 0.01,
            'release': 0.01,
            'sequence': 0.001
        }
    
    def configure(self, macros: Dict, timings: Dict):
        """매크로 설정 적용"""
        self.macros = macros
        self.timings = timings
        
        for key, macro_info in macros.items():
            if macro_info['mode'] == 2:
                self.mode2_events[key] = threading.Event()
                self.mode2_events[key].set()
    
    def toggle_macro(self):
        """매크로 ON/OFF 토글"""
        self.macro_enabled = not self.macro_enabled
        
        if not self.macro_enabled and self.is_running:
            self.stop_signal.set()
        
        return self.macro_enabled
    
    def execute_key(self, key: str, delay: Optional[float] = None, hold: Optional[float] = None) -> bool:
        """단일 키 입력"""
        try:
            keyboard.press(key)
            time.sleep(hold if hold is not None else self.timings['press'])
            keyboard.release(key)
            time.sleep(delay if delay is not None else self.timings['release'])
            return True
        except:
            return False
    
    def run_once(self, trigger: str, keys: List[str], delays: Optional[List[float]] = None,
                holds: Optional[List[float]] = None):
        """모드 2: 1회만 실행"""
        try:
            if trigger in self.mode2_events:
                self.mode2_events[trigger].clear()
            
            for i, key in enumerate(keys):
                if not self.macro_enabled:
                    break
                
                delay = delays[i] if delays and i < len(delays) else None
                hold = holds[i] if holds and i < len(holds) else None
                
                if not self.execute_key(key, delay, hold):
                    break
            
        finally:
            if trigger in self.mode2_events:
                self.mode2_events[trigger].set()
            self._cleanup()
    
    def run_repeat(self, trigger: str, keys: List[str], delays: Optional[List[float]] = None,
                  holds: Optional[List[float]] = None):
        """모드 1: 연속 반복 실행"""
        try:
            while not self.stop_signal.is_set() and self.macro_enabled:
                if trigger not in self.pressed_keys:
                    break
                
                for i, key in enumerate(keys):
                    if trigger not in self.pressed_keys:
                        return
                    
                    delay = delays[i] if delays and i < len(delays) else None
                    hold = holds[i] if holds and i < len(holds) else None
                    
                    if not self.execute_key(key, delay, hold):
                        return
                
                time.sleep(self.timings['sequence'])
                
        finally:
            self._cleanup()
    
    def start(self, trigger: str) -> bool:
        """매크로 시작"""
        if not self.macro_enabled or trigger not in self.macros:
            return False
        
        macro_info = self.macros[trigger]
        mode = macro_info['mode']
        
        if mode == 0:
            return False
        
        if mode == 2:
            if trigger in self.mode2_events:
                if not self.mode2_events[trigger].is_set():
                    return False
            
            keys = macro_info['keys']
            delays = macro_info.get('delays', None)
            holds = macro_info.get('holds', None)
            
            threading.Thread(
                target=self.run_once,
                args=(trigger, keys, delays, holds),
                daemon=True
            ).start()
            return True
        
        with self.lock:
            if self.is_running:
                return False
            
            self.is_running = True
            self.current_macro = trigger
            self.stop_signal.clear()
        
        keys = macro_info['keys']
        delays = macro_info.get('delays', None)
        holds = macro_info.get('holds', None)
        
        threading.Thread(
            target=self.run_repeat,
            args=(trigger, keys, delays, holds),
            daemon=True
        ).start()
        return True
    
    def stop(self, trigger: str):
        """매크로 중단"""
        if self.current_macro == trigger:
            self.stop_signal.set()
    
    def _cleanup(self):
        """실행 종료 후 정리"""
        with self.lock:
            self.is_running = False
            self.current_macro = None
    
    def add_pressed_key(self, key: str):
        """눌린 키 추가"""
        self.pressed_keys.add(key)
    
    def remove_pressed_key(self, key: str):
        """눌린 키 제거"""
        self.pressed_keys.discard(key)
    
    def is_macro_key(self, key: str) -> bool:
        """매크로 트리거 키 확인"""
        return key in self.macros