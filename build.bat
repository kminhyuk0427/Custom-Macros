@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
echo ========================================
echo GThey5M 빌드
echo ========================================
echo.

REM ========================================
REM 1단계: Python 설치 확인
REM ========================================
echo [1/6] Python 확인 중...
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python
    echo [OK] Python 발견: python
) else (
    set PYTHON=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe
    if exist "!PYTHON!" (
        echo [OK] Python 발견: !PYTHON!
    ) else (
        echo [실패] Python을 찾을 수 없습니다.
        echo.
        echo ========================================
        echo 해결 방법:
        echo ========================================
        echo 1. Python 설치 확인
        echo    - Python이 설치되어 있나요?
        echo    - 설치 안 됨: https://python.org 에서 다운로드
        echo.
        echo 2. PATH 환경변수 확인
        echo    - Python 설치 시 "Add to PATH" 체크했나요?
        echo    - 안 했다면: Python 재설치 권장
        echo.
        echo 3. 수동 경로 설정
        echo    - Python 설치 경로를 찾아서
        echo    - build.bat 파일 17번째 줄 수정
        echo    - set PYTHON=경로\python.exe
        echo ========================================
        pause
        exit /b 1
    )
)

%PYTHON% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [실패] Python 실행 오류
    echo.
    echo Python이 손상되었을 수 있습니다.
    echo Python을 재설치해주세요: https://python.org
    pause
    exit /b 1
)

%PYTHON% --version
echo.

REM ========================================
REM 2단계: 필수 라이브러리 설치 확인
REM ========================================
echo [2/6] 필수 라이브러리 확인 중...
%PYTHON% -c "import keyboard, pystray, PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo [경고] 필수 라이브러리 누락 감지
    echo.
    echo 자동 설치를 시도합니다...
    echo.
    
    %PYTHON% -m pip install --upgrade pip >nul 2>&1
    %PYTHON% -m pip install -r requirements.txt
    
    if %errorlevel% neq 0 (
        echo [실패] 라이브러리 설치 실패
        echo.
        echo ========================================
        echo 해결 방법:
        echo ========================================
        echo 1. 관리자 권한으로 실행
        echo    - build.bat 우클릭
        echo    - "관리자 권한으로 실행" 선택
        echo.
        echo 2. 수동 설치 시도
        echo    - 명령 프롬프트 열기
        echo    - 다음 명령어 실행:
        echo      pip install keyboard==0.13.5 pystray Pillow
        echo.
        echo 3. pip 업그레이드
        echo    - python -m pip install --upgrade pip
        echo    - 그 후 다시 build.bat 실행
        echo.
        echo 4. 인터넷 연결 확인
        echo    - 방화벽이 pip을 차단하고 있나요?
        echo ========================================
        pause
        exit /b 1
    )
)
echo [OK] 라이브러리 확인 완료
echo.

REM ========================================
REM 3단계: PyInstaller 확인
REM ========================================
echo [3/6] PyInstaller 확인 중...
%PYTHON% -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [경고] PyInstaller 미설치
    echo 자동 설치 중...
    %PYTHON% -m pip install pyinstaller
    
    if %errorlevel% neq 0 (
        echo [실패] PyInstaller 설치 실패
        echo.
        echo 수동으로 설치해주세요:
        echo pip install pyinstaller
        pause
        exit /b 1
    )
)
echo [OK] PyInstaller 준비 완료
echo.

REM ========================================
REM 4단계: 필수 파일 확인
REM ========================================
echo [4/6] 필수 파일 확인 중...
set MISSING_FILES=0

if not exist "main.py" (
    echo [실패] main.py 파일 없음
    set MISSING_FILES=1
)

if not exist "config.py" (
    echo [실패] config.py 파일 없음
    set MISSING_FILES=1
)

if not exist "modules\app.py" (
    echo [실패] modules\app.py 파일 없음
    set MISSING_FILES=1
)

if not exist "modules\core.py" (
    echo [실패] modules\core.py 파일 없음
    set MISSING_FILES=1
)

if not exist "modules\handler.py" (
    echo [실패] modules\handler.py 파일 없음
    set MISSING_FILES=1
)

if not exist "modules\tray.py" (
    echo [실패] modules\tray.py 파일 없음
    set MISSING_FILES=1
)

if !MISSING_FILES! equ 1 (
    echo.
    echo ========================================
    echo 해결 방법:
    echo ========================================
    echo 1. 파일이 모두 있는지 확인
    echo    - main.py
    echo    - config.py
    echo    - modules 폴더 및 내부 파일들
    echo.
    echo 2. 압축 파일을 다시 풀어보세요
    echo    - 모든 파일이 함께 있어야 합니다
    echo.
    echo 3. 파일이 손상되었을 수 있습니다
    echo    - 원본 파일을 다시 다운로드하세요
    echo ========================================
    pause
    exit /b 1
)
echo [OK] 모든 필수 파일 존재
echo.

REM __init__.py 생성
if not exist modules\__init__.py (
    echo # modules package > modules\__init__.py
)

REM 매니페스트 파일 생성
(
echo ^<?xml version="1.0" encoding="UTF-8" standalone="yes"?^>
echo ^<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0"^>
echo   ^<assemblyIdentity version="1.0.0.0" processorArchitecture="*" name="GThey5M" type="win32"/^>
echo   ^<description^>GThey5M^</description^>
echo   ^<trustInfo xmlns="urn:schemas-microsoft-com:asm.v3"^>
echo     ^<security^>
echo       ^<requestedPrivileges^>
echo         ^<requestedExecutionLevel level="requireAdministrator" uiAccess="false"/^>
echo       ^</requestedPrivileges^>
echo     ^</security^>
echo   ^</trustInfo^>
echo ^</assembly^>
) > GThey5M.manifest

REM ========================================
REM 5단계: 이전 빌드 정리
REM ========================================
echo [5/6] 이전 빌드 정리 중...
if exist build (
    rmdir /s /q build >nul 2>&1
)
if exist dist (
    rmdir /s /q dist >nul 2>&1
)
if exist GThey5M.spec (
    del GThey5M.spec >nul 2>&1
)
echo [OK] 정리 완료
echo.

REM ========================================
REM 6단계: 빌드 실행
REM ========================================
echo [6/6] 빌드 시작 (1-2분 소요)
echo.
echo 빌드 중... 잠시만 기다려주세요.
echo.
echo.

REM 빌드 실행
if exist icon.ico (
    %PYTHON% -m PyInstaller --onefile --noconsole --name=GThey5M --manifest=GThey5M.manifest --uac-admin --clean --noconfirm --hidden-import=keyboard --hidden-import=pystray --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageDraw --add-data "config.py;." --add-data "modules;modules" --add-data "icon.ico;." --icon=icon.ico main.py >build_log.txt 2>&1
) else (
    %PYTHON% -m PyInstaller --onefile --noconsole --name=GThey5M --manifest=GThey5M.manifest --uac-admin --clean --noconfirm --hidden-import=keyboard --hidden-import=pystray --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageDraw --add-data "config.py;." --add-data "modules;modules" main.py >build_log.txt 2>&1
)

if %errorlevel% neq 0 (
    echo [실패] 빌드 중 오류 발생
    echo.
    echo ========================================
    echo 오류 로그 확인:
    echo ========================================
    echo 전체 로그는 build_log.txt 파일을 확인하세요.
    echo.
    echo ========================================
    echo 일반적인 해결 방법:
    echo ========================================
    echo 1. 디스크 공간 확인
    echo    - 최소 500MB 이상 필요
    echo.
    echo 2. 바이러스 백신 확인
    echo    - 백신이 빌드를 차단할 수 있음
    echo    - 임시로 비활성화 후 재시도
    echo.
    echo 3. 관리자 권한으로 실행
    echo    - build.bat 우클릭
    echo    - "관리자 권한으로 실행"
    echo.
    echo 4. 경로에 한글 포함 여부
    echo    - 폴더명을 영문으로 변경
    echo.
    echo 5. PyInstaller 재설치
    echo    - pip uninstall pyinstaller
    echo    - pip install pyinstaller
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo 빌드 완료!
echo ========================================

REM ========================================
REM 빌드 결과 확인
REM ========================================
if exist dist\GThey5M.exe (
    echo.
    echo [OK] 실행 파일 생성 성공!
    echo.
    
    REM 바탕화면으로 복사
    set DESKTOP=%USERPROFILE%\Desktop
    copy /Y dist\GThey5M.exe "!DESKTOP!\GThey5M.exe" >nul 2>&1
    
    if exist "!DESKTOP!\GThey5M.exe" (
        echo [OK] 바탕화면 복사 완료!
        echo      위치: !DESKTOP!\GThey5M.exe
    ) else (
        echo [경고] 바탕화면 복사 실패
        echo        수동 복사: dist\GThey5M.exe
    )
    
    echo.
    echo ========================================
    echo 주의사항:
    echo ========================================
    echo - 백신 프로그램이 차단할 수 있음 (허용 설정 필요)
    echo - 반드시 관리자 권한으로 실행
    echo - config.py 수정 후 다시 빌드 필요
    echo ========================================
    
) else (
    echo.
    echo (무시해도 되는 오류)
    echo [경고] dist\GThey5M.exe 파일 생성 안 됨
    echo.
    echo ========================================
    echo 해결 방법:
    echo ========================================
    echo 1. build_log.txt 파일 확인
    echo    - 상세한 오류 내역 포함
    echo.
    echo 2. 다시 시도
    echo    - build.bat을 다시 실행
    echo.
    echo 3. 백신 프로그램 확인
    echo    - 실시간 검사 일시 중지
    echo ========================================
)

echo.
pause