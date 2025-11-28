@echo off
echo ============================================================
echo   Baeckerei Bestellsystem - Setup Script
echo ============================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nicht gefunden! Bitte installieren Sie Python 3.11+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/7] Python gefunden
python --version

REM Create virtual environment
echo.
echo [2/7] Erstelle Virtual Environment...
if not exist venv (
    python -m venv venv
    echo Virtual Environment erstellt
) else (
    echo Virtual Environment existiert bereits
)

REM Activate virtual environment
echo.
echo [3/7] Aktiviere Virtual Environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo [4/7] Update pip...
python -m pip install --upgrade pip --quiet

REM Install requirements
echo.
echo [5/7] Installiere Dependencies (das kann einige Minuten dauern)...
pip install -r requirements.txt --quiet

REM Create .env file
echo.
echo [6/7] Erstelle .env Datei...
if not exist .env (
    copy .env.example .env
    echo .env Datei erstellt - Bitte vor dem ersten Start anpassen!
) else (
    echo .env existiert bereits
)

REM Setup database
echo.
echo [7/7] Initialisiere Datenbank...
python manage.py migrate

echo.
echo ============================================================
echo   Setup erfolgreich abgeschlossen!
echo ============================================================
echo.
echo Naechste Schritte:
echo   1. Beispieldaten laden:  python manage.py load_sample_data
echo   2. Superuser erstellen:  python manage.py createsuperuser
echo   3. Server starten:       python manage.py runserver
echo.
echo Oder Docker verwenden:
echo   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
echo.
echo Dokumentation: README.md
echo Schnellstart:  QUICKSTART.md
echo.
pause
