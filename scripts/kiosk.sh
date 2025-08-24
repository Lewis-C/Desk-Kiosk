#!/bin/bash

URL1="127.0.0.1:5000"

source /usr/files/scripts/python/.venv/bin/activate
python3 /usr/files/scripts/python/extract_data_handler_1h.py
python3 /usr/files/scripts/python/extract_data_handler_15m.py

sleep 1m

xset s noblank
xset s off
xset -dpms

unclutter -idle 0.5 -root &

sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/LC/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/LC/.config/chromium/Default/Preferences

/usr/bin/chromium-browser --noerrdialogs --disable-infobars --disk-cache-dir=/dev/null --disable-gpu --disk-cache-size=1 --kiosk $URL1  &

while true; do
   sleep 10
done
