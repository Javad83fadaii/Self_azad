@echo off
setlocal

set "ROOT_DIR=%~dp0"
pushd "%ROOT_DIR%"

if exist "%ROOT_DIR%.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%ROOT_DIR%.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)
set "DIST_DIR=%ROOT_DIR%dist\UFRSStudentDesktop"
set "ISCC_EXE="

where ISCC.exe >nul 2>nul
if %errorlevel%==0 (
    set "ISCC_EXE=ISCC.exe"
) else (
    if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
        set "ISCC_EXE=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    ) else (
        if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
            set "ISCC_EXE=%ProgramFiles%\Inno Setup 6\ISCC.exe"
        )
    )
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
if not exist "%DIST_DIR%\config" mkdir "%DIST_DIR%\config"
copy /Y "%ROOT_DIR%desktop.env.example" "%DIST_DIR%\config\desktop.env.example" >nul
if errorlevel 1 goto :error
copy /Y "%ROOT_DIR%.env.production.example" "%DIST_DIR%\config\backend.production.env.example" >nul
if errorlevel 1 goto :error
copy /Y "%ROOT_DIR%README.md" "%DIST_DIR%\README.md" >nul
if errorlevel 1 goto :error

echo [4/4] Checking optional installer compiler...
if defined ISCC_EXE (
    echo Inno Setup detected. Building installer...
    call "%ISCC_EXE%" "%ROOT_DIR%installer\ufrs_student_desktop.iss"
) else (
    echo Inno Setup compiler not found. Installer script is ready at installer\ufrs_student_desktop.iss
)

echo.
echo Build completed successfully.
echo Output folder: %DIST_DIR%
popd
goto :eof

:error
echo.
echo Build failed.
popd
exit /b 1
