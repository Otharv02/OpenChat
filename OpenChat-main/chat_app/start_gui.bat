@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Starting OpenChat server...
start /B python app.py

echo Waiting for server to start...
timeout /t 5

echo Starting GUI client...
python gui_app.py

pause
