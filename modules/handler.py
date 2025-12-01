import keyboard
import os
import time
import threading

class EventHandler:
    """키보드 이벤트 핸들러"""
    
    def __init__(self, core, toggle_key='`'):
        self.core = core
        self.running = True
        self.toggle_key = toggle_key
        self.mode2_blocked = set()
        self.trigger_blocked = set()
        
        # mode 1 전용: 물리적 키 차단 (OS 입력 완전 무시)
        self.mode1_active = set()
    
    def get_base_key(self, event) -> str:
        """shift 조합키 제거 후 기본 키만 추출"""
        key_name = event.name
        
        shift_map = {
            '!': '1', '@': '2', '#': '3', '$': '4', '%': '5',
            '^': '6', '&': '7', '*': '8', '(': '9', ')': '0'
        }
        
        return shift_map.get(key_name, key_name)
    
    def handle_press(self, event) -> bool:
        """키 눌림 처리 - False 반환 시 OS 입력 차단"""
        key = self.get_base_key(event)
        
        # 토글 키 처리
        if key == self.toggle_key:
            self.core.toggle_macro()
            return False
        
        # 매크로 비활성화 상태면 모든 키 통과
        if not self.core.macro_enabled:
            return True
        
        # 매크로 키인 경우
        if self.core.is_macro_key(key):
            # 이미 차단 중이면 완전 무시 (OS 입력 차단)
            if key in self.trigger_blocked:
                return False
            
            # 트리거 키 OS 입력 차단 시작
            self.trigger_blocked.add(key)
            
            macro_info = self.core.macros[key]
            mode = macro_info['mode']
            
            # mode 1: 연속 반복 - 물리적 차단 활성화
            if mode == 1:
                self.mode1_active.add(key)
            
            # mode 2: 단일 실행 - 추가 차단
            elif mode == 2:
                if key in self.mode2_blocked:
                    return False
                self.mode2_blocked.add(key)
            
            # 이미 눌린 키면 무시
            if key in self.core.pressed_keys:
                return False
            
            # 키 상태 기록
            self.core.add_pressed_key(key)
            
            # 매크로 시작
            self.core.start(key)
            
            # OS 입력 완전 차단
            return False
        
        # 일반 키는 통과
        return True
    
    def handle_release(self, event) -> bool:
        """키 떼기 처리 - False 반환 시 OS 입력 차단"""
        key = self.get_base_key(event)
        
        # 토글 키 차단
        if key == self.toggle_key:
            return False
        
        # 매크로 비활성화 상태면 모든 키 통과
        if not self.core.macro_enabled:
            return True
        
        # 매크로 키 처리
        if self.core.is_macro_key(key):
            # 키 상태 제거
            self.core.remove_pressed_key(key)
            
            macro_info = self.core.macros[key]
            mode = macro_info['mode']
            
            if mode == 1:
                # 연속 반복: 즉시 중단 및 차단 해제
                self.core.stop(key)
                self.mode1_active.discard(key)
                self.trigger_blocked.discard(key)
                
            elif mode == 2:
                # 단일 실행: 지연 후 차단 해제
                def delayed_unblock():
                    time.sleep(0.05)
                    self.mode2_blocked.discard(key)
                    self.trigger_blocked.discard(key)
                
                threading.Thread(target=delayed_unblock, daemon=True).start()
            
            # OS 입력 완전 차단
            return False
        
        # 일반 키는 통과
        return True
    
    def shutdown(self):
        """프로그램 종료"""
        self.running = False
        self.core.stop_signal.set()
        
        try:
            keyboard.unhook_all()
        except:
            pass
        
        os._exit(0)