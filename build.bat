@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
echo ========================================
echo GTA 게임 매크로 빌드
echo ========================================
echo.

REM Python 경로 자동 감지
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python
) else (
    set PYTHON=C:\Users\kaskm\AppData\Local\Programs\Python\Python313\python.exe
)

echo Python: %PYTHON%
%PYTHON% --version
echo.

REM __init__.py 생성
if not exist modules\__init__.py (
    echo # modules package > modules\__init__.py
    echo __init__.py 생성됨
    echo.
)

REM 매니페스트 파일 생성 (관리자 권한 요청용)
echo 관리자 권한 매니페스트 생성 중...
(
echo ^<?xml version="1.0" encoding="UTF-8" standalone="yes"?^>
echo ^<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0"^>
echo   ^<assemblyIdentity
echo     version="1.0.0.0"
echo     processorArchitecture="*"
echo     name="GameMacro"
echo     type="win32"
echo   /^>
echo   ^<description^>GTA Game Macro^</description^>
echo   ^<trustInfo xmlns="urn:schemas-microsoft-com:asm.v3"^>
echo     ^<security^>
echo       ^<requestedPrivileges^>
echo         ^<requestedExecutionLevel level="requireAdministrator" uiAccess="false"/^>
echo       ^</requestedPrivileges^>
echo     ^</security^>
echo   ^</trustInfo^>
echo ^</assembly^>
) > GameMacro.manifest
echo 매니페스트 파일 생성 완료
echo.

REM 이전 빌드 삭제
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist GameMacro.spec del GameMacro.spec

echo 빌드 시작 (1-2분 소요)...
echo.

REM 빌드 실행
if exist icon.ico (
    %PYTHON% -m PyInstaller ^
        --onefile ^
        --noconsole ^
        --icon=icon.ico ^
        --name=GameMacro ^
        --manifest=GameMacro.manifest ^
        --uac-admin ^
        --clean ^
        --noconfirm ^
        --hidden-import=keyboard ^
        --hidden-import=pystray ^
        --hidden-import=PIL ^
        --hidden-import=PIL.Image ^
        --hidden-import=PIL.ImageDraw ^
        --add-data "config.py;." ^
        --add-data "modules;modules" ^
        --add-data "icon.ico;." ^
        main.py
) else (
    %PYTHON% -m PyInstaller ^
        --onefile ^
        --noconsole ^
        --name=GameMacro ^
        --manifest=GameMacro.manifest ^
        --uac-admin ^
        --clean ^
        --noconfirm ^
        --hidden-import=keyboard ^
        --hidden-import=pystray ^
        --hidden-import=PIL ^
        --hidden-import=PIL.Image ^
        --hidden-import=PIL.ImageDraw ^
        --add-data "config.py;." ^
        --add-data "modules;modules" ^
        main.py
)

echo.
echo ========================================

REM 빌드 결과 확인
if exist dist\GameMacro.exe (
    echo 빌드 성공!
    echo ========================================
    echo.
    
    REM 매니페스트가 제대로 포함되었는지 확인
    echo [확인] 관리자 권한 요청이 포함되었습니다.
    echo.
    
    REM 바탕화면으로 복사
    set DESKTOP=%USERPROFILE%\Desktop
    copy /Y dist\GameMacro.exe "!DESKTOP!\GameMacro.exe" >nul 2>&1
    
    if exist "!DESKTOP!\GameMacro.exe" (
        echo [v] 바탕화면에 복사 완료!
        echo     위치: !DESKTOP!\GameMacro.exe
    ) else (
        echo [!] 바탕화면 복사 실패
        echo     수동 복사: dist\GameMacro.exe
    )
    
    echo.
    echo ========================================
    echo 실행 방법:
    echo ========================================
    echo.
    echo 1. 바탕화면의 GameMacro.exe 더블클릭
    echo    (관리자 권한 요청 팝업이 나타남)
    echo.
    echo 2. "예" 클릭
    echo.
    echo 3. GTA5 실행 후 매크로 사용
    echo.
    echo 종료: 트레이 아이콘 우클릭 - 종료
    echo.
    echo ========================================
    echo.
    echo 참고: 실행 시 UAC 창이 나타나야 정상입니다.
    echo       만약 나타나지 않으면:
    echo       - 우클릭 - 관리자 권한으로 실행
    echo       또는 build.bat을 다시 실행하세요.
    
) else (
    echo 빌드 실패!
    echo ========================================
    echo.
    echo dist\GameMacro.exe 파일이 없습니다.
    echo 오류를 확인하세요.
)

echo.
echo ========================================
pause