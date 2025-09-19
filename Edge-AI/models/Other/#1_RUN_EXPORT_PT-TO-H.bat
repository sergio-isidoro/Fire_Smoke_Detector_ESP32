@echo off
REM Converte model.pt para model.h
REM Certifique-se de que Python está no PATH

set INPUT=model.pt
set OUTPUT=model.h

python export_pt-to-h.py %INPUT% %OUTPUT%

pause
