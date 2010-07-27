
from setuptools import setup, Command
import os
import py2app
from src import manabidict
#from src.manabidict.manabidict import VERSION
import sys

#from distribute_setup import use_setuptools
#use_setuptools()

#os.system('/bin/rm -rf dist')
#os.system('/bin/rm -rf build')

def find_file_in_path(filename):
    for include_path in sys.path:
        file_path = os.path.join(include_path, filename)
        if os.path.exists(file_path):
            return file_path


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

        #for f in ['MacOS/python',
                  #'Frameworks/Python.framework/Versions/2.6/Python',
                  #'Frameworks/QtWebKit.framework/Versions/4/QtWebKit',
                  #'Frameworks/QtGui.framework/Versions/4/QtGui',
                  #'Resources/lib/python2.6/lib-dynload/PyQt4/QtGui.so',
                  #'Frameworks/QtXmlPatterns.framework/Versions/Current/QtXmlPatterns',
                  #'Resources/lib/python2.6/lib-dynload/PyQt4/QtCore.so',
                  #'Frameworks/QtCore.framework/Versions/4/QtCore',
                  #'Frameworks/libmecab.1.dylib',
                  #'Resources/lib/python2.6/lxml/etree.so',
                  #'Frameworks/QtNetwork.framework/Versions/4/QtNetwork',
                  #'Resources/mecab/bin/libmecab.1.dylib',
                  #'Resources/lib/python2.6/lib-dynload/PyQt4/QtNetwork.so',
                  #'Frameworks/QtOpenGL.framework/Versions/4/QtOpenGL',
                 ]:
            #os.system(u'lipo -thin i386 {0}{1} -o {0}{1}'.format('dist/Manabi\ Dictionary.app/Contents/', f))


        #make the dmg with the shell script
        result = os.system('make-dmg.sh')
        if result is not 0:
           raise Exception('dmg creation failed %d' % result)


#os.system pyc


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
        'py2app': {
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
        },
    },

    setup_requires=['py2app'],
    #cmdclass = {'bdist_dmg': bdist_dmg, 'bdist': bdist},
    #cmdclass = { 'bdist': bdist},
    cmdclass = { 'bdist_dmg': bdist_dmg},
)

#os.system(
