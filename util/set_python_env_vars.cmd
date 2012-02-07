@echo off
::Tells other scripts where to get python and other utilities

setlocal
::want absolute dir name of parent directory, this is the only way I know how to get it
set HERE=%~pd0
set OLDCWD=%CD%
cd /d %HERE%\..
set BASEPATH=%CD%
cd /d %OLDCWD%
endlocal & set BASEPATH=%BASEPATH%

set PATH=%~pd0;%~pd0\bin;%PATH%


set TMP_PATH=%BASEPATH%\tmp
set PY_PATH=%BASEPATH%\python

if not exist "%TMP_PATH%" mkdir %TMP_PATH%


set PY_MAJOR=2
set PY_MINOR=7
set PY_REL=2
set PY_VER_SMALL=%PY_MAJOR%.%PY_MINOR%
set PY_VER_FULL=%PY_MAJOR%.%PY_MINOR%.%PY_REL%

set PYTHON_TAR_FN=Python-2.7.2.tar.bz2
set PYTHON_TAR=%TMP_PATH%\%PYTHON_TAR_FN%
set PYTHON_TAR_XFOLDER=Python-2.7.2
set PYTHON_URL=http://www.python.org/ftp/python/2.7.2/Python-2.7.2.tar.bz2





::Needed post-build

set PY_DIR=%PY_PATH%\PCBuild
set PYTHON=%PY_DIR%\python.exe
set PYTHON_D=%PY_DIR%\python_d.exe
set PYTHON_SCRIPTS=%PY_PATH%\Scripts

set DISTRIBUTE_URL=http://python-distribute.org/distribute_setup.py
set PYWIN32_INSTALL=%PYTHON% %~pd0\install_pywin32.py