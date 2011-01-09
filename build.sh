#!/bin/bash
rm -rf Nink.app
mkdir -p Nink.app/Contents/MacOS
cp *.py Nink.app/Contents/MacOS
cp README Nink.app/Contents/MacOS
cp TODO Nink.app/Contents/MacOS
cp -r map Nink.app/Contents/MacOS
cp -r images Nink.app/Contents/MacOS
cp -r shaders Nink.app/Contents/MacOS
cp -r sound Nink.app/Contents/MacOS
cp -r gletools Nink.app/Contents/MacOS
cp -r pyglet Nink.app/Contents/MacOS
ln -s app.py Nink.app/Contents/MacOS/Nink
