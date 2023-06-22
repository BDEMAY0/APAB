#!/bin/bash

# Mise à jour des packages
sudo apt-get update

# Installation des dépendances système
sudo apt-get install -y python3-paramiko build-essential git python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev libgstreamer1.0-dev gstreamer1.0-plugins-{bad,base,good,ugly} gstreamer1.0-{omx,alsa} python3-setuptools libmtdev1 libpango1.0-dev lib32stdc++6 aircrack-ng

# Installation des dépendances Python via pip
pip3 install -r requirements.txt

echo "Installation terminée."
