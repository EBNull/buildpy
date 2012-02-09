"""Copy this python build to the default install location with default structure"""
import os
import sys
import collections
import pprint
import re
import glob
import shutil
import optparse

__dir__ = os.path.dirname(os.path.realpath(__file__))

SRCDIR = os.path.dirname(os.path.realpath(sys.executable))
assert 'PCBuild' in SRCDIR, "system_install.py should only be run on non-system python builds"

SRCDIR = os.path.dirname(SRCDIR) #level above PCBuild dir
os.chdir(SRCDIR)

VER_COMPRESSED=''.join(str(i) for i in sys.version_info[0:2])

INSTALL_PATH=os.path.realpath(os.path.join("C:\Python%s"%(VER_COMPRESSED)))

Patchlevel = collections.namedtuple('patchlevel', "major, minor, micro, level, serial")
def get_patchlevel(srcdir):
    # Extract current version from Include/patchlevel.h
    lines = open(srcdir + "/Include/patchlevel.h").readlines()
    major = minor = micro = level = serial = None
    levels = {
        'PY_RELEASE_LEVEL_ALPHA':0xA,
        'PY_RELEASE_LEVEL_BETA': 0xB,
        'PY_RELEASE_LEVEL_GAMMA':0xC,
        'PY_RELEASE_LEVEL_FINAL':0xF
    }
    for l in lines:
        if not l.startswith("#define"):
            continue
        l = l.split()
        if len(l) != 3:
            continue
        _, name, value = l
        if name == 'PY_MAJOR_VERSION': major = value
        if name == 'PY_MINOR_VERSION': minor = value
        if name == 'PY_MICRO_VERSION': micro = value
        if name == 'PY_RELEASE_LEVEL': level = levels[value]
        if name == 'PY_RELEASE_SERIAL': serial = value
    return Patchlevel(major, minor, micro, level, serial)

def get_docfilename(patchlevel):
    # Compute the name that Sphinx gives to the docfile
    (major, minor, micro, level, serial) = patchlevel
    docfile = ""
    if int(micro):
        docfile = micro
    if level < 0xf:
        if level == 0xC:
            docfile += "rc%s" % (serial,)
        else:
            docfile += '%x%s' % (level, serial)
    docfile = 'python%s%s%s.chm' % (major, minor, docfile)
    return docfile
    
    
class Directory:
    def __init__(self, basedir, physical, name=None):
        self.basedir = basedir
        self.physical = physical
        
        self.files = set()
        self.dirs = set()
        
        if basedir:
            self.absolute = os.path.join(basedir.absolute, physical)
        else:
            self.absolute = physical
        if not name:
            name = physical
        self.name = name
        # initially assume that all files in this directory are unpackaged
        # as files from self.absolute get added, this set is reduced
        self.unpackaged_files = set()
        if os.path.exists(self.absolute):
            for f in os.listdir(self.absolute):
                if os.path.isfile(os.path.join(self.absolute, f)):
                    self.unpackaged_files.add(f)

    def absolute_dest(self):
        if self.basedir is None:
            return ''
        return os.path.join(self.basedir.absolute_dest(), self.name)
        
    def pformat(self):
        return pprint.pformat(self._to_dict())
        
    @property
    def all_files(self):
        for f in self.files:
            yield (f.source, os.path.join(self.absolute_dest(), f.dest))
        for d in self.dirs:
            for x in d.all_files:
                yield x
        
    def remove_pyc(self):
        for f in list(self.files):
            if f.source.endswith('.pyc'):
                self.files.remove(f)
        for f in set(self.unpackaged_files):
            if f.endswith('.pyc'):
                self.mark_packaged(f)
                
    def check_unpackaged(self):
        self.unpackaged_files.discard('__pycache__')
        self.unpackaged_files.discard('.svn')
        if self.unpackaged_files:
            print "Warning: Unpackaged files in %s" % self.absolute
            print self.unpackaged_files
        
    def _to_dict(self):
        dirs = {}
        dirs[''] = sorted(self.files, key=lambda x: repr(x))
        for dir in self.dirs:
            dirs[dir.name] = dir._to_dict()
        return dirs
            
    def add_dir(self, dirname, physical_base=None):
        d = Directory(self, physical_base or dirname, dirname)
        self.dirs.add(d)
        return d
    
    def mark_packaged(self, relative):
        if relative.startswith(self.absolute):
            # mark file as packaged
            relative = relative[len(self.absolute)+1:]
        if relative in self.unpackaged_files:
            self.unpackaged_files.remove(relative)
                
    def add_file(self, file, src=None):
        if file is None:
            #Allow passing only src
            file = os.path.basename(src)
        if not src:
            #allow ommitting src, effectively passing src as file
            src = file
            file = os.path.basename(src) #allow file to actually have been src
        absolute = os.path.join(self.absolute, src)
        self.mark_packaged(absolute)
        assert not re.search(r'[\?|><:/*]"', file) # restrictions on long names

        fs = FileSpec(absolute, file)
        self.files.add(fs)

    def add_glob(self, pattern, exclude=None):
        files = glob.glob1(self.absolute, pattern)
        for f in files:
            if exclude and f in exclude: continue
            self.add_file(f)
        return files
    glob = add_glob
    
class FileSpec(object):
    def __init__(self, source, dest=None):
        if dest == None:
            dest = os.path.basename(source)
        self.source = source
        self.dest = dest
    def __repr__(self):
        missing = ""
        if not os.path.exists(self.source):
            missing=" (missing!)"
        if self.dest != os.path.basename(self.source):
            return '"%s" (from "%s")%s'%(self.dest, os.path.basename(self.source), missing)
        return '"%s"%s'%(self.dest, missing)

def generate_license(SRCDIR, fatal=False):
    import shutil, glob
    out = open(os.path.join(SRCDIR, "LICENSE.txt"), "w")
    shutil.copyfileobj(open(os.path.join(SRCDIR, "LICENSE")), out)
    for name, pat, file in (
            ("bzip2","bzip2-*", "LICENSE"),
            ("openssl", "openssl-*", "LICENSE"),
            ("Tcl", "tcl8*", "license.terms"),
            ("Tk", "tk8*", "license.terms"),
            ("Tix", "tix-*", "license.terms")
            ):
        out.write("\nThis copy of Python includes a copy of %s, which is licensed under the following terms:\n\n" % name)
        gdir = os.path.normpath(os.path.join(SRCDIR,"..",pat))
        dirs = glob.glob(gdir)
        if not dirs:
            if not fatal:
                continue
            raise ValueError, "Could not find "+gdir
        if len(dirs) > 2:
            raise ValueError, "Multiple copies of "+pat
        dir = dirs[0]
        shutil.copyfileobj(open(os.path.join(dir, file)), out)
    out.close()

def extract_msvcr90(arch='x86'):
    # Find the redistributable files
    dir = os.path.join(os.environ['VS90COMNTOOLS'], r"..\..\VC\redist\%s\Microsoft.VC90.CRT" % arch)
    
    result = []
    # omit msvcm90 and msvcp90, as they aren't really needed
    files = ["Microsoft.VC90.CRT.manifest", "msvcr90.dll"]
    for f in files:
        path = os.path.join(dir, f)
        result.append((f, path))
    return result
    
    
def add_root_files(root, srcdir):
    pl = get_patchlevel(srcdir)
    
    lib_file = os.path.join(srcdir, 'PCBuild', "python%s%s.lib" % (pl.major, pl.minor))
    def_file = os.path.join(srcdir, 'PCBuild', "python%s%s.def" % (pl.major, pl.minor))
    dll_file = os.path.join(srcdir, 'PCBuild', "python%s%s.dll" % (pl.major, pl.minor))
    dll_d_file = os.path.join(srcdir, 'PCBuild', "python%s%s_d.dll" % (pl.major, pl.minor))
    

    
    #---------------
    #Root Directory
    root.add_file(None,         os.path.join('PCBuild', "w9xpopen.exe"))
    root.add_file("README.txt", os.path.join("README"))
    root.add_file("NEWS.txt",   os.path.join("Misc", "NEWS"))
    
    #generate_license(srcdir)
    #files[''].append(FileSpec(os.path.join(srcdir, "LICENSE.txt")))
    
    #python component
    root.add_file(None,         os.path.join("PCBuild", "python.exe"))
    #pythonw component
    root.add_file(None,         os.path.join("PCBuild", "pythonw.exe"))
    
    #extra: debug!
    root.add_file(None,         os.path.join("PCBuild", "python_d.exe"))
    root.add_file(None,         os.path.join("PCBuild", "pythonw_d.exe"))
    
    #DLLDIR can be either the root install, or the System32 directory.
    #here, we set it to the root install dir.
    root.add_file(None,         dll_file)
    root.add_file(None,         dll_d_file)

    manifest, crtdll = extract_msvcr90()
    root.add_file(None,         manifest[1])
    root.add_file(None,         crtdll[1])

    
def add_lib_files(root, have_ctypes, have_tcl):
    #Lib directory
    # Add all .py files in Lib, except tkinter, test
    have_tcl = True
    
    dirs = []
    pydirs = [(root, 'Lib')]
    while pydirs:
        parent, dir = pydirs.pop()
        if dir == ".svn" or dir == '__pycache__' or dir.startswith("plat-"):
            continue
        elif dir in ["tkinter", "idlelib", "Icons"]:
            if not have_tcl:
                continue
        elif dir in ['test', 'tests', 'data', 'output']:
            pass
            # test: Lib, Lib/email, Lib/ctypes, Lib/sqlite3
            # tests: Lib/distutils
            # data: Lib/email/test
            # output: Lib/test
        elif not have_ctypes and dir == "ctypes":
            continue

        lib = parent.add_dir(dir)
        # Add additional files
        dirs.append(lib)
        lib.glob("*.txt")
        if dir=='site-packages':
            lib.add_file("README.txt", src="README")
            continue
        lib.glob("*.py")
        lib.glob("*.pyw")
        lib.glob("README")
        
        if dir=='Lib':
            lib.add_file("sysconfig.cfg")
        if dir=='test' and parent.physical=='Lib':
            lib.add_file("185test.db")
            lib.add_file("audiotest.au")
            lib.add_file("sgml_input.html")
            lib.add_file("testtar.tar")
            lib.add_file("test_difflib_expect.html")
            lib.add_file("check_soundcard.vbs")
            lib.add_file("empty.vbs")
            lib.add_file("Sine-1000Hz-300ms.aif")
            lib.glob("*.uue")
            lib.glob("*.pem")
            lib.glob("*.pck")
            lib.glob("cfgparser.*")
            lib.add_file("zip_cp437_header.zip")
            lib.add_file("zipdir.zip")
        if dir=='capath':
            lib.glob("*.0")
        if dir=='tests' and parent.physical=='distutils':
            lib.add_file("Setup.sample")
        if dir=='decimaltestdata':
            lib.glob("*.decTest")
        if dir=='xmltestdata':
            lib.glob("*.xml")
            lib.add_file("test.xml.out")
        if dir=='output':
            lib.glob("test_*")
        if dir=='sndhdrdata':
            lib.glob("sndhdr.*")
        if dir=='idlelib':
            lib.glob("*.def")
            lib.add_file("idle.bat")
            lib.add_file("ChangeLog")
        if dir=="Icons":
            lib.glob("*.gif")
            lib.add_file("idle.icns")
        if dir=="command" and parent.physical in ("distutils", "packaging"):
            lib.glob("wininst*.exe")
            lib.add_file("command_template")
#        if dir=="lib2to3":
#            lib.removefile("pickle", "*.pickle")
        if dir=="macholib":
            lib.add_file("README.ctypes")
            lib.glob("fetch_macholib*")
        if dir=='turtledemo':
            lib.add_file("turtle.cfg")
        if dir=="pydoc_data":
            lib.add_file("_pydoc.css")
        if dir=="data" and parent.physical=="test_email":
            # This should contain all non-.svn files listed in subversion
            for f in os.listdir(lib.absolute):
                if f.endswith(".txt") or f==".svn":continue
                if f.endswith(".au") or f.endswith(".gif"):
                    lib.add_file(f)
            else:
                print("WARNING: New file %s in test/test_email/data" % f)
        for f in os.listdir(lib.absolute):
            if os.path.isdir(os.path.join(lib.absolute, f)):
                pydirs.append((lib, f))
    for d in dirs:
        d.remove_pyc()
        d.check_unpackaged()
    
def add_ext_files(root, srcdir, have_ctypes, have_tcl):
    extensions = [
        'bz2.pyd',
        'pyexpat.pyd',
        'select.pyd',
        'unicodedata.pyd',
        'winsound.pyd',
        '_elementtree.pyd',
        '_socket.pyd',
        '_ssl.pyd',
        '_testcapi.pyd',
        '_tkinter.pyd',
        '_msi.pyd',
        '_ctypes.pyd',
        '_ctypes_test.pyd',
        '_sqlite3.pyd',
        '_hashlib.pyd',
        '_multiprocessing.pyd'
    ]
    if not have_ctypes:
        extensions.remove("_ctypes.pyd")
    
    lib = root.add_dir('DLLs', os.path.join(srcdir, 'PCBuild'))
    lib.add_file(None, os.path.join(SRCDIR, "PC", "py.ico"))
    lib.add_file(None, os.path.join(SRCDIR, "PC", "pyc.ico"))

    dlls = []
    tclfiles = []
    for f in extensions:
        if f=="_tkinter.pyd":
            continue
        fd = f.replace(".pyd", "_d.pyd")
        if not os.path.exists(SRCDIR + "/" + 'PCBUILD' + "/" + f):
            print "WARNING: Missing extension", f
        else:
            dlls.append(f)
            lib.add_file(f)
        if not os.path.exists(SRCDIR + "/" + 'PCBUILD' + "/" + fd):
            print "WARNING: Missing debug extension", fd
        else:
            dlls.append(fd)
            lib.add_file(fd)
        
    #lib.add_file('python3.dll')
    # Add sqlite
    
    sqlite_arch = ""
    tclsuffix = ""
    lib.add_file("sqlite3.dll")
    if have_tcl:
        if not os.path.exists("%s/%s/_tkinter.pyd" % (SRCDIR, 'PCBUILD')):
            print("WARNING: Missing _tkinter.pyd")
        else:
            lib.start_component("TkDLLs", tcltk)
            lib.add_file("_tkinter.pyd")
            dlls.append("_tkinter.pyd")
            tcldir = os.path.normpath(srcdir+("/../tcltk%s/bin" % tclsuffix))
            for f in glob.glob1(tcldir, "*.dll"):
                lib.add_file(f, src=os.path.join(tcldir, f))
    # check whether there are any unknown extensions
    for f in glob.glob1(SRCDIR+"/"+'PCBUILD', "*.pyd"):
        #if f.endswith("_d.pyd"): continue # debug version
        if f in dlls: continue
        if f.replace("_d.pyd", ".pyd") in dlls: continue
        print "WARNING: Unknown extension", f
    return dlls, tclsuffix, sqlite_arch
    
def add_include_files(root, srcdir, dlls, tclsuffix, sqlite_arch, have_mingw, have_tcl):
    (major, minor, micro, level, serial) = get_patchlevel(srcdir)
    # Add headers
    lib = root.add_dir('include')
    lib.glob("*.h")
    lib.add_file("pyconfig.h", src="../PC/pyconfig.h")
    # Add import libraries
    lib = root.add_dir("libs", os.path.join(srcdir, 'PCBuild'))
    for f in dlls:
        lib.add_file(f.replace('pyd','lib'))
    lib.add_file('python%s%s.lib' % (major, minor))
    lib.add_file('python3.lib')
    # Add the mingw-format library
    if have_mingw:
        lib.add_file('libpython%s%s.a' % (major, minor))
    if have_tcl:
        # Add Tcl/Tk
        tcldirs = [(root, '../tcltk%s/lib' % tclsuffix, 'tcl')]
        while tcldirs:
            parent, phys, dir = tcldirs.pop()
            lib = parent.add_dir(dir, phys)
            if not os.path.exists(lib.absolute):
                continue
            for f in os.listdir(lib.absolute):
                if os.path.isdir(os.path.join(lib.absolute, f)):
                    tcldirs.append((lib, f, f))
                else:
                    lib.add_file(f)

def add_tool_files(root, srcdir, have_tcl):
    tooldir = root.add_dir('Tools')
    for f in ['i18n', 'pynche', 'Scripts']:
        lib = tooldir.add_dir(f)
        lib.glob("*.py")
        lib.glob("*.pyw", exclude=['pydocgui.pyw'])
        lib.remove_pyc()
        lib.glob("*.txt")
        if f == "pynche":
            x = lib.add_dir("X")
            x.glob("*.txt")
        if os.path.exists(os.path.join(lib.absolute, "README")):
            lib.add_file("README.txt", src="README")
        if f == 'Scripts':
            lib.add_file("2to3.py", src="2to3")
            lib.add_file("pydoc3.py", src="pydoc3")
            lib.add_file("pysetup3.py", src="pysetup3")
            if have_tcl:
                lib.add_file("pydocgui.pyw")
        # Add documentation
        lib = root.add_dir("Doc")
        docfile = get_docfilename(get_patchlevel(srcdir))
        lib.add_file(docfile, src="build/htmlhelp/"+docfile)
    
def gather_files(srcdir):
    have_mingw = False
    have_tcl = True
    
    # Check if _ctypes.pyd exists
    have_ctypes = os.path.exists(os.path.join(srcdir, "PCBuild", "_ctypes.pyd"))
    if not have_ctypes:
        print("WARNING: _ctypes.pyd not found, ctypes will not be included")
    
    
    
    root = Directory(None, srcdir)
    
    add_root_files(root, srcdir)
    add_lib_files(root, have_ctypes, have_tcl)
    dlls, tclsuffix, sqlite_arch = add_ext_files(root, srcdir, have_ctypes, have_tcl)
    add_include_files(root, srcdir, dlls, tclsuffix, sqlite_arch, have_mingw, have_tcl)    
    add_tool_files(root, srcdir, have_tcl)
    
    return root
    
def install_files(options, root, dest_folder):
    dirs_made = set('')
    files_copied = 0
    for src, d in root.all_files:
        if os.path.exists(src):
            dest = os.path.join(dest_folder, d)
            fn = os.path.dirname(dest)
            if fn not in dirs_made:
                dirs_made.add(fn)
                if not os.path.exists(fn):
                    os.makedirs(fn)
            if options.show_files:
                print dest
            shutil.copy(src, dest)
            files_copied += 1
    cur_dirs = [root]
    while cur_dirs:
        cur = cur_dirs.pop()
        dd = cur.absolute_dest()
        dd = os.path.join(dest_folder, dd)
        if not os.path.exists(dd):
            os.makedirs(dd)
        cur_dirs += cur.dirs
    return files_copied
        
def get_args(argv, defaults):
    from optparse import OptionParser
    parser = OptionParser(usage="%s [dest_folder] [args]"%(argv[0]))
    parser.add_option("", "--install-pywin32",
                      action="store_true", default=False,
                      help="Install pywin32")
    parser.add_option("", "--show-files",
                      action="store_true", default=False,
                      help="Show what files will be installed")
    parser.add_option("-v", "--verbose",
                      action="store_true", default=False,
                      help="Be verbose (implies --show-files)")
    return parser.parse_args(args=argv[1:], values=defaults)
        

def download_distribute(url):
    import tempfile
    import urllib2
    tf = tempfile.NamedTemporaryFile('wb', suffix='.py', prefix='distribute', delete=False)
    try:
        print "Downloading python-distribute installer to %s"%(tf.name)
        u = urllib2.urlopen(url)
        shutil.copyfileobj(u, tf)
        tf.close()
        print "Downloaded %s bytes"%(os.stat(tf.name).st_size)
    except Exception:
        try:
            tf.close()
        except Exception:
            pass
        os.unlink(tf.name)
        raise
    return tf.name


    
    
def postinstall_setup(dest_folder, options):
    import subprocess
    python = os.path.join(dest_folder, 'python.exe')
    if options.install_pip:
        dd = download_distribute("http://python-distribute.org/distribute_setup.py")
        d = subprocess.Popen([python, dd])
        d.wait()
    if options.install_pip and options.install_pywin32:
        instf = os.path.join(__dir__, 'install_pywin32.py')
        print instf
        d = subprocess.Popen([python, instf])
        d.wait()        
        
def main(argv):
    defaults = optparse.Values(dict(
        verbose=False,
        show_files=False,
        install_pip=True,
        install_pywin32=True
    ))
    options, args = get_args(argv, defaults)
    dest_folder = ''
    if len(args) < 1:
        if not options.show_files:
            sys.stderr.write("Need destination argument")
            return 2
    else:
        dest_folder = args[0]
    if options.verbose:
        options.show_files=True

    root = gather_files(SRCDIR)
    
    filecount = 0
    for src, d in root.all_files:
        filecount += 1
        if not os.path.exists(src):
            print "MISSING FILE: %s"%(src)
    
    print "Ready to package %s files"%(filecount)
    
    if dest_folder:
        print "Installing files to %s"%(dest_folder)
        ret = install_files(options, root, dest_folder)
        print "%s files installed"%(ret)
        postinstall_setup(dest_folder, options)
    else:
        print "These files would be installed:"
        for src, d in root.all_files:
            if os.path.exists(src):
                print "%s"%(d)
        
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))