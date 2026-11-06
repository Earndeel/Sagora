#!/usr/bin/env python3
"""Surveillance de l'application familiale (toutes les 5 min, aiostreams-health.timer).
Vérifie AIOStreams, l'entrée nginx et l'adresse publique ; relance les conteneurs s'ils sont arrêtés ;
prévient Monsieur sur Telegram seulement si la panne dure (3 contrôles) malgré la relance, puis au rétablissement."""
import json, os, re, subprocess, time, urllib.request
from pathlib import Path

P = Path("/apps/sagora/production")
STATE = P / "state" / "health.json"
CHECKS = {
    "aiostreams": "http://127.0.0.1:18090/api/v1/health",
    "entrée": "http://127.0.0.1:18085/jellyfin/web/",
    "prowlarr (index Usenet)": "http://127.0.0.1:19696/prowlarr/ping",
    "stremthru (relais TorBox)": "http://127.0.0.1:18095/v0/health",
    "public": "https://sagora.walter-ai.cloud/api/v1/health",
}


def ok(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "walter-health"}), timeout=20) as r:
            return r.status == 200
    except Exception:
        return False


def telegram(text):
    tok = subprocess.run(["walter-secret", "grant", "access", "telegram-bot"], capture_output=True, text=True, timeout=60)
    token = tok.stdout.strip()
    m = re.search(r"^TELEGRAM_HOME_CHANNEL:\s*'?(-?\d+)'?\s*$", (Path.home() / ".hermes" / "config.yaml").read_text(), re.M)
    if tok.returncode or not token or not m:
        return False
    try:
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",
                                     data=json.dumps({"chat_id": m.group(1), "text": text}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read()).get("ok", False)
    except Exception:  # jamais le jeton dans une erreur
        return False


# L'adresse publique n'est surveillée qu'une fois le domaine basculé (switch-domain.sh crée ce marqueur).
if not (P / "state" / "public-live").exists():
    CHECKS.pop("public")
state = json.loads(STATE.read_text()) if STATE.exists() else {"failures": 0, "notified": False}
result = {name: ok(url) for name, url in CHECKS.items()}
healed = False
if not (result["aiostreams"] and result["entrée"]):
    subprocess.run(["docker", "compose", "up", "-d"], cwd=P, capture_output=True, timeout=180)
    healed = True
    time.sleep(45)
    result = {name: ok(url) for name, url in CHECKS.items()}
down = [n for n, good in result.items() if not good]
if down:
    state["failures"] += 1
    if state["failures"] >= 3 and not state["notified"]:
        state["notified"] = telegram(
            "Sagora (sagora.walter-ai.cloud) en panne depuis environ 15 min : "
            + ", ".join(down) + " ne répond pas, la relance automatique n'a pas suffi. Détails : /apps/sagora/README.md.")
else:
    if state.get("notified"):
        telegram("Sagora (sagora.walter-ai.cloud) fonctionne de nouveau.")
    state = {"failures": 0, "notified": False}
state.update(last=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), result=result, healed=healed)
STATE.write_text(json.dumps(state, ensure_ascii=False))
print(json.dumps(state, ensure_ascii=False))
