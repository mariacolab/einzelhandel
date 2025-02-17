#!/bin/sh
echo "Fixing /etc/davfs2/secrets permissions..."
chmod 600 /etc/davfs2/secrets

echo "Checking if rclone is installed..."
if ! command -v rclone &> /dev/null
then
    echo "rclone not found, installing..."
    apt update && apt install -y rclone
fi

echo "Copying files from WebDAV..."
while true; do
    echo "Syncing WebDAV..."
    rclone sync webdav:/ /mnt/gdrive --progress --config=/config/rclone.conf --log-level ERROR > /dev/null 2>&1
    echo "Sleeping for 1 hour..."
    sleep 5
done &

exec gunicorn --bind 0.0.0.0:5005 app:app

