@echo off
python -m PyQt5.uic.pyuic mainwindow.ui -o mainwindow.py
python -m PyQt5.uic.pyuic setting.ui -o setting.py
pause