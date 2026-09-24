@echo off
setlocal

set "ROOT_DIR=%~dp0"
if exist "%ROOT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%ROOT_DIR%.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [1/4] Installing runtime and build dependencies...
call "%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 goto :error
call "%PYTHON_EXE%" -m pip install -r "%ROOT_DIR%requirements.txt"
if errorlevel 1 goto :error
call "%PYTHON_EXE%" -m pip install pyinstaller
if errorlevel 1 goto :error

echo [2/4] Building Windows desktop package with PyInstaller...
call "%PYTHON_EXE%" -m PyInstaller --noconfirm --clean "%ROOT_DIR%ufrs_student_desktop.spec"
if errorlevel 1 goto :error

echo [3/4] Preparing runtime configuration files...
if not exist "%ROOT_DIR%dist\UFRSStudentDesktop\config" mkdir "%ROOT_DIR%dist\UFRSStudentDesktop\config"
copy /Y "%ROOT_DIR%.env.example" "%ROOT_DIR%dist\UFRSStudentDesktop\config\desktop.env.example" >nul
copy /Y "%ROOT_DIR%README.md" "%ROOT_DIR%dist\UFRSStudentDesktop\README.md" >nul

echo [4/4] Checking optional installer compiler...
where ISCC.exe >nul 2>nul
if %errorlevel%==0 (
    echo Inno Setup detected. Building installer...
    call ISCC.exe "%ROOT_DIR%installer\ufrs_student_desktop.iss"
) else (
    echo Inno Setup compiler not found. Installer script is ready at installer\ufrs_student_desktop.iss
)

echo.
echo Build completed successfully.
echo Output folder: %ROOT_DIR%dist\UFRSStudentDesktop
goto :eof

:error
echo.
echo Build failed.
exit /b 1
