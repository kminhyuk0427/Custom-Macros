@echo off
chcp 65001 > nul
echo ========================================
echo 게임 매크로 실행 파일 빌드
echo ========================================
echo.

REM Python 경로 설정
set PYTHON=C:\Users\kaskm\AppData\Local\Programs\Python\Python313\python.exe

REM PyInstaller 설치 확인
%PYTHON% -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [1/4] PyInstaller 설치 중...
    %PYTHON% -m pip install pyinstaller
    echo.
) else (
    echo [1/4] PyInstaller 이미 설치됨
    echo.
)

REM keyboard 라이브러리 설치 확인
echo [2/5] keyboard 라이브러리 확인 중...
%PYTHON% -c "import keyboard" 2>nul
if errorlevel 1 (
    echo keyboard 설치 중...
    %PYTHON% -m pip install keyboard==0.13.5
    echo.
) else (
    echo keyboard 이미 설치됨
    echo.
)

REM pystray 라이브러리 설치 확인
echo [3/5] pystray 라이브러리 확인 중...
%PYTHON% -c "import pystray" 2>nul
if errorlevel 1 (
    echo pystray 설치 중...
    %PYTHON% -m pip install pystray
    echo.
) else (
    echo pystray 이미 설치됨
    echo.
)

REM Pillow 라이브러리 설치 확인
echo [4/5] Pillow 라이브러리 확인 중...
%PYTHON% -c "import PIL" 2>nul
if errorlevel 1 (
    echo Pillow 설치 중...
    %PYTHON% -m pip install Pillow
    echo.
) else (
    echo Pillow 이미 설치됨
    echo.
)

echo [5/5] 실행 파일 생성 중...
echo.

REM 이전 빌드 파일 삭제
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist GameMacro.spec del GameMacro.spec

REM modules 폴더의 모든 파일을 포함하여 빌드
if exist icon.ico (
    REM 아이콘 있으면 포함
    %PYTHON% -m PyInstaller --onefile ^
        --noconsole ^
        --icon=icon.ico ^
        --name="GameMacro" ^
        --uac-admin ^
        --clean ^
        --paths=modules ^
        --hidden-import=keyboard ^
        --hidden-import=pystray ^
        --hidden-import=PIL ^
        --hidden-import=config ^
        --hidden-import=app ^
        --hidden-import=core ^
        --hidden-import=handler ^
        --hidden-import=tray ^
        --collect-all=keyboard ^
        --collect-all=pystray ^
        --collect-all=PIL ^
        main.py
) else (
    REM 아이콘 없으면 기본값
    %PYTHON% -m PyInstaller --onefile ^
        --noconsole ^
        --name="GameMacro" ^
        --uac-admin ^
        --clean ^
        --paths=modules ^
        --hidden-import=keyboard ^
        --hidden-import=pystray ^
        --hidden-import=PIL ^
        --hidden-import=config ^
        --hidden-import=app ^
        --hidden-import=core ^
        --hidden-import=handler ^
        --hidden-import=tray ^
        --collect-all=keyboard ^
        --collect-all=pystray ^
        --collect-all=PIL ^
        main.py
)

if errorlevel 1 (
    echo.
    echo 빌드 실패
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 빌드 완료!
echo ========================================
echo.
echo [6/6] 실행 파일 복사 중...

REM 바탕화면 경로
set DESKTOP=%USERPROFILE%\Desktop

REM 실행 파일을 바탕화면으로 복사
if exist dist\GameMacro.exe (
    copy /Y dist\GameMacro.exe "%DESKTOP%\GameMacro.exe"
    echo.
    echo 실행 파일이 바탕화면에 복사되었습니다!
    echo.
    echo 위치: %DESKTOP%\GameMacro.exe
    echo.
    echo 사용법:
    echo    1. 바탕화면의 GameMacro.exe 우클릭
    echo    2. "관리자 권한으로 실행" 선택
    echo    3. 매크로 사용 시작!
    echo.
    echo 매크로 수정 방법:
    echo    프로젝트 폴더의 config.py 파일을 수정한 후
    echo    다시 build.bat을 실행하세요
    echo.
) else (
    echo 실행 파일을 찾을 수 없습니다!
)

echo ========================================
pause