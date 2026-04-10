@echo off
title Smart Guardian Security System
echo Starting Smart Guardian in Production Mode...
echo Checking dependencies...
pip install -r requirements.txt
python start_production.py
pause
