@echo off
chcp 65001
echo Redmine Wiki Downloader Build Script
echo.

echo 1. Installing PyInstaller...
python -m pip install pyinstaller

echo.
echo 2. Building executable...
pyinstaller --onefile --windowed --name "RedmineWikiDownloader" --icon=favicon.ico main.py

echo.
echo 3. Build Complete!
echo Executable location: dist\RedmineWikiDownloader.exe
echo.

pause