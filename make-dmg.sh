#!/bin/sh

# Makes the DMG with all the nice things already setup.
# Most of the Finder window twiddling is done by an applescript, this just does
# the DMG manipulations.

# This script should be run with the working directory as the top level (where
# the dist folder appears)

if [ ! -d "dist" ]
then
    echo "This must be run in the same directory as 'dist'."
    exit 1
fi

if [ -d "/Volumes/ManabiDictionary" ]
then
    echo "You already have one ManabiDictionary mounted, unmount it first!"
    exit 1
fi

echo --- Configuring 'dist' folder...

if [ ! -e "dist/Applications" ]
then
    ln -s /Applications dist/Applications
fi

#if [ ! -d "dist/.background" ]
#then
#    mkdir dist/.background
#    cp ankiqt/mac/anki-logo-bg.png dist/.background
#fi

#if [ ! -f "dist/.DS_Store" ]
#then
#    cp ankiqt/mac/dmg_ds_store dist/.DS_Store
#fi

echo --- Creating writable DMG...
hdiutil create -attach -ov -format UDRW -volname ManabiDictionary -srcfolder dist -o ManabiDictionary-rw.dmg

RESULT=$?

if [ $RESULT != 0 ]
then
    echo "Creating RW DMG failed! ($RESULT)"
    exit 1
fi

#echo --- Running applescript to configure view settings...
#osascript "ankiqt/mac/set-dmg-settings.scpt"

echo --- Unmounting and converting to RO DMG...
hdiutil detach "/Volumes/ManabiDictionary"
if [ -d "/Volumes/ManabiDictionary" ]
then
    echo  "+++ Waiting for drive to detach..."
    sleep 5
    hdiutil detach "/Volumes/ManabiDictionary"
fi

if [ -d "/Volumes/ManabiDictionary" ]
then
    echo  "!!! Warning: Drive didn't detach cleanly forcing it to detach.."
    sleep 5
    hdiutil detach -force "/Volumes/ManabiDictionary"
fi

echo --- Making final compressed DMG...

hdiutil convert "ManabiDictionary-rw.dmg" -ov -format UDZO -imagekey zlib-level=9 -o ManabiDictionary.dmg

RESULT=$?

rm ManabiDictionary-rw.dmg

exit $RESULT
