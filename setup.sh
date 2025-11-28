#!/bin/bash

echo "============================================================"
echo "  Baeckerei Bestellsystem - Setup Script"
echo "============================================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 nicht gefunden! Bitte installieren Sie Python 3.11+"
    exit 1
fi

echo "[1/7] Python gefunden"
python3 --version

# Create virtual environment
echo ""
echo "[2/7] Erstelle Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual Environment erstellt"
else
    echo "Virtual Environment existiert bereits"
fi

# Activate virtual environment
echo ""
echo "[3/7] Aktiviere Virtual Environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "[4/7] Update pip..."
python -m pip install --upgrade pip --quiet

# Install requirements
echo ""
echo "[5/7] Installiere Dependencies (das kann einige Minuten dauern)..."
pip install -r requirements.txt --quiet

# Create .env file
echo ""
echo "[6/7] Erstelle .env Datei..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env Datei erstellt - Bitte vor dem ersten Start anpassen!"
else
    echo ".env existiert bereits"
fi

# Setup database
echo ""
echo "[7/7] Initialisiere Datenbank..."
python manage.py migrate

echo ""
echo "============================================================"
echo "  Setup erfolgreich abgeschlossen!"
echo "============================================================"
echo ""
echo "Naechste Schritte:"
echo "  1. Beispieldaten laden:  python manage.py load_sample_data"
echo "  2. Superuser erstellen:  python manage.py createsuperuser"
echo "  3. Server starten:       python manage.py runserver"
echo ""
echo "Oder Docker verwenden:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.dev.yml up"
echo ""
echo "Dokumentation: README.md"
echo "Schnellstart:  QUICKSTART.md"
echo ""
