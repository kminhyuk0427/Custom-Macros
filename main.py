import sys
import traceback
import os

# modules 폴더 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

def main():
    """메인 실행 함수"""
    try:
        # 설정 모듈 임포트
        import config
        
        # 애플리케이션 임포트
        from app import MacroApp
        
        # 애플리케이션 초기화
        app = MacroApp()
        
        # 설정 유효성 검사
        if not app.validate_config(config):
            input("\n설정 오류가 있습니다. 아무 키나 눌러 종료...")
            sys.exit(1)
        
        # 설정 로드
        app.load_config(config)
        
        # 애플리케이션 실행
        app.run()
        
    except KeyboardInterrupt:
        # Ctrl+C로 종료
        sys.exit(0)
        
    except ImportError as e:
        print(f"모듈 로드 실패: {e}")
        print("\n필요한 파일이 모두 있는지 확인하세요:")
        print("  - config.py (현재 폴더)")
        print("  - modules/app.py")
        print("  - modules/core.py")
        print("  - modules/handler.py")
        print("  - modules/tray.py")
        print("\n필요한 라이브러리 설치:")
        print("  pip install keyboard==0.13.5")
        print("  pip install pystray")
        print("  pip install Pillow")
        try:
            input("\n아무 키나 눌러 종료...")
        except:
            pass
        sys.exit(1)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        print("\n상세 오류 정보:")
        traceback.print_exc()
        try:
            input("\n아무 키나 눌러 종료...")
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()