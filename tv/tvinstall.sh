#!/bin/sh
export PATH=/usr/local/bin:$PATH
D=192.168.1.38:5555
for i in 1 2 3 4 5 6 7 8; do
  adb kill-server >/dev/null 2>&1; adb connect $D >/dev/null 2>&1; sleep 3
  if adb devices | grep -q "$D.*device$"; then
    out=$(adb -s $D install -r "$1" 2>&1 | tail -1); echo "essai $i: $out"
    case "$out" in Success*) exit 0;; *INSTALL_FAILED*|*Failure*) exit 1;; esac
  fi
  sleep 4
done
exit 1
