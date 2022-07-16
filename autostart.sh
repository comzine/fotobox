#!/bin/bash
xset s noblank
xset s off
xset -dpms
cancel -a photoprinter
cupsenable photoprinter
while true
do
	cd /home/pi/fotobox ; /usr/bin/python3 ./fotobox.py &> fotoboxLog.txt
done
