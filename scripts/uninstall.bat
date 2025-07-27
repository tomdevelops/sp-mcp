@echo off
setlocal enabledelayedexpansion

REM Super Productivity MCP Server Uninstaller for Windows
REM This script reverts all changes made by setup.bat

echo 🗑️  Uninstalling Super Productivity MCP Server...

REM Set config paths for Windows
set "CLAUDE_CONFIG_DIR=%APPDATA%\Claude"
set "CLAUDE_CONFIG=%CLAUDE_CONFIG_DIR%\claude_desktop_config.json"
set "OPENCODE_CONFIG_DIR=%APPDATA%\opencode"
set "OPENCODE_CONFIG=%OPENCODE_CONFIG_DIR%\opencode.json"

REM Function to print status messages
call :print_status "Starting uninstallation process..."

REM Remove MCP configurations
call :remove_mcp_config

REM Remove data directories
call :remove_data_directories

echo.
call :print_status "🎉 Uninstallation completed!"
echo.
call :print_status "The following items have been removed/reverted:"
call :print_status "✅ MCP server configuration from Claude and OpenCode (if found)"
call :print_warning "Note: The project files in %CD% have been kept."
call :print_warning "If you want to completely remove the project, delete this directory manually."
call :print_status "To reinstall, run: setup.bat"

pause
exit /b 0

:print_status
echo [INFO] %~1
exit /b

:print_warning
echo [WARN] %~1
exit /b

:print_error
echo [ERR] %~1
exit /b

:remove_mcp_config
set "config_removed=false"

REM Remove from Claude configuration
if exist "%CLAUDE_CONFIG%" (
    call :print_status "Removing MCP server configuration from Claude..."

    REM Create backup of current config
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
    set "timestamp=!dt:~0,8!_!dt:~8,6!"
    copy "%CLAUDE_CONFIG%" "%CLAUDE_CONFIG%.uninstall.backup.!timestamp!" >nul
    call :print_status "Backup created: %CLAUDE_CONFIG%.uninstall.backup.!timestamp!"

    REM Check if jq is available
    where jq >nul 2>&1
    if !errorlevel! equ 0 (
        REM Use jq to remove the server entry
        jq "del(.mcpServers.\"super-productivity\")" "%CLAUDE_CONFIG%" > "%CLAUDE_CONFIG%.tmp"
        if !errorlevel! equ 0 (
            move "%CLAUDE_CONFIG%.tmp" "%CLAUDE_CONFIG%" >nul
            call :print_status "✅ MCP server configuration removed from Claude"
            set "config_removed=true"
        ) else (
            del "%CLAUDE_CONFIG%.tmp" >nul 2>&1
            call :print_warning "Failed to remove configuration with jq"
        )
    ) else (
        call :print_warning "jq not found. You may need to manually remove the super-productivity entry from %CLAUDE_CONFIG%"
    )
) else (
    call :print_warning "Claude config file not found at %CLAUDE_CONFIG%"
)

REM Remove from OpenCode configuration
if exist "%OPENCODE_CONFIG%" (
    call :print_status "Removing MCP server configuration from OpenCode..."

    REM Create backup of current config
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
    set "timestamp=!dt:~0,8!_!dt:~8,6!"
    copy "%OPENCODE_CONFIG%" "%OPENCODE_CONFIG%.uninstall.backup.!timestamp!" >nul
    call :print_status "Backup created: %OPENCODE_CONFIG%.uninstall.backup.!timestamp!"

    REM Check if jq is available
    where jq >nul 2>&1
    if !errorlevel! equ 0 (
        REM Use jq to remove the server entry
        jq "del(.mcp.\"super-productivity\")" "%OPENCODE_CONFIG%" > "%OPENCODE_CONFIG%.tmp"
        if !errorlevel! equ 0 (
            move "%OPENCODE_CONFIG%.tmp" "%OPENCODE_CONFIG%" >nul
            call :print_status "✅ MCP server configuration removed from OpenCode"
            set "config_removed=true"
        ) else (
            del "%OPENCODE_CONFIG%.tmp" >nul 2>&1
            call :print_warning "Failed to remove configuration with jq"
        )
    ) else (
        call :print_warning "jq not found. You may need to manually remove the super-productivity entry from %OPENCODE_CONFIG%"
    )
) else (
    call :print_warning "OpenCode config file not found at %OPENCODE_CONFIG%"
)

if "!config_removed!" == "false" (
    call :print_warning "No MCP configurations found to remove"
)
exit /b

:remove_data_directories
REM Set data directory for Windows
set "DATA_DIR=%APPDATA%\super-productivity-mcp"

if exist "%DATA_DIR%" (
    call :print_status "Removing MCP data directory at %DATA_DIR%..."
    set /p "confirm=Are you sure you want to remove all MCP data? This cannot be undone. (y/N): "
    if /i "!confirm!" == "y" (
        rmdir /s /q "%DATA_DIR%"
        call :print_status "✅ MCP data directory removed"
    ) else (
        call :print_warning "Skipped removing MCP data directory"
    )
) else (
    call :print_warning "MCP data directory not found at %DATA_DIR%"
)
exit /b