import keyboard
import time
import threading
from typing import List, Dict, Optional

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
        
        # mode 2 전용: 실행 완료 이벤트
        self.mode2_events = {}  # {key: Event} - 실행 완료 대기용
        
        # 매크로 활성화 상태
        self.macro_enabled = True
        
        # 설정값
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
        
        # mode 2 매크로들의 완료 이벤트 미리 생성
        for key, macro_info in macros.items():
            if macro_info['mode'] == 2:
                self.mode2_events[key] = threading.Event()
                self.mode2_events[key].set()  # 초기값: 완료 상태
    
    def toggle_macro(self):
        """매크로 ON/OFF 토글"""
        self.macro_enabled = not self.macro_enabled
        
        # 매크로 비활성화 시 현재 실행중인 매크로 중단
        if not self.macro_enabled and self.is_running:
            self.stop_signal.set()
        
        status = "활성화" if self.macro_enabled else "비활성화"
        print(f"\n{'='*40}")
        print(f"매크로 {status}")
        print(f"{'='*40}\n")
        
        return self.macro_enabled
    
    def execute_key(self, key: str, delay: Optional[float] = None, hold: Optional[float] = None) -> bool:
        """단일 키 입력
        
        Args:
            key: 입력할 키
            delay: 키 입력 후 대기 시간 (None이면 기본값 사용)
            hold: 키를 누르고 있을 시간 (None이면 기본값 사용)
        """
        try:
            # 키 누르기
            keyboard.press(key)
            
            # 홀드 시간 (개별 지정 또는 기본값)
            hold_time = hold if hold is not None else self.timings['press']
            time.sleep(hold_time)
            
            # 키 떼기
            keyboard.release(key)
            
            # 딜레이 시간 (개별 지정 또는 기본값)
            wait_time = delay if delay is not None else self.timings['release']
            time.sleep(wait_time)
            
            return True
        except Exception as e:
            print(f"키 입력 실패 ({key}): {e}")
            return False
    
    def run_once(self, trigger: str, keys: List[str], delays: Optional[List[float]] = None,
                holds: Optional[List[float]] = None):
        """모드 2: 1회만 실행 (완료 보장)"""
        try:
            # 실행 시작 표시
            if trigger in self.mode2_events:
                self.mode2_events[trigger].clear()
            
            # 무조건 끝까지 실행
            for i, key in enumerate(keys):
                # 매크로 비활성화 확인만 함
                if not self.macro_enabled:
                    break
                
                # 해당 키에 대한 개별 딜레이와 홀드 시간
                delay = delays[i] if delays and i < len(delays) else None
                hold = holds[i] if holds and i < len(holds) else None
                
                if not self.execute_key(key, delay, hold):
                    break
            
        finally:
            # 실행 완료 표시
            if trigger in self.mode2_events:
                self.mode2_events[trigger].set()
            self._cleanup()
    
    def run_repeat(self, trigger: str, keys: List[str], delays: Optional[List[float]] = None,
                  holds: Optional[List[float]] = None):
        """모드 1: 연속 반복 실행"""
        try:
            while not self.stop_signal.is_set() and self.macro_enabled:
                # 트리거 키가 눌려있는지 확인
                if trigger not in self.pressed_keys:
                    break
                
                # 각 키 실행 (한 사이클)
                for i, key in enumerate(keys):
                    # 트리거 키 상태 확인
                    if trigger not in self.pressed_keys:
                        return
                    
                    # 해당 키에 대한 개별 딜레이와 홀드 시간
                    delay = delays[i] if delays and i < len(delays) else None
                    hold = holds[i] if holds and i < len(holds) else None
                    
                    # 키 실행
                    if not self.execute_key(key, delay, hold):
                        return
                
                # 루프 사이 딜레이 (0.01초)
                time.sleep(0.01)
                
        finally:
            self._cleanup()
    
    def start(self, trigger: str) -> bool:
        """매크로 시작"""
        # 매크로가 비활성화 상태면 무시
        if not self.macro_enabled:
            return False
        
        # 매크로 키가 아니면 무시
        if trigger not in self.macros:
            return False
        
        # 매크로 정보 가져오기
        macro_info = self.macros[trigger]
        mode = macro_info['mode']
        
        # mode가 0이면 비활성 매크로이므로 무시
        if mode == 0:
            return False
        
        # mode 2 전용 처리
        if mode == 2:
            # 실행 완료 대기 (이미 실행 중이면 여기서 블록됨)
            if trigger in self.mode2_events:
                if not self.mode2_events[trigger].is_set():
                    # 실행 중이므로 무시
                    return False
            
            # 실행
            keys = macro_info['keys']
            delays = macro_info.get('delays', None)
            holds = macro_info.get('holds', None)
            
            thread = threading.Thread(
                target=self.run_once,
                args=(trigger, keys, delays, holds),
                daemon=True
            )
            thread.start()
            return True
        
        # mode 1 처리
        with self.lock:
            # 이미 실행 중이면 무시
            if self.is_running:
                return False
            
            # 실행 상태 설정
            self.is_running = True
            self.current_macro = trigger
            self.stop_signal.clear()
        
        # 매크로 실행 정보
        keys = macro_info['keys']
        delays = macro_info.get('delays', None)
        holds = macro_info.get('holds', None)
        
        # 별도 스레드에서 실행
        thread = threading.Thread(
            target=self.run_repeat,
            args=(trigger, keys, delays, holds),
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