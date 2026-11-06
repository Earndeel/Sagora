#!/bin/sh
# Sauvegarde quotidienne de l'application familiale AIOStreams :
# base SQLite (copie cohérente à chaud), configuration et interface déployée → /user/Lucas/backups/aiostreams
# (inclus dans la sauvegarde restic hors site). Garde 14 jours de sauvegardes faites par ce script.
set -eu
P=/apps/sagora/production
D=/user/Lucas/backups/aiostreams
ts=$(date -u +%Y%m%dT%H%M%SZ)
umask 077
mkdir -p "$D"
python3 - "$P/data/db.sqlite" "$D/db-$ts.sqlite" <<'PY'
import sqlite3, sys
src = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
dst = sqlite3.connect(sys.argv[2])
src.backup(dst)
ok = dst.execute("pragma integrity_check").fetchone()[0]
dst.close(); src.close()
if ok != "ok":
    sys.exit(f"intégrité: {ok}")
PY
zstd -q -19 --rm "$D/db-$ts.sqlite"
tar -C "$P" -czf "$D/config-$ts.tar.gz" compose.yaml settings.env front config web-dist/BUILD data/famille-uuid render-secrets.sh backup.sh README.md 2>/dev/null || \
  tar -C "$P" -czf "$D/config-$ts.tar.gz" compose.yaml settings.env front config
# Notre branche « famille » (commits au-dessus de l'upstream figé), récupérable sans GitHub.
git -C /apps/sagora bundle create "$D/sagora.bundle" --all >/dev/null 2>&1 || true
find "$D" -maxdepth 1 -type f \( -name 'db-*.sqlite.zst' -o -name 'config-*.tar.gz' \) -mtime +14 -delete
echo "sauvegarde $ts : $(du -sh "$D/db-$ts.sqlite.zst" | cut -f1)"
