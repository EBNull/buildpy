@echo off
setlocal
set PWD=%CD%
set HERE=%~pd0
set OLDPATH=%PATH%

if not DEFINED PY_DIR goto nopy

cd /d %HERE%

call set_python_env_vars.cmd

:install_distribute

wget -O %TMP_PATH%\distribute_setup.py %DISTRIBUTE_URL%
"%PY_DIR%\python.exe" %TMP_PATH%\distribute_setup.py

:install_packages
"%PY_DIR%\..\Scripts\easy_install.exe" pip
"%PY_DIR%\..\Scripts\pip.exe" install virtualenv
goto end

:nopy
echo PY_DIR not set, are you running this directly?

:end
cd /d %PWD%