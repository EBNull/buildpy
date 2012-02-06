@echo off
setlocal
set PWD=%CD%
set HERE=%~pd0
set OLDPATH=%PATH%

cd /d %HERE%

call set_python_env_vars.cmd

:get_python
if exist %PYTHON_TAR% goto extract_python
echo Downloading python from %PYTHON_URL%
wget -O %PYTHON_TAR% %PYTHON_URL%

:extract_python
echo off
cd /d %PYTHON_TAR%\..
echo Extracting python from %PYTHON_TAR_FN% to %CD%
bunzip2 -c %PYTHON_TAR_FN% | tar -x
if exist %PY_PATH% rmdir /s /q %PY_PATH%
move /Y %PYTHON_TAR_XFOLDER% %PY_PATH%
cd /d %PY_PATH%
set pp=%CD%
cd /d %HERE%
echo Python source downloaded and extracted to %pp%
