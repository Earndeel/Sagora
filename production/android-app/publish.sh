#!/bin/sh
# Appli Android Sagora : récupère la construction non signée de GitHub Actions (dépôt privé Earndeel/sagora),
# la signe ici avec la clé de Sagora (Bitwarden « Sagora · Android signature », en mémoire seulement, jamais envoyée
# à GitHub), vérifie les signatures et publie APK + update.json là où l'appli cherche ses mises à jour
# (https://sagora.walter-ai.cloud/sagora-app/android/, BuildConfig.UPDATE_FEED).
# Usage : publish.sh [id de l'exécution GitHub]   (sans id : la dernière réussie)
set -eu
export PATH=/root/.local/bin:$PATH
HERE=$(cd "$(dirname "$0")" && pwd)
FEED=/apps/sagora/production/front/app/android
SIGNER="java -jar $HERE/tools/apksigner.jar"
RUN=${1:-$(gh run list -R Earndeel/sagora --workflow sagora-android.yml --status success --limit 1 --json databaseId -q '.[0].databaseId')}
[ -n "$RUN" ] || { echo "aucune construction réussie"; exit 1; }
umask 077
W=$(mktemp -d /dev/shm/sagora-apk-XXXX)
trap 'rm -rf "$W"' EXIT
gh run download "$RUN" -R Earndeel/sagora -n sagora-android -D "$W/in"
walter-secret get "Sagora · Android signature (keystore base64)" notes | base64 -d > "$W/sagora.p12"
SAGORA_KS_PASS=$(walter-secret get "Sagora · Android signature (mot de passe)" password)
export SAGORA_KS_PASS
mkdir -p "$W/out"
apks='{}'
for abi in arm64-v8a armeabi-v7a x86_64; do
  name="sagora-android-$abi.apk"
  $SIGNER sign --ks "$W/sagora.p12" --ks-type PKCS12 --ks-key-alias sagora \
    --ks-pass env:SAGORA_KS_PASS --key-pass env:SAGORA_KS_PASS \
    --out "$W/out/$name" "$W/in/sagora-android-$abi-unsigned.apk"
  $SIGNER verify --print-certs "$W/out/$name" | grep -q "CN=Sagora" || { echo "signature non vérifiée : $name"; exit 1; }
  apks=$(python3 -I -c 'import json,sys; d=json.loads(sys.argv[1]); d[sys.argv[2]]={"name":sys.argv[3],"sha256":sys.argv[4],"size":int(sys.argv[5])}; print(json.dumps(d))' \
    "$apks" "$abi" "$name" "$(sha256sum "$W/out/$name" | cut -d' ' -f1)" "$(stat -c %s "$W/out/$name")")
done
python3 -I -c 'import json,sys; b=json.load(open(sys.argv[1])); print(json.dumps({"version":b["version"],"versionCode":b["versionCode"],"apks":json.loads(sys.argv[2])}, indent=1))' \
  "$W/in/build.json" "$apks" > "$W/out/update.json"
umask 022
mkdir -p "$FEED"
cp "$W/out/"*.apk "$FEED/"
cp "$W/out/update.json" "$FEED/update.json.tmp" && mv "$FEED/update.json.tmp" "$FEED/update.json"
chmod 644 "$FEED"/*
echo "publié (exécution $RUN) :"; cat "$FEED/update.json"
