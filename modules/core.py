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
    'tab': 0x0F, 'esc': 0x01, 'backspace': 0x0E, 'delete': 0xD3,
    'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E, 'f5': 0x3F, 'f6': 0x40, 
    'f7': 0x41, 'f8': 0x42, 'f9': 0x43, 'f10': 0x44, 'f11': 0x57, 'f12': 0x58,
}

# Extended 키
EXTENDED_KEYS = frozenset({'up', 'down', 'left', 'right', 'delete'})

# 플래그
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

class MacroCore:
    """매크로 코어"""
    __slots__ = ('macro_enabled', 'macros', 'timings', 'mode2_events',
                 'pressed_keys', 'executing_keys', 'user_triggers',
                 'is_running', 'current_macro', 'stop_signal',
                 '_extra', '_input_cache')
    
    def __init__(self):
        self.macro_enabled = True
        self.macros = {}
        self.timings = {'press': 0.02, 'release': 0.02, 'sequence': 0.02}
        self.mode2_events = {}
        
        # 키 추적 (set 사용으로 O(1) 조회)
        self.pressed_keys = set()
        self.executing_keys = set()
        self.user_triggers = set()
        
        # mode 1 상태
        self.is_running = False
        self.current_macro = None
        self.stop_signal = threading.Event()
        
        # DirectInput 캐싱
        self._extra = c_ulong(0)
        self._input_cache = {}
    
    def configure(self, macros, timings):
        """설정 적용"""
        self.macros = macros
        self.timings = timings
        
        # mode 2 이벤트 초기화
        for key, info in macros.items():
            if info['mode'] == 2:
                self.mode2_events[key] = threading.Event()
                self.mode2_events[key].set()
    
    def toggle_macro(self):
        """매크로 토글"""
        self.macro_enabled = not self.macro_enabled
        if not self.macro_enabled and self.is_running:
            self.stop_signal.set()
        return self.macro_enabled
    
    def _send_input(self, scan_code, is_extended, is_keyup):
        """DirectInput 전송"""
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
    
    def _interruptible_sleep(self, duration, trigger_key):
        """중단 가능한 sleep (mode 1)"""
        if duration <= 0:
            return True
        
        end_time = time.perf_counter() + duration
        while time.perf_counter() < end_time:
            if trigger_key not in self.pressed_keys or not self.macro_enabled:
                return False
            time.sleep(0.001)  # 1ms 체크
        
        return True
    
    def _execute_key(self, key, trigger_key, hold, delay, mode):
        """단일 키 실행
        
        순서:
        1. 키 누르기
        2. hold초 대기
        3. 키 떼기
        4. delay초 대기
        """
        key_lower = key.lower()
        scan_code = SCANCODE_MAP.get(key_lower)
        
        if scan_code is None:
            return True
        
        # 트리거 키는 실행하지 ㄴㄴ
        if key_lower == trigger_key:
            if delay and delay > 0:
                if mode == 1:
                    return self._interruptible_sleep(delay, trigger_key)
                else:
                    time.sleep(delay)
            return True
        
        is_extended = key_lower in EXTENDED_KEYS
        is_macro_trigger = key_lower in self.macros
        
        # 매크로 트리거면 실행 목록 추가
        if is_macro_trigger:
            self.executing_keys.add(key_lower)
        
        try:
            # 1. 키 누름
            self._send_input(scan_code, is_extended, False)
            
            # 2. hold 대기
            if mode == 1:
                if not self._interruptible_sleep(hold, trigger_key):
                    self._send_input(scan_code, is_extended, True)
                    return False
            else:
                time.sleep(hold)
            
            # 3. 키 떼기
            self._send_input(scan_code, is_extended, True)
            
            # 4. delay 대기
            if delay and delay > 0:
                if mode == 1:
                    if not self._interruptible_sleep(delay, trigger_key):
                        return False
                else:
                    time.sleep(delay)
            
            return True
        
        finally:
            if is_macro_trigger:
                # 실행 목록에서 제거
                threading.Timer(0.15, lambda: self.executing_keys.discard(key_lower)).start()
    
    def _run_once(self, trigger, actions):
        """mode 2: 1회 실행"""
        event = self.mode2_events.get(trigger)
        if event:
            event.clear()
        
        try:
            for hold, key, delay in actions:
                self._execute_key(key, trigger, hold, delay, mode=2)
        finally:
            if event:
                event.set()
    
    def _run_repeat(self, trigger, actions):
        """mode 1: 연속 반복"""
        try:
            while (not self.stop_signal.is_set() and 
                   self.macro_enabled and 
                   trigger in self.pressed_keys):
                
                for hold, key, delay in actions:
                    if trigger not in self.pressed_keys:
                        return
                    
                    if not self._execute_key(key, trigger, hold, delay, mode=1):
                        return
                
                # 시퀀스 간 딜레이
                if not self._interruptible_sleep(self.timings['sequence'], trigger):
                    return
        finally:
            self.is_running = False
            self.current_macro = None
    
    def start(self, trigger):
        """매크로 시작"""
        if not self.macro_enabled:
            return False
        
        info = self.macros.get(trigger)
        if not info or info['mode'] == 0:
            return False
        
        actions = info['actions']
        mode = info['mode']
        
        if mode == 2:
            event = self.mode2_events.get(trigger)
            if event and not event.is_set():
                return False
            
            threading.Thread(
                target=self._run_once,
                args=(trigger, actions),
                daemon=True
            ).start()
            return True
        
        # mode 1
        if self.is_running:
            return False
        
        self.is_running = True
        self.current_macro = trigger
        self.stop_signal.clear()
        
        threading.Thread(
            target=self._run_repeat,
            args=(trigger, actions),
            daemon=True
        ).start()
        return True
    
    def stop(self, trigger):
        """매크로 중단"""
        if self.current_macro == trigger:
            self.stop_signal.set()
    
    def should_block_trigger(self, key):
        """트리거 차단 확인"""
        return key in self.executing_keys