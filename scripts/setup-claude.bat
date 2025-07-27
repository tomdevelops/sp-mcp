@echo off
setlocal enabledelayedexpansion

set "MCP_DIR=%~1"

if "%MCP_DIR%"=="" (
    echo ERROR: MCP directory not provided
    pause
    exit /b 1
)

echo Configuring Claude Desktop...

REM Determine Claude config location
set "CLAUDE_CONFIG=%APPDATA%\Claude\claude_desktop_config.json"

REM Create Claude config directory if it doesn't exist
if not exist "%APPDATA%\Claude" mkdir "%APPDATA%\Claude"

REM Check if config file exists and merge
if exist "%CLAUDE_CONFIG%" (
    echo Backing up existing Claude config...
    copy "%CLAUDE_CONFIG%" "%CLAUDE_CONFIG%.backup" >nul

    echo Adding super-productivity to existing MCP servers...
    echo Merging with existing Claude Desktop configuration...

    python "%MCP_DIR%\merge_config.py" "%CLAUDE_CONFIG%" "%MCP_DIR%"

    if errorlevel 1 (
        echo ERROR: Failed to merge configuration. Your backup is at %CLAUDE_CONFIG%.backup
        echo Please manually add this to your Claude Desktop config:
        echo.
        echo   "super-productivity": {
        echo     "command": "python",
        echo     "args": ["%MCP_DIR%\mcp_server.py"]
        echo   }
        echo.
        pause
        exit /b 1
    )
) else (
    echo Creating new Claude Desktop configuration...
    (
        echo {
        echo   "mcpServers": {
        echo     "super-productivity": {
        echo       "command": "python",
        echo       "args": ["%MCP_DIR:\=\\%\\mcp_server.py"]
        echo     }
        echo   }
        echo }
    ) > "%CLAUDE_CONFIG%"
)

echo ✓ Claude Desktop configuration updated at: %CLAUDE_CONFIG%