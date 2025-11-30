import keyboard
import sys
import os

class EventHandler:
    """키보드 이벤트 핸들러"""
    
    def __init__(self, core):
        """
        Args:
            core: MacroCore 인스턴스
        """
        self.core = core
        self.running = True
    
    def handle_press(self, event) -> bool:
        """키 눌림 처리
        
        Returns:
            False를 반환하면 키 입력 차단
        """
        key = event.name
        
        # ESC 키 처리
        if key == 'esc':
            self.shutdown()
            return True
        
        # 매크로 키인 경우 무조건 차단
        if self.core.is_macro_key(key):
            # 이미 눌린 키면 무시 (연속 입력 방지)
            if key in self.core.pressed_keys:
                return False  # 입력 차단
            
            # 키 상태 기록
            self.core.add_pressed_key(key)
            
            # 매크로 시작
            self.core.start(key)
            return False  # 트리거 키 입력 차단
        
        # 일반 키는 통과
        return True
    
    def handle_release(self, event) -> bool:
        """키 떼기 처리
        
        Returns:
            False를 반환하면 키 입력 차단
        """
        key = event.name
        
        # 키 상태 제거
        self.core.remove_pressed_key(key)
        
        # 매크로 키 처리
        if self.core.is_macro_key(key):
            self.core.stop(key)
            return False  # 트리거 키 입력 차단
        
        return True
    
    def shutdown(self):
        """프로그램 종료"""
        print("프로그램을 종료합니다...")
        self.running = False
        self.core.stop_signal.set()
        
        # 키보드 후킹 모두 해제
        try:
            keyboard.unhook_all()
        except:
            pass
        
        # 강제 종료
        os._exit(0)