@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

echo ========================================
echo GThey5M Build
echo ========================================
echo.

REM ========================================
REM Step 1: Check Python Installation
REM ========================================
echo [1/6] Checking Python...
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python
    echo [OK] Python found: python
) else (
    set PYTHON=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe
    if exist "!PYTHON!" (
        echo [OK] Python found: !PYTHON!
    ) else (
        echo [FAIL] Python not found.
        echo.
        echo ========================================
        echo Solutions:
        echo ========================================
        echo 1. Check Python installation
        echo    - Is Python installed?
        echo    - If not: Download from https://python.org
        echo.
        echo 2. Check PATH environment variable
        echo    - Did you check "Add to PATH" during install?
        echo    - If not: Reinstall Python recommended
        echo.
        echo 3. Manual path setting
        echo    - Find Python installation path
        echo    - Edit build.bat line 17
        echo    - set PYTHON=path\python.exe
        echo ========================================
        pause
        exit /b 1
    )
)

%PYTHON% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Python execution error
    echo.
    echo Python may be corrupted.
    echo Please reinstall Python: https://python.org
    pause
    exit /b 1
)

%PYTHON% --version
echo.

REM ========================================
REM Step 2: Check Required Libraries
REM ========================================
echo [2/6] Checking required libraries...
%PYTHON% -c "import keyboard, pystray, PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Missing required libraries detected
    echo.
    echo Attempting automatic installation...
    echo.
    
    %PYTHON% -m pip install --upgrade pip >nul 2>&1
    %PYTHON% -m pip install -r requirements.txt
    
    if %errorlevel% neq 0 (
        echo [FAIL] Library installation failed
        echo.
        echo ========================================
        echo Solutions:
        echo ========================================
        echo 1. Run as administrator
        echo    - Right-click build.bat
        echo    - Select "Run as administrator"
        echo.
        echo 2. Try manual installation
        echo    - Open command prompt
        echo    - Run: pip install keyboard==0.13.5 pystray Pillow
        echo.
        echo 3. Upgrade pip
        echo    - python -m pip install --upgrade pip
        echo    - Then run build.bat again
        echo.
        echo 4. Check internet connection
        echo    - Is firewall blocking pip?
        echo ========================================
        pause
        exit /b 1
    )
)
echo [OK] Libraries verified
echo.

REM ========================================
REM Step 3: Check PyInstaller
REM ========================================
echo [3/6] Checking PyInstaller...
%PYTHON% -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] PyInstaller not installed
    echo Installing automatically...
    %PYTHON% -m pip install pyinstaller
    
    if %errorlevel% neq 0 (
        echo [FAIL] PyInstaller installation failed
        echo.
        echo Please install manually:
        echo pip install pyinstaller
        pause
        exit /b 1
    )
)
echo [OK] PyInstaller ready
echo.

REM ========================================
REM Step 4: Check Required Files
REM ========================================
echo [4/6] Checking required files...
set MISSING_FILES=0

if not exist "main.py" (
    echo [FAIL] main.py not found
    set MISSING_FILES=1
)

if not exist "config.py" (
    echo [FAIL] config.py not found
    set MISSING_FILES=1
)

if not exist "modules\app.py" (
    echo [FAIL] modules\app.py not found
    set MISSING_FILES=1
)

if not exist "modules\core.py" (
    echo [FAIL] modules\core.py not found
    set MISSING_FILES=1
)

if not exist "modules\handler.py" (
    echo [FAIL] modules\handler.py not found
    set MISSING_FILES=1
)

if not exist "modules\tray.py" (
    echo [FAIL] modules\tray.py not found
    set MISSING_FILES=1
)

if !MISSING_FILES! equ 1 (
    echo.
    echo ========================================
    echo Solutions:
    echo ========================================
    echo 1. Check if all files exist
    echo    - main.py
    echo    - config.py
    echo    - modules folder and its files
    echo.
    echo 2. Re-extract the archive
    echo    - All files must be together
    echo.
    echo 3. Files may be corrupted
    echo    - Re-download original files
    echo ========================================
    pause
    exit /b 1
)
echo [OK] All required files exist
echo.

REM Create __init__.py
if not exist modules\__init__.py (
    echo # modules package > modules\__init__.py
)

REM Create manifest file
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
REM Step 5: Clean Previous Build
REM ========================================
echo [5/6] Cleaning previous build...
if exist build (
    rmdir /s /q build >nul 2>&1
)
if exist dist (
    rmdir /s /q dist >nul 2>&1
)
if exist GThey5M.spec (
    del GThey5M.spec >nul 2>&1
)
echo [OK] Cleanup complete
echo.

REM ========================================
REM Step 6: Start Build
REM ========================================
echo [6/6] Starting build (1-2 minutes)
echo.
echo Building... Please wait.
echo.
echo.

REM Execute build
if exist icon.ico (
    %PYTHON% -m PyInstaller --onefile --noconsole --name=GThey5M --manifest=GThey5M.manifest --uac-admin --clean --noconfirm --hidden-import=keyboard --hidden-import=pystray --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageDraw --add-data "config.py;." --add-data "modules;modules" --add-data "icon.ico;." --icon=icon.ico main.py >build_log.txt 2>&1
) else (
    %PYTHON% -m PyInstaller --onefile --noconsole --name=GThey5M --manifest=GThey5M.manifest --uac-admin --clean --noconfirm --hidden-import=keyboard --hidden-import=pystray --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageDraw --add-data "config.py;." --add-data "modules;modules" main.py >build_log.txt 2>&1
)

if %errorlevel% neq 0 (
    echo [FAIL] Build error occurred
    echo.
    echo ========================================
    echo Check error log:
    echo ========================================
    echo Full log available in build_log.txt file.
    echo.
    echo ========================================
    echo Common solutions:
    echo ========================================
    echo 1. Check disk space
    echo    - Minimum 500MB required
    echo.
    echo 2. Check antivirus
    echo    - Antivirus may block build
    echo    - Temporarily disable and retry
    echo.
    echo 3. Run as administrator
    echo    - Right-click build.bat
    echo    - "Run as administrator"
    echo.
    echo 4. Check path for Korean characters
    echo    - Change folder name to English
    echo.
    echo 5. Reinstall PyInstaller
    echo    - pip uninstall pyinstaller
    echo    - pip install pyinstaller
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================

REM ========================================
REM Check Build Result
REM ========================================
if exist dist\GThey5M.exe (
    echo.
    echo [OK] Executable created successfully!
    echo.
    
    REM Copy to desktop
    set DESKTOP=%USERPROFILE%\Desktop
    copy /Y dist\GThey5M.exe "!DESKTOP!\GThey5M.exe" >nul 2>&1
    
    if exist "!DESKTOP!\GThey5M.exe" (
        echo [OK] Copied to desktop!
        echo      Location: !DESKTOP!\GThey5M.exe
    ) else (
        echo [WARN] Desktop copy failed
        echo        Manual copy: dist\GThey5M.exe
    )
    
    echo.
    echo ========================================
    echo Important Notes:
    echo ========================================
    echo - Antivirus may block (allow in settings)
    echo - Must run with administrator privileges
    echo - Need to rebuild after modifying config.py
    echo ========================================
    
) else (
    echo.
    echo (Ignorable warning)
    echo [WARN] dist\GThey5M.exe not created
    echo.
    echo ========================================
    echo Solutions:
    echo ========================================
    echo 1. Check build_log.txt file
    echo    - Contains detailed error info
    echo.
    echo 2. Try again
    echo    - Run build.bat again
    echo.
    echo 3. Check antivirus
    echo    - Pause real-time scanning
    echo ========================================
)

echo.
pause