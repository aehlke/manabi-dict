#!/bin/sh
./buildresources.sh
./buildui.sh
python setup.py py2app -O2
#python setup.py py2app -O2 --no-strip
cp qt.conf dist/Manabi\ Dictionary.app/Contents/Resources
chmod 755 dist/Manabi\ Dictionary.app/Contents/Resources/mecab/bin/mecab
