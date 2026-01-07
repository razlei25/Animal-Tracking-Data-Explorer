@echo off
echo Cleaning UV cache...
uv cache clean
echo.
echo Running data explorer GUI...
uv run data_explorer_GUI.py
pause
