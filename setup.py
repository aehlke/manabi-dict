
from setuptools import setup, Command
import os
from src import manabidict
#from src.manabidict.manabidict import VERSION
import sys

IS_WINDOWS = sys.platform in ('win32', )

if IS_WINDOWS:
    import py2exe
    SETUP_REQUIRES = ['py2exe']
else:
    import py2app
    SETUP_REQUIRES = ['py2app']

#install_requires=[
    #'lxml>=2.2.4',
    #'ebmodule>=2.2',
#]
#from distribute_setup import use_setuptools
#use_setuptools()




class bdist_dmg(Command):
    description = "create a Mac disk image (.dmg) binary distribution"
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        #self.run_command('bdist')
        os.system('/bin/rm -rf dist')
        os.system('/bin/rm -rf build')
        self.run_command('py2app')
        os.system("mkdir -p dist/Manabi\ Dictionary.app/Contents/Resources/include/python2.6")
        os.system("cp /Library/Frameworks/Python.framework/Versions/2.6/include/\
python2.6/pyconfig.h dist/Manabi\ Dictionary.app/Contents/Resources/include/python2.6/pyconfig.h")
        os.system('cp qt.conf dist/Manabi\ Dictionary.app/Contents/Resources')
        os.system('chmod 755 dist/Manabi\ Dictionary.app/Contents/Resources/mecab/bin/mecab')
        os.system('cp -r resources/Python.framework dist/Manabi\ Dictionary.app/Contents/Frameworks/')

        os.system('cp /usr/lib/libmecab.1.dylib dist/Manabi\ Dictionary.app/Contents/Frameworks/')

        # strip out x86_64 resources
        #os.system('ditto --rsrc --arch i386 dist/Manabi\ Dictionary.app dist/Manabi\ Dictionaryi386.app')
        #os.system('cp dist/Manabi\ Dictionary.app/Contents/MacOS/Manabi\ Dictionary dist/Manabi\ Dictionaryi386.app/Contents/MacOS/')
        #os.system('rm -rf dist/Manabi\ Dictionary.app')
        #os.system('mv dist/Manabi\ Dictionaryi386.app dist/Manabi\ Dictionary.app')
        # if we strip MacOS/Manabi\ Dictionary, for some reason it will always crash.
        #os.system(u'lipo -thin i386 {0}{1} -o {0}{1}'.format('dist/Manabi\ Dictionary.app/Contents/', f))

        #make the dmg with the shell script
        result = os.system('make-dmg.sh')
        if result is not 0:
           raise Exception('dmg creation failed %d' % result)

class bdist_exe(Command):
    description = "create a Mac disk image (.dmg) binary distribution"
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        os.system('rm -rf dist')
        os.system('rm -rf build')
        self.run_command('py2exe')
        #os.system('cp qt.conf dist/Manabi\ Dictionary.app/Contents/Resources')


#os.system pyc


# py2app stuff

PLIST = {
    'CFBundleIdentifier': 'org.manabi.dictionary',
    'CFBundleName': 'Manabi Dictionary',
	'CFBundleLocalizations': ['en'],

    'PyRuntimeLocations': ['@executable_path/../Frameworks/Python.framework/Versions/2.6/Python',]
                           ##'/System/Library/Frameworks/Python.framework/Versions/2.6/Python'],
}

DATA_FILES = [
    './resources/PlugIns',
    './resources/mecab',
]

PY2APP_OPTIONS = {
    'semi_standalone': False,
    'iconfile': 'resources/book.icns',
    #'argv_emulation': True,
    'includes': ['sip', 'PyQt4', 'gzip', 'PyQt4.QtCore', 'PyQt4.QtGui','PyQt4.QtWebKit', 'zlib'],
    'excludes': ['PyQt4.QtDesigner', 'PyQt4.QtOpenGL', 'PyQt4.QtScript',
                    'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtXml', 'phonon',
                    'QtOpenGL', 'QtXmlPatterns', 'wx', 'tcl', 'Tkinter',
                    'numpy', 'scipy', 'pygame', 'matplotlib', 'PIL'],
    'dylib_excludes': ['libncurses.5.dylib', '_wxagg.so', '_tkagg.so', '_gtkagg.so', 'wx.so'],
    'packages': ['lxml'],
    'optimize': 0,
    'plist': PLIST,
}


# py2exe

PY2EXE_OPTIONS = {
    'compressed': True,
    'includes': ['PyQt4._qt', 'sip', 'gzip'],
    'excludes': ['pywin', 'Tkinter', 'Tkconstants', 'tcl',],

}

WINDOWS = {
    'script': 'src/manabidict/manabidict.py',
    #'icon_resources': [(1, '')]
}



setup(
    name='Manabi Dictionary',
    version='0.000002',
    description='A viewer for EPWING-formatted Japanese dictionaries.',
    author='Alex Ehlke',
    url='http://manabi.org',
    license='GPLv3',
    app=['src/manabidict/manabidict.py'],
    zip_safe=False,
    #include_package_data=True,
    data_files=DATA_FILES,

    options={
        'py2app': PY2APP_OPTIONS,
        'py2exe': PY2EXE_OPTIONS,
    },

    windows=WINDOWS,

    setup_requires=SETUP_REQUIRES,
    #cmdclass = {'bdist_dmg': bdist_dmg, 'bdist': bdist},
    #cmdclass = { 'bdist': bdist},
    cmdclass = { 'bdist_dmg': bdist_dmg},
)

#os.system(
