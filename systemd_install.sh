#!/bin/sh

user="$(whoami)"
repo_path="$(dirname "$(readlink -f "$0")")"
python_path="$(command -v python3)"

__body="
[Unit]
Description=Remote SMART for Home Assistant
After=network.target

[Service]
Type=simple
ExecStart=${python_path} -u ${repo_path}/ha_remote_smart/main.py --config ${repo_path}/config_local.yaml
WorkingDirectory=${repo_path}/ha_remote_smart
Restart=always

[Install]
WantedBy=multi-user.target
"
echo "$__body" > "${repo_path}/remote_smart.service"

sudo mv -f "${repo_path}/remote_smart.service" /etc/systemd/system/remote_smart.service

sudo systemctl daemon-reload
sudo systemctl enable remote_smart.service
sudo systemctl start remote_smart.service
