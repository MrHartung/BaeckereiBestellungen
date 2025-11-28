# Deployment Checkliste

## Pre-Deployment

### 1. Code Review
- [ ] Alle Tests laufen durch
- [ ] Keine TODO/FIXME im Production-Code
- [ ] Keine Debug-Statements
- [ ] Code-Review abgeschlossen

### 2. Konfiguration
- [ ] `.env` Datei mit Production-Werten erstellt
- [ ] `DEBUG = False`
- [ ] Starkes `SECRET_KEY` generiert
- [ ] `ALLOWED_HOSTS` konfiguriert
- [ ] Database Credentials sicher
- [ ] SMTP E-Mail konfiguriert

### 3. Datenbank
- [ ] PostgreSQL installiert und läuft
- [ ] Database Backup-Strategie definiert
- [ ] Migrations getestet
- [ ] Initial Data geladen (falls nötig)

### 4. Server Setup
- [ ] Docker & docker-compose installiert
- [ ] Firewall konfiguriert (Ports 80, 443)
- [ ] SSL/TLS Zertifikat erstellt (Let's Encrypt)
- [ ] Domain konfiguriert (DNS)

### 5. Sicherheit
- [ ] SSL/TLS aktiviert
- [ ] Security Headers gesetzt
- [ ] Rate-Limiting aktiv
- [ ] CSRF Protection aktiv
- [ ] Strong Password Policy

## Deployment

### 1. Build & Start
```bash
# Clone Repository
git clone <repo-url> /opt/baecker
cd /opt/baecker

# Environment konfigurieren
cp .env.example .env
vim .env  # Production-Werte eintragen

# Build & Start
docker-compose up -d --build
```

### 2. Initialisierung
```bash
# Migrations
docker-compose exec web python manage.py migrate

# Static Files
docker-compose exec web python manage.py collectstatic --noinput

# Superuser
docker-compose exec web python manage.py createsuperuser

# Optional: Sample Data
docker-compose exec web python manage.py load_sample_data
```

### 3. Nginx SSL
```bash
# Let's Encrypt Zertifikat
sudo certbot certonly --nginx -d your-domain.com

# Nginx Config anpassen (HTTPS aktivieren)
vim nginx/conf.d/default.conf

# Restart
docker-compose restart nginx
```

## Post-Deployment

### 1. Funktionstest
- [ ] Homepage lädt
- [ ] Admin-Login funktioniert
- [ ] Benutzer-Registrierung funktioniert
- [ ] E-Mail-Versand funktioniert
- [ ] Produkt-Bestellung funktioniert
- [ ] API-Endpoints erreichbar

### 2. Monitoring Setup
- [ ] Log-Rotation konfiguriert
- [ ] Uptime-Monitoring (z.B. UptimeRobot)
- [ ] Error-Tracking (z.B. Sentry)
- [ ] Backup-Cron-Job eingerichtet

### 3. Backup-Test
```bash
# Database Backup
docker-compose exec db pg_dump -U baecker_user baecker_db > backup_test.sql

# Restore Test
docker-compose exec -T db psql -U baecker_user baecker_db < backup_test.sql
```

### 4. Performance
- [ ] Static Files cachen
- [ ] Database Indexes geprüft
- [ ] Gunicorn Worker optimiert
- [ ] Nginx Compression aktiv

## Export Setup (Windows Server)

### 1. Windows Server Vorbereitung
- [ ] Python 3.11+ installiert
- [ ] pyodbc installiert (`pip install pyodbc`)
- [ ] Access 97 ODBC Driver installiert
- [ ] VPN zu Bäcker-Netzwerk konfiguriert

### 2. Export Script Setup
```cmd
# Script kopieren
copy \\django-server\exports\write_to_access.py C:\BaeckerExport\

# Config anpassen
notepad C:\BaeckerExport\write_to_access.py
# ACCESS_DB_PATH = r'\\baecker-server\share\baecker.mdb'

# Test-Run
python C:\BaeckerExport\write_to_access.py test_export.csv
```

### 3. Task Scheduler
- [ ] Task erstellt: Täglich 04:00 UTC
- [ ] Aktion: `python C:\BaeckerExport\write_to_access.py <csv_file>`
- [ ] E-Mail-Benachrichtigung bei Fehler
- [ ] VPN Auto-Connect aktiviert

## Rollback Plan

Falls Probleme auftreten:

1. **Stopp Services:**
   ```bash
   docker-compose down
   ```

2. **Restore Backup:**
   ```bash
   docker-compose up -d db
   docker-compose exec -T db psql -U baecker_user baecker_db < backup_latest.sql
   ```

3. **Previous Version deployen:**
   ```bash
   git checkout <previous-tag>
   docker-compose up -d --build
   ```

## Wartung

### Täglich
- [ ] Logs überprüfen
- [ ] Export-Status prüfen
- [ ] Uptime-Monitoring checken

### Wöchentlich
- [ ] Backup-Test
- [ ] Security Updates prüfen
- [ ] Disk Space prüfen

### Monatlich
- [ ] Dependency Updates
- [ ] Performance Review
- [ ] Security Audit

## Kontakt im Notfall

- **Tech-Team:** tech@example.com
- **Server-Admin:** admin@example.com
- **Hosting:** support@hosting.com
- **Bäcker-IT:** it@baecker.de
