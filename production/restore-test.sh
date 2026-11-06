#!/bin/sh
# Test de restauration : dernière sauvegarde → instance AIOStreams jetable sur 127.0.0.1:18097
# (mêmes secrets, données copiées), connexion « Famille » vérifiée, puis tout est retiré.
set -eu
P=/apps/sagora/production
D=/user/Lucas/backups/aiostreams
last=$(ls -1t "$D"/db-*.sqlite.zst | head -1)
work=$(mktemp -d /tmp/aiostreams-restore.XXXXXX)
trap 'docker logs aiostreams-restore-test 2>&1 | tail -5 | cut -c1-300 > /tmp/restore-last.log; docker rm -f aiostreams-restore-test >/dev/null 2>&1 || true; rm -rf "$work"' EXIT
mkdir -p "$work/data"
zstd -q -d "$last" -o "$work/data/db.sqlite"
cp "$P/data/famille-uuid" "$work/data/"
# Caches téléchargeables (bases anime, correspondances) : copiés pour démarrer vite, pas indispensables.
for d in anime-database id-mappings scene-mappings seadex; do [ -d "$P/data/$d" ] && cp -a "$P/data/$d" "$work/data/"; done
# docker run lit les guillemets littéralement, contrairement à compose.
sed "s/^\([A-Z_]*\)='\(.*\)'$/\1=\2/" "$P/secrets.env" > "$work/secrets.env"
image=$(sed -n 's/^ *image: \(ghcr.io[^ ]*\)/\1/p' "$P/compose.yaml" | head -1)
docker run -d --name aiostreams-restore-test -p 127.0.0.1:18097:3000 \
  --env-file "$P/settings.env" --env-file "$work/secrets.env" -e BASE_URL=http://127.0.0.1:18097 \
  -v "$work/data:/app/data" -m 1g "$image" >/dev/null
for i in $(seq 1 80); do
  curl -sf http://127.0.0.1:18097/api/v1/health >/dev/null 2>&1 && break; sleep 3
done
out=$(python3 "$P/tests/jellyfin_smoke.py" http://127.0.0.1:18097) || { echo "ÉCHEC de la restauration depuis $(basename "$last")"; exit 1; }
echo "$out" | head -1
echo "restauration OK depuis $(basename "$last")"
