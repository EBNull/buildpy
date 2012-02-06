@echo off
::This file looks for VS9 and exports %VS9% as the visual studio path, and runs vcvarsall.bat
::    to allow ms's utils to be on the path.
::
:: You can specify the compiler as the first argument, as seen at
::    http://msdn.microsoft.com/en-us/library/x4d2c09s%28v=vs.80%29.aspx
::
:: Examples:
::    vs9_env.cmd x86          (Default, native 32 bit -> 32 bit)
::    vs9_env.cmd x86_amd64    (native 32 bit -> 64 bit)
::    vs9_env.cmd amd64        (native 64 bit -> 64 bit)
::    vs9_env.cmd              (same as vs9_env.cmd x86)
::
::
::SETLOCAL / ENDLOCAL trick
::    All cmd files should begin with setlocal.
::    To export an env var, you can use endlocal& set var=%var%&set var2=%var2
::    Spaces are important.
::
:: Alternatively, use the multiple return technique here: http://ss64.com/nt/endlocal.html
::
setlocal
set PWD=%CD%
set HERE=%~pd0

cd /d %HERE%

:set_vs9_env
setlocal
    set pf=
    if exist "%ProgramFiles(x86)%" set pf=%ProgramFiles(x86)%
    if not exist "%pf%" set pf=%ProgramFiles%
    set VS9=%pf%\Microsoft Visual Studio 9.0
endlocal & set VS9=%VS9%
if not exist "%VS9%\VC\vcvarsall.bat" goto novs9

:hasvs9
endlocal & set VS9=%VS9%& set PWD=%PWD%
::%1 == compiler
call "%VS9%\VC\vcvarsall.bat" %1 
goto end

:novs9
set VS9=
endlocal & set PWD=%PWD%
echo Visual Studio 9.0 (2008) was not found.
echo.

:end
cd /d %PWD%

echo.
echo.