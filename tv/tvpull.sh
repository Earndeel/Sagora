#!/bin/sh
export PATH=/usr/local/bin:$PATH
D=192.168.1.38:5555
for i in 1 2 3 4 5 6; do
  adb devices | grep -q "$D.*device$" && adb -s $D pull "$1" "$2" >/dev/null 2>&1 && exit 0
  adb kill-server >/dev/null 2>&1; adb connect $D >/dev/null 2>&1; sleep 3
done
exit 1
