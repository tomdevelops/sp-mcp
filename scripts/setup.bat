@echo off
setlocal enabledelayedexpansion

echo ============================================
echo Super Productivity MCP Bridge Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3 is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed or not in PATH
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo Installing MCP dependencies...
pip install mcp

if errorlevel 1 (
    echo ERROR: Failed to install MCP dependencies
    pause
    exit /b 1
)

REM Create data directory
set "MCP_DIR=%LOCALAPPDATA%\super-productivity-mcp"

echo Creating MCP directory: %MCP_DIR%
if not exist "%MCP_DIR%" mkdir "%MCP_DIR%"
if not exist "%MCP_DIR%\plugin_commands" mkdir "%MCP_DIR%\plugin_commands"
if not exist "%MCP_DIR%\plugin_responses" mkdir "%MCP_DIR%\plugin_responses"

REM Copy MCP server to data directory (from parent directory)
echo Copying MCP server...
set "SCRIPT_DIR=%~dp0"
copy "%SCRIPT_DIR%..\mcp_server.py" "%MCP_DIR%\mcp_server.py" >nul
copy "%SCRIPT_DIR%..\merge_config.py" "%MCP_DIR%\merge_config.py" >nul

REM Create start script
echo Creating start script...
(
echo @echo off
echo echo Starting Super Productivity MCP Server...
echo cd /d "%MCP_DIR%"
echo python mcp_server.py
echo pause
) > "%MCP_DIR%\start_mcp_server.bat"

echo.
echo ============================================
echo MCP Server Setup Complete!
echo ============================================
echo.

REM Ask about Claude Desktop setup
set /p CLAUDE_CHOICE="Do you want to configure Claude Desktop? (y/N): "
if /i "%CLAUDE_CHOICE%"=="y" (
    echo Setting up Claude Desktop...
    call "%SCRIPT_DIR%setup-claude.bat" "%MCP_DIR%"
) else (
    echo Skipping Claude Desktop setup.
)

echo.

REM Ask about Open Code setup
set /p OPENCODE_CHOICE="Do you want to configure Open Code? (y/N): "
if /i "%OPENCODE_CHOICE%"=="y" (
    echo Setting up Open Code...
    call "%SCRIPT_DIR%setup-opencode.bat" "%MCP_DIR%"
) else (
    echo Skipping Open Code setup.
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Install the plugin in Super Productivity:
echo    - Open Super Productivity
echo    - Go to Settings ^> Plugins
echo    - Click "Upload Plugin"
echo    - Select the sp-mcp-bridge-v*.zip file from the parent folder
echo.
echo 2. Restart your configured applications to load the MCP server
echo.
echo 3. Test the integration by asking your AI assistant to:
echo    "Create a task in Super Productivity"
echo.
echo MCP Server installed at: %MCP_DIR%
echo.
pause