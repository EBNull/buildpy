import os
import sys
import time
import shutil
import tempfile
import urllib2
import subprocess

VER_SMALL='.'.join(str(i) for i in sys.version_info[0:2])

URL="http://downloads.sourceforge.net/project/pywin32/pywin32/Build216/pywin32-216.win32-py%s.exe?r=&ts=%s&use_mirror=voxel"%(
    VER_SMALL,
    int(time.time())
)

def find_easy_install():
    search_base = os.path.dirname(os.path.realpath(sys.executable))
    locs = [
        os.path.join(search_base, '..', 'Scripts'), #python from build dir
        os.path.join(search_base, 'Scripts'),       #installed python
    ]
    for dir in locs:
        checkdir = os.path.abspath(os.path.join(dir, 'easy_install.exe'))
        if os.path.exists(checkdir):
            return checkdir

def make_rescheck(succeded_check):
    import ctypes
    def rescheck(value):
        if not succeded_check(value):
            raise ctypes.WinError()
        return value
    return rescheck
    
def shell_execute_uac(cmd, args):
    import ctypes
    se = ctypes.windll.shell32.ShellExecuteA
    se.restype = make_rescheck(lambda x: x > 32)
    return se(
        None,
        "runas",
        cmd,
        ' '.join('"%s"'%(x) for x in args),
        os.getcwd(), 
        1
    )
            
class ElevationError(WindowsError):
    pass
def execute_subprocess(*args, **kwargs):
    ERROR_ELEVATION_REQUIRED = 740
    try:
        return subprocess.call(*args, **kwargs)
    except WindowsError as e:
        if e.winerror != ERROR_ELEVATION_REQUIRED:
            raise
        ee = ElevationError()
        ee.errno = e.errno
        ee.winerror = e.winerror
        ee.strerror = e.strerror
        raise ElevationError, ee, sys.exc_info()[2]
            
def main(argv):
    easy_install = find_easy_install()
    if not easy_install:
        print "Could not find easy_install.exe!"
        return
    try:
        execute_subprocess((easy_install, "--help"))
    except ElevationError:
        print "Not enough privileges, relaunching self"
        shell_execute_uac(sys.executable, [os.path.abspath(argv[0])] + argv[1:])
        return
    
    install_pywin32(easy_install)

def install_pywin32(easy_install):
    tf = tempfile.NamedTemporaryFile('wb', suffix='.exe', prefix='pywin32-py%s'%(VER_SMALL), delete=False)
    try:
        print "Downloading pywin32 installer to %s"%(tf.name)
        u = urllib2.urlopen(URL)
        shutil.copyfileobj(u, tf)
        tf.close()
        print "Downloaded %s bytes"%(os.stat(tf.name).st_size)
        if open(tf.name, "rb").read(2) != 'MZ':
            print "Error - didn't download a valid exe file"
            return
        print "File has valid MZ header"
        print "Executing easy_install on pywin32 installer"
        execute_subprocess((easy_install, tf.name))

    finally:
        if os.path.exists(tf.name):
            try:
                tf.close()
            except Exception:
                pass
            os.unlink(tf.name)

if __name__ == '__main__':
    main(sys.argv)
