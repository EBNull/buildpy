@echo off
setlocal
set PWD=%CD%
set HERE=%~pd0
set OLDPATH=%PATH%

cd /d %HERE%

call set_python_env_vars.cmd

%PYTHON% %HERE%\system_install.py %1 %2 %3 %4 %5 %6 %7 %8 %9

endlocal