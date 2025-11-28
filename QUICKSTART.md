# Quick Start Guide - Ubuntu 24.04 (Proxmox VM)

## 🖥️ Voraussetzungen auf Ubuntu VM

### System-Pakete installieren

```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python und Dependencies installieren
sudo apt install -y python3 python3-pip python3-venv git postgresql postgresql-contrib

# Optional: Docker für Container-Deployment
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER  # Logout/Login erforderlich
```

---

## 🚀 Option 1: Lokale Installation (ohne Docker)

### 1. Repository klonen

```bash
# Repository klonen
git clone https://github.com/MrHartung/BaeckereiBestellungen.git
cd BaeckereiBestellungen

# Oder falls lokal: Dateien hochladen via SCP/SFTP
```

### 2. Virtual Environment einrichten

```bash
# Virtual Environment erstellen
python3 -m venv venv

# Aktivieren
source venv/bin/activate

# pip aktualisieren
pip install --upgrade pip

# Dependencies installieren
pip install -r requirements.txt
```

### 3. Datenbank konfigurieren

**Option A: SQLite (einfach für Tests)**
```bash
# .env Datei erstellen
cp .env.example .env

# Folgende Zeile in .env leer lassen (dann wird SQLite verwendet):
# DATABASE_URL=
```

**Option B: PostgreSQL (empfohlen für Production)**
```bash
# PostgreSQL Datenbank erstellen
sudo -u postgres psql

# In psql:
CREATE DATABASE baecker_db;
CREATE USER baecker_user WITH PASSWORD 'sicheres_passwort';
GRANT ALL PRIVILEGES ON DATABASE baecker_db TO baecker_user;
\q

# .env Datei bearbeiten
nano .env

# Folgende Zeile eintragen:
DATABASE_URL=postgresql://baecker_user:sicheres_passwort@localhost:5432/baecker_db
```

### 4. Django initialisieren

```bash
# Datenbank-Migrationen ausführen
python manage.py migrate

# Beispieldaten laden (optional aber empfohlen für Tests)
python manage.py load_sample_data

# Oder eigenen Superuser erstellen
python manage.py createsuperuser
```

### 5. Server starten

```bash
# Entwicklungsserver (für Tests)
python manage.py runserver 0.0.0.0:8000
```

**Zugriff von außen:**
- Finde VM IP: `ip addr show` oder `hostname -I`
- Öffne im Browser: `http://VM-IP:8000`
- Firewall-Regel falls nötig: `sudo ufw allow 8000`

### 6. Testen

**Frontend:** http://VM-IP:8000  
**Admin:** http://VM-IP:8000/admin  
**API:** http://VM-IP:8000/api/v1/

**Login-Credentials (nach load_sample_data):**
- **User:** test@example.com / testpass1234  
- **Admin:** admin@example.com / admin1234567890

---

## 🐳 Option 2: Docker Installation (empfohlen)

### 1. Repository vorbereiten

```bash
cd BaeckereiBestellungen

# .env Datei erstellen
cp .env.example .env

# Minimal-Config für Development (in .env):
nano .env
```

**Wichtige .env Einstellungen:**
```env
SECRET_KEY=change-this-to-something-random
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,VM-IP-HIER-EINTRAGEN
DATABASE_URL=postgresql://baecker_user:baecker_pass@db:5432/baecker_db
```

### 2. Docker Container starten

**Development-Modus:**
```bash
# Container bauen und starten
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# Logs ansehen
docker-compose logs -f web
```

**Production-Modus:**
```bash
docker-compose up -d --build
```

### 3. Initialisierung

```bash
# Migrations ausführen (wird automatisch gemacht, aber zur Sicherheit)
docker-compose exec web python manage.py migrate

# Beispieldaten laden
docker-compose exec web python manage.py load_sample_data

# Oder Superuser erstellen
docker-compose exec web python manage.py createsuperuser
```

### 4. Zugriff

**Development:**
- Frontend: http://VM-IP:8080
- Admin: http://VM-IP:8080/admin

**Production:**
- Frontend: http://VM-IP
- Admin: http://VM-IP/admin

**Firewall öffnen:**
```bash
sudo ufw allow 8080  # Development
sudo ufw allow 80    # Production
sudo ufw allow 443   # HTTPS (später)
```

---

## 📝 Wichtige Commands

### Lokale Installation (ohne Docker)
```bash
# Virtual Environment aktivieren (falls nicht aktiv)
source venv/bin/activate

# Server starten
python manage.py runserver 0.0.0.0:8000

# Server im Hintergrund (mit nohup)
nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &

# Migrations
python manage.py makemigrations
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser

# Tests ausführen
pytest

# Export simulieren
python manage.py export_orders --dry-run

# Django Shell
python manage.py shell
```

### Docker Installation
```bash
# Container starten
docker-compose up -d

# Container stoppen
docker-compose down

# Logs ansehen
docker-compose logs -f web

# Command im Container ausführen
docker-compose exec web python manage.py <command>

# Shell im Container
docker-compose exec web bash

# Container neu bauen
docker-compose up -d --build
```

---

## 🧪 Test-Workflow

### 1. Frontend testen
```bash
# Browser öffnen: http://VM-IP:8000 (lokal) oder http://VM-IP:8080 (Docker)

# Registrierung testen
# - Neuen Account erstellen
# - E-Mail-Verifikation (wird in Konsole ausgegeben)

# Login testen
# - Mit test@example.com / testpass1234

# Bestellung testen
# - Produkte ansehen
# - In Warenkorb legen
# - Checkout durchführen
# - Bestellhistorie prüfen
```

### 2. Admin-Interface testen
```bash
# Browser: http://VM-IP:8000/admin

# Login: admin@example.com / admin1234567890

# Testen:
# - Produkte verwalten
# - Bestellungen ansehen
# - Export-Logs prüfen
```

### 3. API testen
```bash
# Beispiel: Produkte abrufen
curl http://VM-IP:8000/api/v1/products/

# Login via API
curl -X POST http://VM-IP:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass1234"}'
```

### 4. Export testen
```bash
# Lokale Installation
python manage.py export_orders --dry-run

# Docker
docker-compose exec web python manage.py export_orders --dry-run

# CSV-Datei prüfen
ls -la exports/  # oder /app/exports im Container
```

---

## 🔧 Troubleshooting Ubuntu VM

### Problem: "Invalid HTTP_HOST header" / Bad Request (400)
```bash
# .env Datei bearbeiten und VM IP-Adresse hinzufügen
nano .env

# Zeile ändern zu:
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.0.113  # Deine VM IP hier

# Server neu starten
python manage.py runserver 0.0.0.0:8000
```

### Problem: SSL_ERROR_RX_RECORD_TOO_LONG im Browser
```
Ursache: Browser versucht HTTPS, aber Server läuft auf HTTP

Lösung: Explizit http:// verwenden:
http://192.168.0.113:8000  (NICHT https://)

Falls Browser automatisch umleitet:
- Inkognito/Privater Modus verwenden
- Oder HSTS-Eintrag löschen (Browser-Einstellungen)
```

### Problem: Port nicht erreichbar
```bash
# Firewall-Status prüfen
sudo ufw status

# Port öffnen
sudo ufw allow 8000

# Oder Firewall deaktivieren (nur für Tests!)
sudo ufw disable
```

### Problem: PostgreSQL Connection Error
```bash
# PostgreSQL Status prüfen
sudo systemctl status postgresql

# PostgreSQL starten
sudo systemctl start postgresql

# PostgreSQL Logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Problem: Speicherplatz
```bash
# Speicher prüfen
df -h

# Docker aufräumen (falls verwendet)
docker system prune -a
```

### Problem: Python-Modul fehlt
```bash
# Virtual Environment aktivieren!
source venv/bin/activate

# Requirements neu installieren
pip install -r requirements.txt
```

### Problem: Migration-Fehler "InconsistentMigrationHistory"
```bash
# Datenbank komplett zurücksetzen (bei SQLite)
rm db.sqlite3
python manage.py migrate
python manage.py load_sample_data
```

### Problem: "no such table" Fehler
```bash
# Migrations erstellen und ausführen
python manage.py makemigrations
python manage.py migrate
```

### E-Mail-Verifikation ohne Mailserver testen
```bash
# Option 1: Verifikations-Token aus Console-Output kopieren
# Bei Registrierung wird der Link in der Console ausgegeben:
# "Verification URL: http://localhost:8000/verify-email/TOKEN"

# Option 2: User manuell verifizieren (Django Shell)
python manage.py shell

# In der Shell:
from bestellungen.models import CustomUser
user = CustomUser.objects.get(email='test@example.com')
user.is_email_verified = True
user.save()
exit()

# Option 3: Verwende die vorbereiteten Test-User (bereits verifiziert)
# User: test@example.com / testpass1234
# Admin: admin@example.com / admin1234567890
```

### Server im Hintergrund laufen lassen
```bash
# Option 1: nohup
nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &

# Option 2: systemd Service (empfohlen für Production)
# Siehe DEPLOYMENT.md für Details
```

---

## 🌐 Zugriff von Windows-PC aus

### 1. VM IP-Adresse finden
```bash
# Auf der VM:
hostname -I
# oder
ip addr show
```

### 2. Von Windows aus zugreifen
```
http://VM-IP:8000        # Lokale Installation
http://VM-IP:8080        # Docker Development
http://VM-IP             # Docker Production
```

### 3. Netzwerk-Voraussetzungen
- VM muss in Bridged Network sein (oder Port-Forwarding in Proxmox)
- Firewall auf VM muss Ports erlauben
- Firewall auf Windows muss ausgehende Verbindung erlauben

---

## 🎯 Nächste Schritte nach Installation

1. ✅ Alle 3 Accounts testen (Frontend, Admin, API)
2. ✅ Mindestens eine Testbestellung durchführen
3. ✅ Export-Command testen
4. ✅ API-Endpoints mit curl/Postman testen
5. ✅ Logs prüfen (server.log oder docker-compose logs)
6. ✅ README.md für Produktiv-Deployment lesen

---

## 📚 Weitere Dokumentation

- **README.md** - Komplette Dokumentation
- **DEPLOYMENT.md** - Production-Setup mit SSL/TLS
- **API.md** - Vollständige API-Dokumentation
- **CHANGELOG.md** - Versionshistorie

## ❓ Support

Bei Problemen:
1. Logs prüfen (`server.log` oder `docker-compose logs`)
2. README.md Troubleshooting-Sektion lesen
3. GitHub Issues: https://github.com/MrHartung/BaeckereiBestellungen/issues
