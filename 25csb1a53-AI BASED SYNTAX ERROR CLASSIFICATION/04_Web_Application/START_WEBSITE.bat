@echo off
title AI Based Syntax Error Classification - Web Studio
echo Starting AI Based Syntax Error Classification Server...
start "" http://localhost:8000
python server.py
pause