# 1. [Git](https://git-scm.com/downloads) installieren.
# 2. SSH-Schlüssel erstellen:

   # 1. Terminal öffnen 
   # 2. SSH-Schlüssel erstellen mit dem Befehl:

   ```bash
      ssh-keygen -t rsa -b 4096 -C "email@example.com"
   ```
   
   # 3. SSH-Schlüssel SSH-Agent hinzufügen:
   
   ```bash
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_rsa
   ```
   
   # 4. SSH-Schlüssel zu GitHub hinzufügen
    
   ````bash
   cat ~/.ssh/id_rsa.pub
   ````
   
   -in GitHub:
- auf Profilbild oben rechts klicken und Settings auswählen
    - SSH and GPG keys auswählen
    - Klicke auf New SSH key, füge den kopierten Schlüssel ein und speichere.

    # 5. klonen in Terminal den Befehl ausführen:

    # SSH

   ````bash
   git@github.com:USERNAME/einzelhandel.git
   ````
    
    Verbindung testen:
    - ssh -T git@github.com