
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
oder per Terminal (ehr für Linux Nutzer, unter Windows recht umständlich umzusätzen) 

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
3. Erstellen und Starten der Docker-Container mit dem Befehl:
    ````bash
    docker-compose -f docker-compose.yml up
    ````
4. der Postgres Container muss manchmal noch mal gestartet werden, in dem Fall in Docker Desktop den Startbutton klicken
oder in der Konsole
    ````bash
    docker-compose up postgres_container
    ````
# GPU unterstützung einrichten

1. unter Windows mus WSL2 aktiviert sein 
2. powershell öffnen
    ````bash
      wsl --install
      sudo apt update && sudo apt upgrade -y
    ````
3. NVIDIA Container Toolkit installieren https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
4. prüfen ob nvidia default runtime ist und prüfen ob die config Dateien vorhanden sind
    ````bash
      docker info | grep -i runtime
      cat /etc/docker/daemon.json
      cat /etc/containerd/config.toml
    ````
5. falls nicht erstellen
    ````bash
    mkdir -p /etc/docker/daemon.json

    sudo tee /etc/docker/daemon.json <<EOF
    {
    "runtimes": {
    "nvidia": {
    "path": "nvidia-container-runtime",
    "runtimeArgs": []
    }
    }
    }
    EOF
   
   sudo apt install -y containerd
   
      sudo mkdir -p /etc/containerd/config.toml

    sudo tee /etc/docker/daemon.json <<EOF
    disabled_plugins = []
    imports = []
    oom_score = 0
    plugin_dir = ""
    required_plugins = []
    root = "/var/lib/containerd"
    state = "/run/containerd"
    temp = ""
    version = 2
    
    [cgroup]
    path = ""
    
    [debug]
    address = ""
    format = ""
    gid = 0
    level = ""
    uid = 0
    
    [grpc]
    address = "/run/containerd/containerd.sock"
    gid = 0
    max_recv_message_size = 16777216
    max_send_message_size = 16777216
    tcp_address = ""
    tcp_tls_ca = ""
    tcp_tls_cert = ""
    tcp_tls_key = ""
    uid = 0
    
    [metrics]
    address = ""
    grpc_histogram = false
    
    [plugins]
    
    [plugins."io.containerd.gc.v1.scheduler"]
    deletion_threshold = 0
    mutation_threshold = 100
    pause_threshold = 0.02
    schedule_delay = "0s"
    startup_delay = "100ms"
    
    [plugins."io.containerd.grpc.v1.cri"]
    cdi_spec_dirs = ["/etc/cdi", "/var/run/cdi"]
    device_ownership_from_security_context = false
    disable_apparmor = false
    disable_cgroup = false
    disable_hugetlb_controller = true
    disable_proc_mount = false
    disable_tcp_service = true
    drain_exec_sync_io_timeout = "0s"
    enable_cdi = false
    enable_selinux = false
    enable_tls_streaming = false
    enable_unprivileged_icmp = false
    enable_unprivileged_ports = false
    ignore_deprecation_warnings = []
    ignore_image_defined_volumes = false
    image_pull_progress_timeout = "5m0s"
    image_pull_with_sync_fs = false
    max_concurrent_downloads = 3
    max_container_log_line_size = 16384
    netns_mounts_under_state_dir = false
    restrict_oom_score_adj = false
    sandbox_image = "registry.k8s.io/pause:3.8"
    selinux_category_range = 1024
    stats_collect_period = 10
    stream_idle_timeout = "4h0m0s"
    stream_server_address = "127.0.0.1"
    stream_server_port = "0"
    systemd_cgroup = false
    tolerate_missing_hugetlb_controller = true
    unset_seccomp_profile = ""
    
        [plugins."io.containerd.grpc.v1.cri".cni]
          bin_dir = "/opt/cni/bin"
          conf_dir = "/etc/cni/net.d"
          conf_template = ""
          ip_pref = ""
          max_conf_num = 1
          setup_serially = false
     
        [plugins."io.containerd.grpc.v1.cri".containerd]
          default_runtime_name = "nvidia"
          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia]
            runtime_type = "io.containerd.runc.v2"
            privileged_without_host_devices = false
            pod_annotations = ["io.kubernetes.cri.runtime"]
            [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia.options]
              BinaryName = "/usr/bin/nvidia-container-runtime"
     
          [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime]
            base_runtime_spec = ""
            cni_conf_dir = ""
            cni_max_conf_num = 0
            container_annotations = []
            pod_annotations = []
            privileged_without_host_devices = false
            privileged_without_host_devices_all_devices_allowed = false
            runtime_engine = ""
            runtime_path = ""
            runtime_root = ""
            runtime_type = ""
            sandbox_mode = ""
            snapshotter = ""
     
            [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime.options]
     
          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
     
     
            [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
              base_runtime_spec = ""
              cni_conf_dir = ""
              cni_max_conf_num = 0
              container_annotations = []
              pod_annotations = []
              privileged_without_host_devices = false
              privileged_without_host_devices_all_devices_allowed = false
              runtime_engine = ""
              runtime_path = ""
              runtime_root = ""
              runtime_type = "io.containerd.runc.v2"
              sandbox_mode = "podsandbox"
              snapshotter = ""
     
              [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
                BinaryName = ""
                CriuImagePath = ""
                CriuPath = ""
                CriuWorkPath = ""
                IoGid = 0
                IoUid = 0
                NoNewKeyring = false
                NoPivotRoot = false
                Root = ""
                ShimCgroup = ""
                SystemdCgroup = false
     
          [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime]
            base_runtime_spec = ""
            cni_conf_dir = ""
            cni_max_conf_num = 0
            container_annotations = []
            pod_annotations = []
            privileged_without_host_devices = false
            privileged_without_host_devices_all_devices_allowed = false
            runtime_engine = ""
            runtime_path = ""
            runtime_root = ""
            runtime_type = ""
            sandbox_mode = ""
            snapshotter = ""
     
            [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime.options]
     
        [plugins."io.containerd.grpc.v1.cri".image_decryption]
          key_model = "node"
     
        [plugins."io.containerd.grpc.v1.cri".registry]
          config_path = ""
     
          [plugins."io.containerd.grpc.v1.cri".registry.auths]
     
          [plugins."io.containerd.grpc.v1.cri".registry.configs]
     
          [plugins."io.containerd.grpc.v1.cri".registry.headers]
     
          [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
     
        [plugins."io.containerd.grpc.v1.cri".x509_key_pair_streaming]
          tls_cert_file = ""
          tls_key_file = ""
    
    [plugins."io.containerd.internal.v1.opt"]
    path = "/opt/containerd"
    
    [plugins."io.containerd.internal.v1.restart"]
    interval = "10s"
    
    [plugins."io.containerd.internal.v1.tracing"]
    
    [plugins."io.containerd.metadata.v1.bolt"]
    content_sharing_policy = "shared"
    
    [plugins."io.containerd.monitor.v1.cgroups"]
    no_prometheus = false
    
    [plugins."io.containerd.nri.v1.nri"]
    disable = true
    disable_connections = false
    plugin_config_path = "/etc/nri/conf.d"
    plugin_path = "/opt/nri/plugins"
    plugin_registration_timeout = "5s"
    plugin_request_timeout = "2s"
    socket_path = "/var/run/nri/nri.sock"
    
    [plugins."io.containerd.runtime.v1.linux"]
    no_shim = false
    runtime = "runc"
    runtime_root = ""
    shim = "containerd-shim"
    shim_debug = false
    
    [plugins."io.containerd.runtime.v2.task"]
    platforms = ["linux/amd64"]
    sched_core = false
    
    [plugins."io.containerd.service.v1.diff-service"]
    default = ["walking"]
    
    [plugins."io.containerd.service.v1.tasks-service"]
    blockio_config_file = ""
    rdt_config_file = ""
    
    [plugins."io.containerd.snapshotter.v1.aufs"]
    root_path = ""
    
    [plugins."io.containerd.snapshotter.v1.blockfile"]
    fs_type = ""
    mount_options = []
    root_path = ""
    scratch_file = ""
    
    [plugins."io.containerd.snapshotter.v1.btrfs"]
    root_path = ""
    
    [plugins."io.containerd.snapshotter.v1.devmapper"]
    async_remove = false
    base_image_size = ""
    discard_blocks = false
    fs_options = ""
    fs_type = ""
    pool_name = ""
    root_path = ""
    
    [plugins."io.containerd.snapshotter.v1.native"]
    root_path = ""
    
    [plugins."io.containerd.snapshotter.v1.overlayfs"]
    mount_options = []
    root_path = ""
    sync_remove = false
    upperdir_label = false
    
    [plugins."io.containerd.snapshotter.v1.zfs"]
    root_path = ""
    
    [plugins."io.containerd.tracing.processor.v1.otlp"]
    
    [plugins."io.containerd.transfer.v1.local"]
    config_path = ""
    max_concurrent_downloads = 3
    max_concurrent_uploaded_layers = 3
    
        [[plugins."io.containerd.transfer.v1.local".unpack_config]]
          differ = ""
          platform = "linux/amd64"
          snapshotter = "overlayfs"
    
    [proxy_plugins]
    
    [stream_processors]
    
    [stream_processors."io.containerd.ocicrypt.decoder.v1.tar"]
    accepts = ["application/vnd.oci.image.layer.v1.tar+encrypted"]
    args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
    env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
    path = "ctd-decoder"
    returns = "application/vnd.oci.image.layer.v1.tar"
    
    [stream_processors."io.containerd.ocicrypt.decoder.v1.tar.gzip"]
    accepts = ["application/vnd.oci.image.layer.v1.tar+gzip+encrypted"]
    args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
    env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
    path = "ctd-decoder"
    returns = "application/vnd.oci.image.layer.v1.tar+gzip"
    
    [timeouts]
    "io.containerd.timeout.bolt.open" = "0s"
    "io.containerd.timeout.metrics.shimstats" = "2s"
    "io.containerd.timeout.shim.cleanup" = "5s"
    "io.containerd.timeout.shim.load" = "5s"
    "io.containerd.timeout.shim.shutdown" = "3s"
    "io.containerd.timeout.task.state" = "2s"
    
    [ttrpc]
    address = ""
    gid = 0
    uid = 0
    EOF
    ````
6. in Docker Desktop in dne Einstellungen prüfen ob unter General -> 
Use the WSL 2 based engine (Windows Home can only run the WSL 2 backend) ein häckchen gesetzt ist
und unter Resources -> WSL integration -> Ubuntu schieberegler aktivieren 
7. mit Apply & restart bestätigen
8. Docker komplett schließen mit rechtsklick Quit Docker Desktop

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
    --form "filename=@Pfad\desBildes.jpg" ^
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

