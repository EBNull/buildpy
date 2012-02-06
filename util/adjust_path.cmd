@echo off
setlocal
set PWD=%CD%
set HERE=%~pd0
set OLDPATH=%PATH%

cd /d %HERE%

call set_python_env_vars.cmd

endlocal & set OLDPATH=%PATH%&set PATH=%PY_DIR%;%PYTHON_SCRIPTS%;%PATH%