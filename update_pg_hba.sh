#!/bin/bash

# Pfad zur pg_hba.conf
PG_HBA="/var/lib/postgresql/data/pg_hba.conf"

# Sicherstellen, dass die Datei existiert
if [ -f "$PG_HBA" ]; then
    echo "Ändere pg_hba.conf: trust zu scram-sha-256..."

    # Ersetze 'trust' durch 'scram-sha-256'
    sed -i 's/trust/scram-sha-256/g' "$PG_HBA"

    echo "pg_hba.conf erfolgreich aktualisiert. Neuladen der PostgreSQL-Konfiguration..."

    # PostgreSQL-Konfiguration neu laden
    pg_ctl reload

    echo "Konfiguration neu geladen."
else
    echo "Fehler: $PG_HBA nicht gefunden."
    exit 1
fi
