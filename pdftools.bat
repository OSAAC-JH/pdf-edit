@echo off
REM pdftools.bat - KBFG PDF Tools launcher (Windows)
REM
REM Double-click this file to start the interactive menu.
REM Or pass arguments to run a subcommand directly, e.g.:
REM   pdftools.bat split input.pdf --pages "1,3-5"
REM
REM NOTE: This file is kept plain-ASCII on purpose. Korean text inside a
REM .bat file saved as UTF-8 can be misread by Korean-locale cmd.exe
REM (default code page 949), which corrupts REM comments and breaks
REM command parsing. All Korean text lives in pdftools.py instead, and
REM "chcp 65001" below makes the console display it correctly.

chcp 65001 >nul

setlocal
set SCRIPT_DIR=%~dp0

REM Activate the virtual environment if one exists
if exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    call "%SCRIPT_DIR%venv\Scripts\activate.bat"
)

python "%SCRIPT_DIR%pdftools.py" %*
set PDFTOOLS_EXIT_CODE=%ERRORLEVEL%

REM Keep the window open only when double-clicked with no arguments
if "%~1"=="" (
    echo.
    pause
)

exit /b %PDFTOOLS_EXIT_CODE%
