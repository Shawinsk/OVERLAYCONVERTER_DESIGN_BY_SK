@echo off
echo Fixing blocked files...
powershell -Command "Get-ChildItem -Path '%~dp0' -Recurse | Unblock-File"
echo.
echo ========================================================
echo  SUCCESS! All files in this folder are now UNBLOCKED.
echo  You can now open them without any warnings.
echo ========================================================
echo.
pause
