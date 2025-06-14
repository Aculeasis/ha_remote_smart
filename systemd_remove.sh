#!/bin/sh

sudo systemctl stop remote_smart.service
sudo systemctl disable remote_smart.service
sudo rm /etc/systemd/system/remote_smart.service
sudo systemctl daemon-reload
