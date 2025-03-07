
## Inhaltsverzeichnis

- [Git](#git)
    - [1. Git installieren](#1-git-installieren)
    - [2. SSH-Schlüssel erstellen](#2-ssh-schlüssel-erstellen)
        - [1. Terminal öffnen](#1-terminal-öffnen)
        - [2. SSH-Schlüssel erstellen](#2-ssh-schlüssel-erstellen-mit-dem-befehl)
    - [3. SSH-Schlüssel SSH-Agent hinzufügen](#3-ssh-schlüssel-ssh-agent-hinzufügen)
    - [4. SSH-Schlüssel zu GitHub hinzufügen](#4-ssh-schlüssel-zu-github-hinzufügen)
    - [5. Klonen in Terminal](#5-klonen-in-terminal)

- [Docker starten und bauen der Container](#docker-starten-und-bauen-der-container)

- [Starten der Anwendung mit Frontend](#starten-der-anwendung-mit-frontend)

- [Starten der Anwendung ohne Frontend](#starten-der-anwendung-ohne-frontend)

- [Docker aufräumen](#docker-aufräumen)

-------------------------------------------------------------------------------------

# Git

## 1. [Git](https://git-scm.com/downloads) installieren.
## 2. SSH-Schlüssel erstellen:

### 1. Terminal öffnen
### 2. SSH-Schlüssel erstellen mit dem Befehl:

   ```bash
      ssh-keygen -t rsa -b 4096 -C "email@example.com"
   ```

## 3. SSH-Schlüssel SSH-Agent hinzufügen:

   ```bash
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_rsa
   ```

## 4. SSH-Schlüssel zu GitHub hinzufügen

   ````bash
   cat ~/.ssh/id_rsa.pub
   ````

-in GitHub:
- auf Profilbild oben rechts klicken und Settings auswählen
    - SSH and GPG keys auswählen
    - Klicke auf New SSH key, füge den kopierten Schlüssel ein und speichere.

## 5. klonen in Terminal den Befehl ausführen:

### SSH

   ````bash
   git@github.com:USERNAME/einzelhandel.git
   ````

Verbindung testen:

    - ssh -T git@github.com

-------------------------------------------------------------------------------------

# Docker starten und bauen der Container

Voraussetzung: Docker muss installiert sein, entweder [Docker Desktop](https://www.docker.com/products/docker-desktop/)
oder per Terminal (für Linux Nutzer)

1. im Projektverzeichnis einen Ordner secrets anlegen und in diesem eine Datei github_credentials.txt
2. in die Datei die folgenden Werte kopieren
    ````bash
    PEPPER_KEY=my-secret-pepper
     POSTGRES_PASSWORD=a2GtDwGcCYpPMfzb9T
     RABBITMQ_PASSWORD=5UtFfSysADFUre8r1fU576
     ENCRYPTION_KEY=y34iezZ6HNempLRypUYriwYewur72YhQslzuGGXymwA=
     mcqQVi84zBN7iyrfmwFUT26ljn94Sw9V5EydCUrrds=rd
     REDIS_PASSWORD=your_redis_password
     SECRET_KEY=supersecretkey
     JWT_SECRET_KEY=jwtsecretkey
     ````
3. ebenfalls in dem Projektverzeichnis einzelhandel/ muss eine .env angelegt werden
   ````bash
   PEPPER_KEY=my-secret-pepper
   POSTGRES_PASSWORD=a2GtDwGcCYpPMfzb9T
   RABBITMQ_PASSWORD=5UtFfSysADFUre8r1fU576
   ENCRYPTION_KEY=y34iezZ6HNempLRypUYriwYewur72YhQslzuGGXymwA=
   mcqQVi84zBN7iyrfmwFUT26ljn94Sw9V5EydCUrrds=rd
   REDIS_PASSWORD=your_redis_password
   SECRET_KEY=supersecretkey
   JWT_SECRET_KEY=jwtsecretkey
   ````

1. Docker Daemon starten, in dem Docker Desktop gestartet wird oder per Terminal.
2. Bauen der Docker Images mit dem Befehl:
    ````bash
    #Powershell
    $env:DOCKER_BUILDKIT=1
    #CMD
    set DOCKER_BUILDKIT=1
   
    docker-compose -f docker-compose.yml build --parallel
    docker-compose -f docker-compose.yml up
    ````
3. der Postgres Container muss manchmal noch mal gestartet werden, in dem Fall in Docker Desktop den Startbutton klicken
   oder in der Konsole
    ````bash
    docker-compose up postgres_container
    ````

# Starten der Anwendung mit Frontend

1. warten bis alle Container vollständig gebaut sind ca. 1-2min
2. prüfen ob die Container laufen sonst starten mit:
3. Frontend über http://localhost:4200 aufrufen

# Starten der Anwendung ohne Frontend

Vorausetzung: wenn Requests nicht per CURL sondern über eine Collection genutzt werden sollen, dann muss ein API Client   
heruntergeladen werden wie [Postman](https://www.postman.com/downloads/) oder
[Bruno](https://docs.usebruno.com/get-started/bruno-basics/download)

1. nachdem der Client installiert wurde kann die Collection
   [Einzelhandel.postman_collection.json](https://drive.google.com/file/d/1r-va-SVz5_67Owtehy-zt-iI5mkOvfPa/view?usp=sharing)
   importiert werden
2. existiert noch kein User muss zuerst der Endpunkt registrieren ausgeführt werden
3. wurde der Body im Endpunkt registrieren angepasst, dann müssen die Daten im Body vom login ebenfalls angepasst werden
4. jetzt login ausführen und den Inhalt des Response Body vom token ohne " " kopieren
5. den kopierten Token in das Event ImageUploaded im Header Authorization hinter Bearer mit einem Leerzeichen getrennt
   einfügen und senden

#### Per Curl:
- Endpunkt registrieren:
    ````bash
    curl --location "http://localhost/user-management/auth/register" ^
    --header "Content-Type: application/json" ^
    --data "{\"username\": \"testuser5\", \"password\": \"securepassword\", \"role\": \"Mitarbeiter\"}"
    ````
- Endpunkt login:
    ````bash
    curl -c cookies.txt --location "http://localhost/user-management/auth/login" ^
    --header "Content-Type: application/json" ^
    --data "{\"username\": \"testuser5\", \"password\": \"securepassword\"}"
    ````
- Event ImageUploaded:
     ````bash
    curl -b cookies.txt --location "http://localhost/eventing-service/publish/ImageUploaded" ^
    --form "type=ProcessFiles" ^
    --form "filename=@Pfad\desBildes.jpg"
     ````

# Docker aufräumen

 ````bash
docker stop $(docker ps -aq) #stopt laufende Container
docker rm $(docker ps -aq) # Container werden gelöscht
docker rmi $(docker images -q) -f # Images werden gelöscht  
docker volume rm $(docker volume ls -q) # Volumes werden gelöscht  
docker network rm $(docker network ls -q) # Netzwerke werden gelöscht
docker system prune -a --volumes -f  # Vollständige Bereinigung von Docker 
 ````

