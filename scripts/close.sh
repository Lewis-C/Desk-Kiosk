#!/bin/bash

export DISPLAY=:0 && export XAUTHORITY=/home/LC/.Xauthority && xdotool get_desktop

WID=$(xdotool search --onlyvisible --class chromium|head -1)
xdotool windowactivate ${WID}
xdotool key alt+F4