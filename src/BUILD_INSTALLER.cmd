@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Hela Jyotishya - Commercial Licensed Installer Builder

echo ======================================================
echo   HELA JYOTISHYA - TRIAL + PAID COMMERCIAL BUILDER
echo ======================================================
echo.

set "PYCMD="
py -3.12 -c "import sys;print(sys.version)" >nul 2>nul && set "PYCMD=py -3.12"
if not defined PYCMD py -3 -c "import sys;print(sys.version)" >nul 2>nul && set "PYCMD=py -3"
if not defined PYCMD python -c "import sys;print(sys.version)" >nul 2>nul && set "PYCMD=python"
if not defined PYCMD (
  echo Python 3 was not found.
  echo Install Python 3.12 and run this file again.
  pause
  exit /b 1
)

if not exist ".builder\Scripts\python.exe" (
  echo [1/6] Creating build environment...
  %PYCMD% -m venv .builder
  if errorlevel 1 goto :fail
) else (
  echo [1/6] Build environment already exists.
)

echo [2/6] Installing build tools...
".builder\Scripts\python.exe" -m pip install --upgrade pip >nul
".builder\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 goto :fail

echo [3/6] Running application and licensing self-tests...
set PYTHONDONTWRITEBYTECODE=1
".builder\Scripts\python.exe" -B -c "import sys;sys.path.insert(0,'app');import server;assert server.self_test();print('Astrology self-test OK')"
if errorlevel 1 goto :fail
".builder\Scripts\python.exe" -B -c "import license_client;assert license_client.self_test();print('License self-test OK')"
if errorlevel 1 goto :fail

echo [4/6] Checking commercial configuration...
".builder\Scripts\python.exe" -B CHECK_COMMERCIAL_CONFIG.py
if errorlevel 2 goto :fail

echo [5/6] Building desktop executable...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
".builder\Scripts\pyinstaller.exe" --clean --noconfirm HelaJyotishya.spec
if errorlevel 1 goto :fail

echo [5b/6] Testing packaged EXE dependencies...
"%CD%\dist\HelaJyotishya.exe" --package-self-test
if errorlevel 1 (
  echo.
  echo Packaged EXE self-test failed. SQLite or another runtime component is missing.
  goto :fail
)
echo Packaged EXE self-test OK.

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC (
  echo.
  echo Inno Setup 6 is not installed. Trying winget...
  where winget >nul 2>nul
  if not errorlevel 1 (
    winget install --id JRSoftware.InnoSetup -e --accept-source-agreements --accept-package-agreements
    if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
  )
)
if not defined ISCC (
  echo.
  echo HelaJyotishya.exe was built successfully, but Inno Setup is missing.
  echo Install Inno Setup 6, then run BUILD_INSTALLER.cmd again.
  pause
  exit /b 2
)

echo [6/6] Building Setup.exe...
if not exist release mkdir release
"%ISCC%" installer\HelaJyotishya.iss
if errorlevel 1 goto :fail

echo.
echo ======================================================
echo SUCCESS - TRIAL + PAID INSTALLER CREATED
for %%F in (release\Hela_Jyotishya_Setup*.exe) do echo Installer: %%~fF
echo ======================================================
echo.
explorer "%CD%\release"
pause
exit /b 0

:fail
echo.
echo BUILD FAILED. Keep this window open and send a screenshot of the error.
pause
exit /b 1
