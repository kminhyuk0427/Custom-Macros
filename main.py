import sys
import os

# PyInstaller 환경 처리
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)
sys.path.insert(0, os.path.join(application_path, 'modules'))

def main():
    """메인 진입점"""
    try:
        import config
        from app import MacroApp
        
        app = MacroApp()
        
        # 설정 검증
        if not app.validate_config(config):
            print("\nconfig.py을 확인하고 다시 시도하세요.")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # 설정 로드 및 실행
        app.load_config(config)
        app.run()
        
    except KeyboardInterrupt:
        print("\n프로그램 종료 중...")
        sys.exit(0)
        
    except ImportError as e:
        print(f"\n[오류] 필수 모듈을 가져올 수 없습니다: {e}")
        print("requirements.txt의 패키지들이 설치되어 있는지 확인하세요.")
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n[오류] 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()