#!/bin/sh
# Connexion ADB instable (voir skill tv-dongle-maintenance) : reconnecter jusqu'à « device », puis tout en un seul shell.
export PATH=/usr/local/bin:$PATH
D=192.168.1.38:5555
for i in 1 2 3 4 5 6; do
  adb kill-server >/dev/null 2>&1; adb connect $D >/dev/null 2>&1; sleep 3
  adb devices | grep -q "$D.*device$" && break
  sleep 4
done
adb -s $D shell "$1"
