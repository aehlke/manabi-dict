
from setuptools import setup
import os
import py2app
from src import manabidict

#from distribute_setup import use_setuptools
#use_setuptools()


os.system('/bin/rm -rf dist')
os.system('/bin/rm -rf build')
#os.system pyc


PLIST = {
    'PyRuntimeLocations': ['/System/Library/Frameworks/Python.framework/Versions/2.6/Python'],
}


setup(
    name='manabidict',
    #version=
    description='A viewer for EPWING-formatted Japanese dictionaries.',
    author='Alex Ehlke',
    url='http://manabi.org',
    license='GPLv3',
    app=['src/manabidict/manabidict.py'],
    zip_safe=False,

    options={
        'py2app': {
            'semi_standalone': False,
            #'argv_emulation': True,
            'includes': ['sip', 'PyQt4', 'gzip', 'PyQt4.QtCore', 'PyQt4.QtGui','PyQt4.QtWebKit',],
            'excludes': ['PyQt4.QtDesigner', 'PyQt4.QtOpenGL', 'PyQt4.QtScript', 'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtXml', 'PyQt4.phonon', 'wx', 'tcl', 'Tkinter'],
            'packages': ['lxml'],
            'plist': PLIST,
        },
    },

    setup_requires=['py2app'],
)

#os.system(
