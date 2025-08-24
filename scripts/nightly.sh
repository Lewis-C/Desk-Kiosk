#!/bin/bash

echo "---" >> /usr/files/logs/nightly_log.txt
date >> /usr/files/logs/nightly_log.txt
sudo apt update >> /usr/files/logs/nightly_log.txt
sudo apt full-upgrade -y >> /usr/files/logs/nightly_log.txt
sudo apt autoremove -y >> /usr/files/logs/nightly_log.txt
reboot