import time
import threading
import ctypes
from ctypes import c_ulong, c_ushort, c_long, Structure, Union, POINTER, windll

# DirectInput 구조체
PUL = POINTER(c_ulong)

class KeyBdInput(Structure):
    _fields_ = [("wVk", c_ushort), ("wScan", c_ushort), ("dwFlags", c_ulong), 
                ("time", c_ulong), ("dwExtraInfo", PUL)]

class HardwareInput(Structure):
    _fields_ = [("uMsg", c_ulong), ("wParamL", c_ushort), ("wParamH", c_ushort)]

class MouseInput(Structure):
    _fields_ = [("dx", c_long), ("dy", c_long), ("mouseData", c_ulong), 
                ("dwFlags", c_ulong), ("time", c_ulong), ("dwExtraInfo", PUL)]

class Input_I(Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]

class Input(Structure):
    _fields_ = [("type", c_ulong), ("ii", Input_I)]

SendInput = windll.user32.SendInput

# 스캔코드 맵
SCANCODE_MAP = {
    '0': 0x0B, '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06, 
    '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A,
    'q': 0x10, 'w': 0x11, 'e': 0x12, 'r': 0x13, 't': 0x14, 'y': 0x15, 
    'u': 0x16, 'i': 0x17, 'o': 0x18, 'p': 0x19,
    'a': 0x1E, 's': 0x1F, 'd': 0x20, 'f': 0x21, 'g': 0x22, 'h': 0x23, 
    'j': 0x24, 'k': 0x25, 'l': 0x26,
    'z': 0x2C, 'x': 0x2D, 'c': 0x2E, 'v': 0x2F, 'b': 0x30, 'n': 0x31, 'm': 0x32,
    'up': 0xC8, 'down': 0xD0, 'left': 0xCB, 'right': 0xCD,
    'space': 0x39, 'enter': 0x1C, 'shift': 0x2A, 'ctrl': 0x1D, 'alt': 0x38, 
    'tab': 0x0F, 'esc': 0x01, 'backspace': 0x0E,
    'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E, 'f5': 0x3F, 'f6': 0x40, 
    'f7': 0x41, 'f8': 0x42, 'f9': 0x43, 'f10': 0x44, 'f11': 0x57, 'f12': 0x58,
}

EXTENDED_KEYS = frozenset({'up', 'down', 'left', 'right'})

# 플래그
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

class macroCore:
    """매크로 코어"""
    __slots__ = ('is_running', 'current_macro', 'stop_signal', 'pressed_keys', 
                 'mode2_events', 'macro_enabled', 'macros', 'timings', 
                 '_extra', '_input_cache', 'user_trigger_keys', 'macro_executing')
    
    def __init__(self):
        self.is_running = False
        self.current_macro = None
        self.stop_signal = threading.Event()
        self.pressed_keys = set()
        self.mode2_events = {}
        self.macro_enabled = True
        self.macros = {}
        self.timings = {'press': 0.05, 'release': 0.03, 'sequence': 0.01}
        self._extra = c_ulong(0)
        self._input_cache = {}
        
        # 사용자가 직접 누른 트리거 키 추적
        self.user_trigger_keys = set()
        
        # 매크로 실행 중 플래그
        self.macro_executing = threading.Lock()
    
    def configure(self, macros, timings):
        self.macros = macros
        self.timings = timings
        
        for key, info in macros.items():
            if info['mode'] == 2:
                self.mode2_events[key] = threading.Event()
                self.mode2_events[key].set()
    
    def toggle_macro(self):
        self.macro_enabled = not self.macro_enabled
        if not self.macro_enabled and self.is_running:
            self.stop_signal.set()
        return self.macro_enabled
    
    def _send_input(self, scan_code, is_extended, is_keyup):
        """DirectInput"""
        flags = KEYEVENTF_SCANCODE
        if is_extended:
            flags |= KEYEVENTF_EXTENDEDKEY
        if is_keyup:
            flags |= KEYEVENTF_KEYUP
        
        cache_key = (scan_code, flags)
        if cache_key not in self._input_cache:
            ii = Input_I()
            ii.ki = KeyBdInput(0, scan_code, flags, 0, POINTER(c_ulong)(self._extra))
            self._input_cache[cache_key] = Input(c_ulong(1), ii)
        
        SendInput(1, ctypes.pointer(self._input_cache[cache_key]), ctypes.sizeof(Input))
    
    def execute_key(self, key, delay=None, hold=None):
        """단일 키 실행"""
        key_lower = key.lower()
        
        if key_lower not in SCANCODE_MAP:
            return
        
        scan_code = SCANCODE_MAP[key_lower]
        is_extended = key_lower in EXTENDED_KEYS
        
        # 키 누르기
        self._send_input(scan_code, is_extended, False)
        time.sleep(hold if hold is not None else self.timings['press'])
        
        # 키 떼기 (Extended Key는 KEYUP에도 플래그 필요)
        self._send_input(scan_code, is_extended, True)
        time.sleep(delay if delay is not None else self.timings['release'])
    
    def run_once(self, trigger, keys, delays, holds):
        """모드 2: 1회 실행"""
        event = self.mode2_events.get(trigger)
        if event:
            event.clear()
        
        try:
            for i, key in enumerate(keys):
                if not self.macro_enabled:
                    break
                self.execute_key(key, delays[i] if delays else None, 
                               holds[i] if holds else None)
        finally:
            if event:
                event.set()
    
    def run_repeat(self, trigger, keys, delays, holds):
        """모드 1: 연속 반복"""
        try:
            while (not self.stop_signal.is_set() and self.macro_enabled and 
                   trigger in self.pressed_keys):
                for i, key in enumerate(keys):
                    if trigger not in self.pressed_keys:
                        return
                    self.execute_key(key, delays[i] if delays else None, 
                                   holds[i] if holds else None)
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
            event = self.mode2_events.get(trigger)
            if event and not event.is_set():
                return False
            threading.Thread(target=self.run_once, args=(trigger, keys, delays, holds), 
                           daemon=True).start()
            return True
        
        if self.is_running:
            return False
        
        self.is_running = True
        self.current_macro = trigger
        self.stop_signal.clear()
        threading.Thread(target=self.run_repeat, args=(trigger, keys, delays, holds), 
                       daemon=True).start()
        return True
    
    def stop(self, trigger):
        """매크로 중단"""
        if self.current_macro == trigger:
            self.stop_signal.set()