@echo off
gcc c\helper.c -O2 -o helper.exe
if errorlevel 1 exit /b 1
echo Built helper.exe
