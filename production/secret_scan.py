"""Contrôle avant tout envoi sur GitHub. Cherche les vraies valeurs des secrets de Sagora (lues dans Bitwarden, jamais affichées) dans des fichiers
ou dans tout l'historique Git. Usage : secret_scan.py files <fichiers…> | secret_scan.py history <dépôt>"""
import subprocess, sys
ITEMS = [("AIOStreams · TorBox API", "password"), ("AIOStreams · TMDB", "password"), ("AIOStreams · TorrentClaw API", "password"),
         ("AIOStreams · TorrentClaw Usenet (NNTP)", "password"), ("AIOStreams préproduction · SECRET_KEY", "password"),
         ("AIOStreams préproduction · admin", "password"), ("AIOStreams préproduction · configuration Famille", "password"),
         ("Sagora · Prowlarr admin", "password"), ("Sagora · Prowlarr API", "password"), ("Sagora · compte de service Usenet", "password"),
         ("Sagora · C411 API", "password"), ("Sagora · TR4KER API", "password"), ("Sagora · Android signature (mot de passe)", "password"),
         ("Sagora · Android signature (keystore base64)", "notes"), ("Sagora · lanceur TV (clé de signature)", "password")]
values = {}
for name, field in ITEMS:
    r = subprocess.run(["walter-secret", "get", name, field], capture_output=True, text=True)
    v = r.stdout.strip()
    if len(v) >= 8:
        values[name] = v[:200]  # assez pour reconnaître une clé ou le début d'un keystore
    else:
        print("non lu ou trop court :", name)
uuid = open("/apps/sagora/production/data/famille-uuid").read().strip()
values["identifiant de la configuration Famille (famille-uuid)"] = uuid
print(len(values), "valeurs chargées")
found = set()
if sys.argv[1] == "files":
    for f in sys.argv[2:]:
        try:
            data = open(f, "rb").read().decode("utf-8", "replace")
        except (IsADirectoryError, FileNotFoundError):
            continue
        for name, v in values.items():
            if v in data:
                found.add((name, f))
else:
    repo = sys.argv[2]
    revs = subprocess.run(["git", "-C", repo, "rev-list", "--all"], capture_output=True, text=True).stdout.split()
    for name, v in values.items():
        r = subprocess.run(["git", "-C", repo, "grep", "-l", "-F", "-e", v] + revs, capture_output=True, text=True)
        for line in r.stdout.splitlines():
            found.add((name, line.split(":", 1)[1] if ":" in line else line))
        log = subprocess.run(["git", "-C", repo, "log", "--all", "--format=%B"], capture_output=True, text=True).stdout
        if v in log:
            found.add((name, "messages de commit"))
for name, where in sorted(found):
    print("TROUVÉ :", name, "dans", where)
print("aucun secret trouvé" if not found else f"{len(found)} occurrence(s)")
