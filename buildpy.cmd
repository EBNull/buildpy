@echo off
setlocal
set PWD=%CD%
set HERE=%~pd0
set OLDPATH=%PATH%

cd /d %HERE%

call util\set_python_env_vars.cmd

if exist %PYTHON% goto no_download_build

call util\download_python.cmd
call util\build_python.cmd
goto cont

:no_download_build
echo Python already exists, not downloading / rebuilding

:cont
call util\postbuild_setup.cmd