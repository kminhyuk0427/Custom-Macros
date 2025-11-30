import keyboard
import time
import threading
from typing import List, Dict

class MacroCore:
    """매크로 핵심 실행 엔진"""
    
    def __init__(self):
        # 실행 상태
        self.is_running = False
        self.current_macro = None
        self.stop_signal = threading.Event()
        self.lock = threading.Lock()
        
        # 키 상태 추적
        self.pressed_keys = set()
        
        # 설정값
        self.macros = {}
        self.timings = {
            'press': 0.01,
            'release': 0.01,
            'sequence': 0.02
        }
    
    def configure(self, macros: Dict, timings: Dict):
        """매크로 설정 적용"""
        self.macros = macros
        self.timings = timings
    
    def execute_key(self, key: str) -> bool:
        """단일 키 입력"""
        try:
            keyboard.press(key)
            time.sleep(self.timings['press'])
            keyboard.release(key)
            time.sleep(self.timings['release'])
            return True
        except Exception as e:
            print(f"키 입력 실패 ({key}): {e}")
            return False
    
    def execute_sequence(self, keys: List[str]) -> bool:
        """키 시퀀스 1회 실행"""
        for key in keys:
            if self.stop_signal.is_set():
                return False
            if not self.execute_key(key):
                return False
        return True
    
    def run_once(self, trigger: str, keys: List[str]):
        """모드 0: 1회만 실행"""
        try:
            self.execute_sequence(keys)
        finally:
            self._cleanup()
    
    def run_repeat(self, trigger: str, keys: List[str]):
        """모드 1: 연속 반복 실행"""
        try:
            while not self.stop_signal.is_set():
                # 트리거 키가 아직 눌려있는지 확인
                if trigger not in self.pressed_keys:
                    break
                
                # 시퀀스 실행
                if not self.execute_sequence(keys):
                    break
                
                # 다음 반복까지 대기
                time.sleep(self.timings['sequence'])
        finally:
            self._cleanup()
    
    def start(self, trigger: str) -> bool:
        """매크로 시작"""
        with self.lock:
            # 이미 실행 중이면 무시
            if self.is_running:
                return False
            
            # 매크로 키가 아니면 무시
            if trigger not in self.macros:
                return False
            
            # 실행 상태 설정
            self.is_running = True
            self.current_macro = trigger
            self.stop_signal.clear()
        
        # 매크로 정보 가져오기
        macro_info = self.macros[trigger]
        keys = macro_info['keys']
        mode = macro_info['mode']
        
        # 모드에 따라 실행 함수 선택
        runner = self.run_repeat if mode == 1 else self.run_once
        
        # 별도 스레드에서 실행
        thread = threading.Thread(
            target=runner,
            args=(trigger, keys),
            daemon=True
        )
        thread.start()
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