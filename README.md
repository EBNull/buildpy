Rationale
---------

The process of developing (anything, really) on Windows can be quite
cumbersome compared to linux. In particular, when developing Python extentions
or debugging programs that embed python, it is often useful to be able to step through
python's source code or run under the debug version of Python.

For a user unfamiliar with the subtlies of building python, and also for easily replicating
build environments on fresh windows installations, a better method was desired.

Goals
------------

Given a barebones windows install, without any dependancies except for VS 2008, download
and build python (release and debug) and install easy_install and pip.


Dependancies
------------

Windows has no command line method to download executables from the internet. As such,
this project packages wget.exe. It also cannot natively extract tar.bz2 files, which the
Python source resides in. Thus, this also bundles tar.exe and bunzip2.exe.

These binaries are from the http://unxutils.sourceforge.net/ project. Specifically, they were
acquired on 2012-02-05 from http://sourceforge.net/projects/unxutils/files/unxutils/current/UnxUtils.zip/download
in the file UnxUtils.zip dated 2007-03-01.

Usage
-----

Download & Build:

git clone git://github.com/CBWhiz/buildpy.git
cd buildpy
buildpy.cmd

Install to system:

util\system_install.cmd -v C:\Python27

