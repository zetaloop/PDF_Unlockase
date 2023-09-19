cd %~dp0

REM Remove the existing environment and build directories if they exist
if exist venv rmdir /s /q venv
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist mainui.spec del mainui.spec

REM Create a new virtual environment
python -m venv venv

REM Activate the virtual environment
call .\venv\Scripts\activate.bat

REM Install dependencies
python.exe -m pip install -U pip setuptools
pip install -U pyinstaller
pip install -U python-magic-bin pikepdf python-tkdnd

REM Run PyInstaller to build the project
pyinstaller --onefile --windowed --icon=../icon.ico --add-data "../icon.ico;." --add-data "../icon.png;." --collect-data tkinterDnD --distpath . --workpath build  ../mainui.py

REM Remove the virtual environment, build, and PyInstaller bootloader directories
if exist venv rmdir /s /q venv
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__
if exist mainui.spec del mainui.spec

echo.
echo Build completed.
pause