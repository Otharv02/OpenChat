@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Starting OpenChat server...
python app.py

pause
