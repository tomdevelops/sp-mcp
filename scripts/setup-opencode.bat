@echo off
setlocal enabledelayedexpansion

set "MCP_DIR=%~1"

if "%MCP_DIR%"=="" (
    echo ERROR: MCP directory not provided
    pause
    exit /b 1
)

echo Configuring Open Code...

REM Determine Open Code config location
set "OPENCODE_CONFIG=%APPDATA%\opencode\config.json"

REM Create Open Code config directory if it doesn't exist
if not exist "%APPDATA%\opencode" mkdir "%APPDATA%\opencode"

REM Check if config file exists and merge
if exist "%OPENCODE_CONFIG%" (
    echo Backing up existing Open Code config...
    copy "%OPENCODE_CONFIG%" "%OPENCODE_CONFIG%.backup" >nul

    echo Adding super-productivity to existing MCP servers...
    echo Merging with existing Open Code configuration...

    python "%MCP_DIR%\merge_config.py" "%OPENCODE_CONFIG%" "%MCP_DIR%"

    if errorlevel 1 (
        echo ERROR: Failed to merge configuration. Your backup is at %OPENCODE_CONFIG%.backup
        echo Please manually add this to your Open Code config.json:
        echo.
        echo   "mcp": {
        echo     "super-productivity": {
        echo       "type": "local",
        echo       "command": ["python", "%MCP_DIR%\mcp_server.py"],
        echo       "enabled": true
        echo     }
        echo   }
        echo.
        pause
        exit /b 1
    )
) else (
    echo Creating new Open Code configuration...
    (
        echo {
        echo   "$schema": "https://opencode.ai/config.json",
        echo   "mcp": {
        echo     "super-productivity": {
        echo       "type": "local",
        echo       "command": [
        echo         "python",
        echo         "%MCP_DIR:\=\\%\\mcp_server.py"
        echo       ],
        echo       "enabled": true
        echo     }
        echo   }
        echo }
    ) > "%OPENCODE_CONFIG%"
)

echo ✓ Open Code configuration updated at: %OPENCODE_CONFIG%