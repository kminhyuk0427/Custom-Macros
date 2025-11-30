import sys
import traceback
import os

# 실행 파일로 빌드되었을 때의 경로 처리
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 실행 파일
    application_path = sys._MEIPASS
else:
    # 일반 Python 스크립트
    application_path = os.path.dirname(os.path.abspath(__file__))

# 경로 추가
sys.path.insert(0, application_path)
sys.path.insert(0, os.path.join(application_path, 'modules'))

def main():
    """메인 실행 함수"""
    try:
        # 설정 모듈 임포트
        import config
        
        # modules 내부 임포트
        from app import MacroApp
        
        # 애플리케이션 초기화
        app = MacroApp()
        
        # 설정 유효성 검사
        if not app.validate_config(config):
            print("\n설정 오류가 있습니다.")
            input("아무 키나 눌러 종료...")
            sys.exit(1)
        
        # 설정 로드
        app.load_config(config)
        
        # 애플리케이션 실행
        app.run()
        
    except KeyboardInterrupt:
        # Ctrl+C로 종료
        print("\n프로그램이 중단되었습니다.")
        sys.exit(0)
        
    except ImportError as e:
        print(f"\n모듈 로드 실패: {e}")
        print("\n필요한 파일:")
        print("  - config.py")
        print("  - modules/app.py")
        print("  - modules/core.py")
        print("  - modules/handler.py")
        print("  - modules/tray.py")
        print("  - modules/__init__.py")
        print("\n필요한 라이브러리:")
        print("  pip install keyboard==0.13.5 pystray Pillow")
        input("\n아무 키나 눌러 종료...")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        print("\n상세 오류 정보:")
        traceback.print_exc()
        input("\n아무 키나 눌러 종료...")
        sys.exit(1)

if __name__ == "__main__":
    main()