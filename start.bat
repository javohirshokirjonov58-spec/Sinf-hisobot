@echo off
chcp 65001 >nul
title Sinf Kassasi
echo ====================================================
echo        🎓 SINF KASSASI DASTURI ISHGA TUSHMOQDA...
echo ====================================================
echo Brauzerda ochilmoqda: http://localhost:8501
echo Dasturni to'xtatish uchun: Ctrl + C
echo.
"C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe" -m streamlit run app.py
pause
