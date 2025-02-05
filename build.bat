@echo off
REM Build the executable using PyInstaller with the custom icon and include the assets folder in the bundle
pyinstaller --onefile --windowed --icon=assets/folder.ico --add-data "assets;assets" main.py

REM Pause so that you can see any messages before the window closes
pause 