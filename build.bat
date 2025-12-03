@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

echo ========================================
echo KeyM Build System
echo ========================================
echo.

REM ========================================
REM Step 0: Check if KeyM is Running
REM ========================================
echo [0/6] Checking for running KeyM...
tasklist /FI "IMAGENAME eq KeyM.exe" 2>NUL | find /I /N "KeyM.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo.
    echo ========================================
    echo [STOP] KeyM.exe is Currently Running
    echo ========================================
    echo.
    echo Please close KeyM before building:
    echo.
    echo Method 1: Force Quit Key
    echo    - Press ALT + SHIFT + DEL simultaneously
    echo.
    echo Method 2: System Tray
    echo    - Right-click KeyM icon in tray
    echo    - Select "Exit" or similar option
    echo.
    echo Method 3: Task Manager
    echo    - Press Ctrl + Shift + Esc
    echo    - Find "KeyM.exe"
    echo    - Click "End Task"
    echo.
    echo After closing KeyM, run build.bat again.
    echo ========================================
    pause
    exit /b 1
)
echo [OK] No running KeyM detected
echo.

REM ========================================
REM Step 1: Check Python Installation
REM ========================================
echo [1/6] Checking Python installation...
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=python
    echo [OK] Python found: python
) else (
    set PYTHON=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe
    if exist "!PYTHON!" (
        echo [OK] Python found: !PYTHON!
    ) else (
        echo [FAIL] Python not found
        echo.
        echo ========================================
        echo How to Fix: Install Python
        echo ========================================
        echo.
        echo Step 1: Download Python
        echo    - Visit: https://python.org
        echo    - Click "Download Python 3.x"
        echo.
        echo Step 2: Install Python
        echo    - Run the downloaded installer
        echo    - IMPORTANT: Check "Add Python to PATH"
        echo    - Click "Install Now"
        echo.
        echo Step 3: Verify Installation
        echo    - Open new Command Prompt
        echo    - Type: python --version
        echo    - Should show Python version
        echo.
        echo Step 4: Run build.bat again
        echo.
        echo Alternative: Manual Path Configuration
        echo    - Find Python installation path
        echo    - Edit build.bat line 56
        echo    - Change: set PYTHON=C:\YourPath\python.exe
        echo ========================================
        pause
        exit /b 1
    )
)

%PYTHON% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Python execution error
    echo.
    echo ========================================
    echo How to Fix: Python Corrupted
    echo ========================================
    echo.
    echo Your Python installation may be corrupted.
    echo.
    echo Solution:
    echo    1. Uninstall Python
    echo       - Settings ^> Apps ^> Python
    echo       - Click Uninstall
    echo.
    echo    2. Download fresh installer
    echo       - Visit: https://python.org
    echo.
    echo    3. Reinstall Python
    echo       - Remember to check "Add to PATH"
    echo.
    echo    4. Run build.bat again
    echo ========================================
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
    echo [FAIL] Required libraries missing
    echo.
    echo ========================================
    echo How to Fix: Install Libraries
    echo ========================================
    echo.
    echo Automatic Installation:
    echo    1. Make sure you have internet connection
    echo    2. Run this command:
    echo       python -m pip install -r requirements.txt
    echo.
    echo    3. If you see errors, try:
    echo       python -m pip install --upgrade pip
    echo       python -m pip install -r requirements.txt
    echo.
    echo Manual Installation:
    echo    Run these commands one by one:
    echo    - python -m pip install keyboard==0.13.5
    echo    - python -m pip install pystray
    echo    - python -m pip install Pillow
    echo.
    echo Common Issues:
    echo    - "Access Denied" error
    echo      ^> Run Command Prompt as Administrator
    echo.
    echo    - "No module named pip"
    echo      ^> Reinstall Python with pip option checked
    echo.
    echo    - Firewall blocking
    echo      ^> Temporarily disable antivirus/firewall
    echo.
    echo After installing, run build.bat again.
    echo ========================================
    pause
    exit /b 1
)
echo [OK] All libraries verified
echo.

REM ========================================
REM Step 3: Check PyInstaller
REM ========================================
echo [3/6] Checking PyInstaller...
%PYTHON% -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] PyInstaller not installed
    echo.
    echo ========================================
    echo How to Fix: Install PyInstaller
    echo ========================================
    echo.
    echo Run this command:
    echo    python -m pip install pyinstaller
    echo.
    echo If you see errors:
    echo    1. Update pip first:
    echo       python -m pip install --upgrade pip
    echo.
    echo    2. Install PyInstaller:
    echo       python -m pip install pyinstaller
    echo.
    echo    3. If still failing:
    echo       - Run Command Prompt as Administrator
    echo       - Try the commands again
    echo.
    echo After installing, run build.bat again.
    echo ========================================
    pause
    exit /b 1
)
echo [OK] PyInstaller ready
echo.

REM ========================================
REM Step 4: Check Required Files
REM ========================================
echo [4/6] Checking required files...
set MISSING_FILES=0
set MISSING_LIST=

if not exist "main.py" (
    echo [FAIL] main.py not found
    set MISSING_FILES=1
    set MISSING_LIST=!MISSING_LIST! main.py
)

if not exist "config.py" (
    echo [FAIL] config.py not found
    set MISSING_FILES=1
    set MISSING_LIST=!MISSING_LIST! config.py
)

if not exist "modules\app.py" (
    echo [FAIL] modules\app.py not found
    set MISSING_FILES=1
    set MISSING_LIST=!MISSING_LIST! modules\app.py
)

if not exist "modules\core.py" (
    echo [FAIL] modules\core.py not found
    set MISSING_FILES=1
    set MISSING_LIST=!MISSING_LIST! modules\core.py
)

if not exist "modules\handler.py" (
    echo [FAIL] modules\handler.py not found
    set MISSING_FILES=1
    set MISSING_LIST=!MISSING_LIST! modules\handler.py
)

if not exist "modules\tray.py" (
    echo [FAIL] modules\tray.py not found
    set MISSING_FILES=1
    set MISSING_LIST=!MISSING_LIST! modules\tray.py
)

if !MISSING_FILES! equ 1 (
    echo.
    echo ========================================
    echo How to Fix: Missing Files
    echo ========================================
    echo.
    echo Missing files:!MISSING_LIST!
    echo.
    echo Solution 1: Re-download Project
    echo    1. Delete current folder
    echo    2. Download fresh copy from GitHub
    echo    3. Extract all files to same location
    echo.
    echo Solution 2: Check File Location
    echo    1. Make sure build.bat is in root folder
    echo    2. Verify folder structure:
    echo       Custom-Macros-master\
    echo       ├── build.bat
    echo       ├── main.py
    echo       ├── config.py
    echo       ├── requirements.txt
    echo       └── modules\
    echo           ├── app.py
    echo           ├── core.py
    echo           ├── handler.py
    echo           └── tray.py
    echo.
    echo Solution 3: Re-extract Archive
    echo    - Make sure to extract ALL files
    echo    - Don't run build.bat from inside ZIP
    echo.
    echo After fixing, run build.bat again.
    echo ========================================
    pause
    exit /b 1
)
echo [OK] All required files present
echo.

REM Create __init__.py if missing
if not exist modules\__init__.py (
    echo # modules package > modules\__init__.py
)

REM Create manifest file
(
echo ^<?xml version="1.0" encoding="UTF-8" standalone="yes"?^>
echo ^<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0"^>
echo   ^<assemblyIdentity version="1.8.0.0" processorArchitecture="*" name="KeyM" type="win32"/^>
echo   ^<description^>KeyM - Macro Chain Prevention^</description^>
echo   ^<trustInfo xmlns="urn:schemas-microsoft-com:asm.v3"^>
echo     ^<security^>
echo       ^<requestedPrivileges^>
echo         ^<requestedExecutionLevel level="requireAdministrator" uiAccess="false"/^>
echo       ^</requestedPrivileges^>
echo     ^</security^>
echo   ^</trustInfo^>
echo ^</assembly^>
) > KeyM.manifest

REM ========================================
REM Step 5: Clean Previous Build
REM ========================================
echo [5/6] Cleaning previous build files...
if exist build (
    rmdir /s /q build >nul 2>&1
    if exist build (
        echo [WARN] Could not delete build folder
        echo        This is usually fine, continuing...
    )
)
if exist dist (
    rmdir /s /q dist >nul 2>&1
    if exist dist (
        echo [WARN] Could not delete dist folder
        echo        This is usually fine, continuing...
    )
)
if exist KeyM.spec (
    del KeyM.spec >nul 2>&1
)
echo [OK] Cleanup complete
echo.

REM ========================================
REM Step 6: Start Build Process
REM ========================================
echo [6/6] Building executable...
echo.
echo This may take 1-2 minutes, please wait...
echo.

REM Execute build
if exist icon.ico (
    %PYTHON% -m PyInstaller --onefile --noconsole --name=KeyM --manifest=KeyM.manifest --uac-admin --clean --noconfirm --hidden-import=keyboard --hidden-import=pystray --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageDraw --add-data "config.py;." --add-data "modules;modules" --add-data "icon.ico;." --icon=icon.ico main.py >build_log.txt 2>&1
) else (
    %PYTHON% -m PyInstaller --onefile --noconsole --name=KeyM --manifest=KeyM.manifest --uac-admin --clean --noconfirm --hidden-import=keyboard --hidden-import=pystray --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageDraw --add-data "config.py;." --add-data "modules;modules" main.py >build_log.txt 2>&1
)

if %errorlevel% neq 0 (
    echo [FAIL] Build failed
    echo.
    echo ========================================
    echo How to Fix: Build Errors
    echo ========================================
    echo.
    echo First: Check build_log.txt for details
    echo    - Open build_log.txt in this folder
    echo    - Look for error messages at the end
    echo.
    echo Common Issues and Solutions:
    echo.
    echo 1. Disk Space
    echo    Problem: Not enough space
    echo    Solution: Free up at least 500MB
    echo.
    echo 2. Antivirus Blocking
    echo    Problem: Antivirus blocks PyInstaller
    echo    Solution:
    echo    - Add this folder to antivirus exclusions
    echo    - Temporarily disable real-time protection
    echo    - Run build.bat again
    echo    - Re-enable antivirus after build
    echo.
    echo 3. Path Too Long
    echo    Problem: Folder path has too many characters
    echo    Solution:
    echo    - Move folder closer to C:\
    echo    - Example: C:\KeyM
    echo.
    echo 4. Special Characters in Path
    echo    Problem: Path contains Korean/special chars
    echo    Solution:
    echo    - Move to path with English only
    echo    - Example: C:\KeyM
    echo.
    echo 5. Permissions
    echo    Problem: Cannot write to folder
    echo    Solution:
    echo    - Right-click build.bat
    echo    - Run as Administrator
    echo.
    echo 6. PyInstaller Corruption
    echo    Problem: PyInstaller is broken
    echo    Solution:
    echo    - python -m pip uninstall pyinstaller
    echo    - python -m pip install pyinstaller
    echo    - Run build.bat again
    echo.
    echo 7. Import Errors
    echo    Problem: Cannot find modules
    echo    Solution:
    echo    - Check all files are present
    echo    - Verify modules folder structure
    echo    - Re-download project if needed
    echo.
    echo After fixing, run build.bat again.
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Successful!
echo ========================================

REM ========================================
REM Verify Build Result
REM ========================================
if exist dist\KeyM.exe (
    echo.
    echo [OK] KeyM.exe created successfully
    echo.
    
    REM Copy to desktop
    set DESKTOP=%USERPROFILE%\Desktop
    copy /Y dist\KeyM.exe "!DESKTOP!\KeyM.exe" >nul 2>&1
    
    if exist "!DESKTOP!\KeyM.exe" (
        echo [OK] Copied to desktop
        echo      Location: !DESKTOP!\KeyM.exe
    ) else (
        echo [WARN] Could not copy to desktop
        echo        Please copy manually from: dist\KeyM.exe
        echo        To: !DESKTOP!
    )
    
    echo.
    echo ========================================
    echo Important Information
    echo ========================================
    echo.
    echo Antivirus Warning:
    echo    - Your antivirus may flag KeyM.exe
    echo    - This is normal for compiled Python apps
    echo    - Add KeyM.exe to antivirus exclusions
    echo.
    echo Administrator Rights:
    echo    - KeyM requires admin privileges
    echo    - Windows will ask for permission
    echo    - Click "Yes" when prompted
    echo.
    echo After Config Changes:
    echo    - If you edit config.py
    echo    - You must rebuild KeyM.exe
    echo    - Close KeyM first, then run build.bat
    echo.
    echo Testing:
    echo    - Run your game first
    echo    - Then start KeyM.exe
    echo    - Test macros to verify settings
    echo.
    echo Force Quit:
    echo    - Press ALT + SHIFT + DEL to exit
    echo    - Or right-click tray icon ^> Exit
    echo.
    echo Rebuild Instructions:
    echo    1. Close KeyM.exe completely
    echo    2. Run build.bat again
    echo ========================================
    
) else (
    echo.
    echo [WARN] KeyM.exe not found in dist folder
    echo.
    echo ========================================
    echo How to Fix: Executable Missing
    echo ========================================
    echo.
    echo This means build completed but file missing.
    echo.
    echo Possible Causes:
    echo    1. Antivirus deleted it immediately
    echo       - Check antivirus quarantine
    echo       - Restore KeyM.exe
    echo       - Add to exclusions
    echo.
    echo    2. Windows Defender blocked it
    echo       - Open Windows Security
    echo       - Protection History
    echo       - Restore KeyM.exe
    echo       - Allow on device
    echo.
    echo    3. File system error
    echo       - Check build_log.txt
    echo       - Look for access denied errors
    echo.
    echo Solution:
    echo    - Add folder to antivirus exclusions
    echo    - Run build.bat again
    echo ========================================
)

echo.
pause