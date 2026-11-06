#!/bin/sh
# Bascule stremio.walter-ai.cloud de l'ancien Stremio Web (localhost:18080) vers l'application AIOStreams
# (entrée nginx localhost:18085). Seule la règle de ce domaine change dans le tunnel ; DNS inchangé.
# Retour arrière : rollback-domain.sh
set -eu
P=/apps/sagora/production
CFG=/root/.cloudflared/config.yml
curl -sf http://127.0.0.1:18085/jellyfin/web/ >/dev/null || { echo "l'application ne répond pas en local : bascule annulée"; exit 1; }
cp -p "$CFG" "/user/Lucas/backups/changes/cloudflared-before-switch-$(date +%Y%m%d-%H%M%S).yml"
python3 - "$CFG" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
old = "- hostname: stremio.walter-ai.cloud\n  service: http://localhost:18080\n"
new = "- hostname: stremio.walter-ai.cloud\n  service: http://localhost:18085\n"
if new not in s:
    assert s.count(old) == 1, "règle stremio introuvable"
    s = s.replace(old, new)
# La route de préproduction (jamais publiée en DNS) n'a plus lieu d'être.
s = s.replace("- hostname: aiostreams-preprod.walter-ai.cloud\n  service: http://localhost:18090\n", "")
open(p, "w").write(s)
PY
cloudflared tunnel --config "$CFG" ingress validate
systemctl restart cloudflared-tunnel
for i in $(seq 1 30); do
  curl -sf https://stremio.walter-ai.cloud/api/v1/health >/dev/null 2>&1 && break; sleep 4
done
curl -sf https://stremio.walter-ai.cloud/api/v1/health >/dev/null || { echo "le domaine ne sert pas encore AIOStreams"; exit 1; }
# L'ancien Stremio reste sur le disque, arrêté et sans redémarrage automatique.
for c in stremio-web stremio-preprod-web-1 stremio-server; do
  docker update --restart=no "$c" >/dev/null 2>&1 || true
  docker stop "$c" >/dev/null 2>&1 || true
done
touch "$P/state/public-live"
echo "stremio.walter-ai.cloud sert AIOStreams"
