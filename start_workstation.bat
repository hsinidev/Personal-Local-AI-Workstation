@echo off
title Personal Local AI Workstation v2.0 - Developed by Hsini Mohamed
color 0B

echo =====================================================================
echo   🚀 PERSONAL LOCAL AI WORKSTATION v2.0 (ADVANCED RAG SUITE)
echo   👨‍💻 Developed by: Hsini Mohamed (hsini.jk@gmail.com)
echo   🌐 Portfolio: https://hsini.dev
echo =====================================================================
echo.
echo [*] Initializing Workstation Environment...
python launcher.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Python execution encountered an issue.
    echo [*] Attempting direct fallback dashboard launch...
    python apps\dashboard\serve.py
)

pause
