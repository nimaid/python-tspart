@echo off

REM Run this file to initialize the project

set ORIGDIR="%CD%"
set FILEDIR="%~dp0"

set INSTALLCONDA="install_conda_windows.bat"
set SELFNAME="init.bat"

cd %FILEDIR%

echo Cheking if Conda needs to be installed...
call cmd /c %INSTALLCONDA%
if errorlevel 1 goto ERROR

echo.
echo Setup environment for "init.py"...
call conda activate base
if errorlevel 1 goto ERROR
call pip install keyboard
if errorlevel 1 goto ERROR
echo.
echo Run "init.py"...
call python init.py
if errorlevel 1 goto ERROR

echo Install the starting conda environment...
call conda env create -f environment.yml

echo Delete remaining init files...
del /f /q %INSTALLCONDA% 1>nul 2>&1
del /f /q %SELFNAME% 1>nul 2>&1

cd %ORIGDIR%

:ERROR
echo Project initialization failed!
exit /B 1

:DONE
echo Project initialization done!
exit /B 0