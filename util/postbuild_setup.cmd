@echo off
setlocal
set PWD=%CD%
set HERE=%~pd0
set OLDPATH=%PATH%

cd /d %HERE%

call set_python_env_vars.cmd

:install_distribute
wget -O %TMP_PATH%\distribute_setup.py %DISTRIBUTE_URL%
"%PY_DIR%\python.exe" %TMP_PATH%\distribute_setup.py

:install_pywin32
"%PYTHON%" "%HERE%\install_pywin32.py"

:install_packages
"%PY_DIR%\..\Scripts\easy_install.exe" pip
::virtualenv 1.7 has an issue creating virtualenvs from a python build directory.
::see https://github.com/pypa/virtualenv/issues/139 for more information
::"%PY_DIR%\..\Scripts\pip.exe" install virtualenv
"%PY_DIR%\..\Scripts\pip.exe" install git+https://github.com/pypa/virtualenv.git#egg=virtualenv


goto end

:nopy
echo PY_DIR not set, are you running this directly?

:end
cd /d %PWD%