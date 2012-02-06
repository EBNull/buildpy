@echo off
::Compiles python
::Sets PY_DIR env var to built directory
setlocal
set PWD=%CD%
set HERE=%~pd0
set OLDPATH=%PATH%

cd /d %HERE%

call set_python_env_vars.cmd
call vs9_env.cmd

echo %VS9%
if not exist "%VS9%" goto novs9
goto build_python

:novs9
echo Visual Studio 9.0 (2008) was not found.
echo.
goto end

:build_python
echo VS9 found at "%VS9%"
echo.
cd %PY_PATH%\PCBuild

if exist python.exe echo Skipping python.exe compile (already exists)
if not exist python.exe call build.bat
if exist python_d.exe echo Skipping python_d.exe compile (already exists)
if not exist python_d.exe call build.bat -d
echo.
if exist python.exe echo python.exe created
if exist python_d.exe echo python_d.exe created


endlocal

:end
cd /d %HERE%