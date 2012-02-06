@echo off
::Tells other scripts where to get python and other utilities
set PATH=%~pd0;%~pd0\bin;%PATH%

set TMP_PATH=%~pd0\..\tmp
set PY_PATH=%~pd0\..\python

if not exist "%TMP_PATH%" mkdir %TMP_PATH%

set PYTHON_TAR_FN=Python-2.7.2.tar.bz2
set PYTHON_TAR=%TMP_PATH%\%PYTHON_TAR_FN%
set PYTHON_TAR_XFOLDER=Python-2.7.2
set PYTHON_URL=http://www.python.org/ftp/python/2.7.2/Python-2.7.2.tar.bz2

set DISTRIBUTE_URL=http://python-distribute.org/distribute_setup.py