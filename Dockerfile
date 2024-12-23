FROM postgres:latest

# Kopiere das Skript in das Image
COPY update_pg_hba.sh /docker-entrypoint-initdb.d/update_pg_hba.sh

# Rechte setzen
RUN chmod +x /docker-entrypoint-initdb.d/update_pg_hba.sh