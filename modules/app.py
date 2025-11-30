import keyboard
import sys
import os

# modules 폴더에서 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from core import MacroCore
from handler import EventHandler
from tray import TrayIcon

class MacroApp:
    """매크로 애플리케이션 메인 클래스"""
    
    def __init__(self):
        # 핵심 엔진 초기화
        self.core = MacroCore()
        
        # 이벤트 핸들러 초기화
        self.handler = EventHandler(self.core)
        
        # 트레이 아이콘 초기화
        self.tray = TrayIcon(self.on_exit)
        
        # 종료 플래그
        self.should_exit = False
    
    def on_exit(self):
        """프로그램 종료"""
        print("종료 신호 수신...")
        self.should_exit = True
        self.handler.shutdown()
    
    def load_config(self, config):
        """설정 로드
        
        Args:
            config: 설정 모듈 (config.py)
        """
        # 타이밍 설정 구성
        timings = {
            'press': config.KEY_PRESS_DURATION,
            'release': config.KEY_RELEASE_DURATION,
            'sequence': config.SEQUENCE_DELAY
        }
        
        # 핵심 엔진에 설정 적용
        self.core.configure(
            macros=config.MACROS,
            timings=timings
        )
    
    def setup_hooks(self):
        """키보드 후킹 설정"""
        # 매크로 키 후킹 (입력 차단)
        for macro_key in self.core.macros.keys():
            keyboard.on_press_key(
                macro_key,
                self.handler.handle_press,
                suppress=True
            )
            keyboard.on_release_key(
                macro_key,
                self.handler.handle_release,
                suppress=True
            )
        
        # ESC 키 후킹 (입력 허용)
        keyboard.on_press_key(
            'esc',
            self.handler.handle_press,
            suppress=False
        )
    
    def run(self):
        """애플리케이션 실행"""
        # 트레이 아이콘 시작
        self.tray.run()
        
        # 키보드 후킹 설정
        self.setup_hooks()
        
        print("매크로 프로그램이 실행 중입니다...")
        print("ESC 키를 누르거나 트레이 아이콘에서 '종료'를 선택하세요.")
        
        # 이벤트 대기
        keyboard.wait()
    
    def validate_config(self, config) -> bool:
        """설정 유효성 검사
        
        Returns:
            설정이 유효하면 True
        """
        # MACROS 검증
        if not hasattr(config, 'MACROS'):
            print("오류: MACROS가 정의되지 않았습니다")
            return False
        
        if not config.MACROS:
            print("오류: 매크로가 비어있습니다")
            return False
        
        if not isinstance(config.MACROS, dict):
            print("오류: MACROS는 딕셔너리 형태여야 합니다")
            return False
        
        # 각 매크로 검증
        for key, macro_info in config.MACROS.items():
            # 딕셔너리 형태 확인
            if not isinstance(macro_info, dict):
                print(f"오류: '{key}' 매크로는 딕셔너리 형태여야 합니다")
                print(f"예시: '{key}': {{'keys': ['a', 'b'], 'mode': 1}}")
                return False
            
            # 'keys' 키 존재 확인
            if 'keys' not in macro_info:
                print(f"오류: '{key}' 매크로에 'keys'가 없습니다")
                return False
            
            # 'mode' 키 존재 확인
            if 'mode' not in macro_info:
                print(f"오류: '{key}' 매크로에 'mode'가 없습니다")
                return False
            
            # mode 값 검증
            if macro_info['mode'] not in [0, 1]:
                print(f"오류: '{key}' 매크로의 mode는 0 또는 1이어야 합니다 (현재: {macro_info['mode']})")
                return False
            
            # keys 리스트 확인
            if not isinstance(macro_info['keys'], list):
                print(f"오류: '{key}' 매크로의 'keys'는 리스트여야 합니다")
                return False
            
            if not macro_info['keys']:
                print(f"오류: '{key}' 매크로의 'keys'가 비어있습니다")
                return False
        
        # 타이밍 검증
        if not hasattr(config, 'KEY_PRESS_DURATION'):
            print("오류: KEY_PRESS_DURATION이 정의되지 않았습니다")
            return False
        
        if config.KEY_PRESS_DURATION < 0:
            print("오류: KEY_PRESS_DURATION은 0 이상이어야 합니다")
            return False
        
        if not hasattr(config, 'KEY_RELEASE_DURATION'):
            print("오류: KEY_RELEASE_DURATION이 정의되지 않았습니다")
            return False
        
        if config.KEY_RELEASE_DURATION < 0:
            print("오류: KEY_RELEASE_DURATION은 0 이상이어야 합니다")
            return False
        
        if not hasattr(config, 'SEQUENCE_DELAY'):
            print("오류: SEQUENCE_DELAY가 정의되지 않았습니다")
            return False
        
        if config.SEQUENCE_DELAY < 0:
            print("오류: SEQUENCE_DELAY는 0 이상이어야 합니다")
            return False
        
        return True