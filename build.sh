#!/bin/sh
./buildresources.sh
./buildui.sh
python setup.py py2app
cp qt.conf dist/manabidict.app/Contents/Resources
