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
        
        # 이벤트 핸들러 초기화 (토글 키는 나중에 설정)
        self.handler = None
        
        # 트레이 아이콘 초기화
        self.tray = TrayIcon(self.on_exit)
        
        # 토글 키 저장
        self.toggle_key = '`'
    
    def on_exit(self):
        """프로그램 종료"""
        print("종료 신호 수신...")
        if self.handler:
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
        
        # 토글 키 설정
        self.toggle_key = config.TOGGLE_KEY
        
        # 핵심 엔진에 설정 적용
        self.core.configure(
            macros=config.MACROS,
            timings=timings
        )
        
        # 이벤트 핸들러 초기화 (토글 키 포함)
        self.handler = EventHandler(self.core, self.toggle_key)
    
    def setup_hooks(self):
        """키보드 후킹 설정"""
        # 토글 키 후킹 (최우선)
        keyboard.on_press_key(
            self.toggle_key,
            self.handler.handle_press,
            suppress=True
        )
        keyboard.on_release_key(
            self.toggle_key,
            self.handler.handle_release,
            suppress=True
        )
        
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
    
    def run(self):
        """애플리케이션 실행"""
        # 트레이 아이콘 시작
        self.tray.run()
        
        # 키보드 후킹 설정
        self.setup_hooks()
        
        print("========================================")
        print("게임 매크로가 실행 중입니다!")
        print("========================================")
        print()
        print("매크로 ON/OFF:")
        print(f"  - [{self.toggle_key}] 키를 눌러 토글")
        print(f"  - 현재 상태: {'활성화' if self.core.macro_enabled else '비활성화'}")
        print()
        print("종료 방법:")
        print("  - 작업표시줄 오른쪽 하단 숨겨진 아이콘")
        print("  - 녹색 원 아이콘 우클릭")
        print("  - '종료' 선택")
        print()
        print("========================================")
        
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
        
        # TOGGLE_KEY 검증
        if not hasattr(config, 'TOGGLE_KEY'):
            print("오류: TOGGLE_KEY가 정의되지 않았습니다")
            return False
        
        if not isinstance(config.TOGGLE_KEY, str):
            print("오류: TOGGLE_KEY는 문자열이어야 합니다")
            return False
        
        # 각 매크로 검증
        for key, macro_info in config.MACROS.items():
            # 딕셔너리 형태 확인
            if not isinstance(macro_info, dict):
                print(f"오류: '{key}' 매크로는 딕셔너리 형태여야 합니다")
                print(f"예시: '{key}': {{'keys': ['a', 'b'], 'mode': 2}}")
                return False
            
            # 'keys' 키 존재 확인
            if 'keys' not in macro_info:
                print(f"오류: '{key}' 매크로에 'keys'가 없습니다")
                return False
            
            # 'mode' 키 존재 확인
            if 'mode' not in macro_info:
                print(f"오류: '{key}' 매크로에 'mode'가 없습니다")
                return False
            
            # mode 값 검증 (0, 1, 2)
            if macro_info['mode'] not in [0, 1, 2]:
                print(f"오류: '{key}' 매크로의 mode는 0, 1 또는 2여야 합니다 (현재: {macro_info['mode']})")
                print("  0 = 비활성, 1 = 연속 반복, 2 = 단일 실행")
                return False
            
            # keys 리스트 확인
            if not isinstance(macro_info['keys'], list):
                print(f"오류: '{key}' 매크로의 'keys'는 리스트여야 합니다")
                return False
            
            if not macro_info['keys']:
                print(f"오류: '{key}' 매크로의 'keys'가 비어있습니다")
                return False
            
            # delays 검증 (선택사항)
            if 'delays' in macro_info:
                delays = macro_info['delays']
                
                if not isinstance(delays, list):
                    print(f"오류: '{key}' 매크로의 'delays'는 리스트여야 합니다")
                    return False
                
                if len(delays) != len(macro_info['keys']):
                    print(f"오류: '{key}' 매크로의 'delays' 개수({len(delays)})가 'keys' 개수({len(macro_info['keys'])})와 다릅니다")
                    print(f"팁: delays를 지정하지 않으면 기본 딜레이를 사용합니다")
                    return False
                
                # 각 딜레이 값이 숫자인지 확인
                for i, delay in enumerate(delays):
                    if not isinstance(delay, (int, float)):
                        print(f"오류: '{key}' 매크로의 delays[{i}]는 숫자여야 합니다 (현재: {delay})")
                        return False
                    
                    if delay < 0:
                        print(f"오류: '{key}' 매크로의 delays[{i}]는 0 이상이어야 합니다 (현재: {delay})")
                        return False
            
            # holds 검증 (선택사항)
            if 'holds' in macro_info:
                holds = macro_info['holds']
                
                if not isinstance(holds, list):
                    print(f"오류: '{key}' 매크로의 'holds'는 리스트여야 합니다")
                    return False
                
                if len(holds) != len(macro_info['keys']):
                    print(f"오류: '{key}' 매크로의 'holds' 개수({len(holds)})가 'keys' 개수({len(macro_info['keys'])})와 다릅니다")
                    print(f"팁: holds를 지정하지 않으면 기본 홀드 시간을 사용합니다")
                    return False
                
                # 각 홀드 값이 숫자인지 확인
                for i, hold in enumerate(holds):
                    if not isinstance(hold, (int, float)):
                        print(f"오류: '{key}' 매크로의 holds[{i}]는 숫자여야 합니다 (현재: {hold})")
                        return False
                    
                    if hold < 0:
                        print(f"오류: '{key}' 매크로의 holds[{i}]는 0 이상이어야 합니다 (현재: {hold})")
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