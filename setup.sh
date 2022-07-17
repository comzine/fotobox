#!/bin/bash

echo "Enabling Camera"
# enabling raspi legacy camera
# disabling automount in file explorer (gui)
# user pi

echo "Updating System"
sudo apt update
yes | sudo apt upgrade

echo "Installing prerequirements"
yes | sudo apt install python3 python3-picamera python3-pyqt5 python3-pyqt5.qtwebkit python3-rpi.gpio gphoto2 printer-driver-gutenprint
# Suggested tools: sxiv tmux vim usbmount x11vnc

# be careful! maybe harmful
cupsctl --remote-admin --remote-any

echo "Installing Fotobox"
git clone https://github.com/comzine/fotobox.git /home/pi/fotobox

mkdir -p ~/.config/autostart

echo "[Desktop Entry]" > ~/.config/autostart/fotobox.desktop
echo "Type=Application" >> ~/.config/autostart/fotobox.desktop
echo "Name=Fotobox" >> ~/.config/autostart/fotobox.desktop
echo "Exec=/bin/bash /home/pi/autostart.sh" >> ~/.config/autostart/fotobox.desktop


echo "export DISPLAY=:0" > ~/autostart.sh
echo "pkill -f gphoto2" >> ~/autostart.sh
echo "xset s noblank" >> ~/autostart.sh
echo "xset s off" >> ~/autostart.sh
echo "xset -dpms" >> ~/autostart.sh
echo "cancel -a fotoprinter" >> ~/autostart.sh
echo "cupsenable fotoprinter" >> ~/autostart.sh
echo "while true" >> ~/autostart.sh
echo "do" >> ~/autostart.sh
echo "cd ~/fotobox/ ; python3 fotobox.py | tee fotobox.log" >> ~/autostart.sh
echo "done" >> ~/autostart.sh
chmod a+x ~/autostart.sh

echo "Syncing..."
sudo sync

