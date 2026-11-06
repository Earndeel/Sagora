#!/usr/bin/env python3
"""Crée ou met à jour la configuration « Famille » de la préproduction AIOStreams.

Modèle officiel Debrid Starter + famille.json ; secrets lus dans Bitwarden (jamais affichés).
L'identifiant de la configuration est gardé dans ../data/famille-uuid (le mot de passe reste dans Bitwarden).
"""
import base64, copy, http.cookiejar, json, os, subprocess, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("AIOSTREAMS_URL", "http://127.0.0.1:18090")
TEMPLATE = "/apps/sagora/code/resources/templates/debrid-starter.json"
PROFILE = os.environ.get("AIOSTREAMS_PROFILE", "famille")
UUID_FILE = os.path.join(HERE, "..", "data", f"{PROFILE}-uuid")
ADMIN_ITEM = "60fd7166-82ec-48e6-ac6d-6e6c25fd7805"
CONFIG_ITEM = os.environ.get("CONFIG_ITEM", "AIOStreams préproduction · configuration Famille")
TORBOX_ITEM = os.environ.get("TORBOX_ITEM", "AIOStreams · TorBox API")


def secret(item, field="password", required=True):
    r = subprocess.run(["walter-secret", "get", item, field], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        if required:
            sys.exit(f"secret manquant : {item}")
        return None
    return r.stdout.strip()


jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def api(method, path, body=None, basic=None):
    headers = {"Content-Type": "application/json"}
    if basic:
        headers["Authorization"] = "Basic " + base64.b64encode(":".join(basic).encode()).decode()
    req = urllib.request.Request(BASE + "/api/v1" + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers=headers)
    try:
        with opener.open(req, timeout=60) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.load(e)
        except Exception:
            return e.code, {}


def build_config():
    tpl = json.load(open(TEMPLATE))["config"]
    fam = json.load(open(os.path.join(HERE, f"{PROFILE}.json")))
    cfg = copy.deepcopy(tpl)
    cfg.pop("tmdbApiKey", None)  # valeur factice du modèle
    cfg["addonName"] = fam["addonName"]
    cfg["presets"] = fam["extraPresets"] + cfg["presets"]
    cfg.update({k: v for k, v in fam["overrides"].items() if not k.startswith("_")})
    tmdb = secret("AIOStreams · TMDB", required=False)
    if tmdb:
        cfg["tmdbApiKey"] = tmdb
        for k in ("titleMatching", "yearMatching", "digitalReleaseFilter"):
            cfg[k] = tpl.get(k, {"enabled": True})
    torbox = secret(TORBOX_ITEM, required=False)
    cfg["services"] = [{"id": "torbox", "enabled": True, "credentials": {"apiKey": torbox}}] if torbox else []
    if fam.get("onlyExtraPresets"):
        cfg["presets"] = fam["extraPresets"]
    elif not torbox:  # sans service debrid, les addons de flux du modèle sont refusés : catalogues seuls
        cfg["presets"] = fam["extraPresets"]
    return cfg, bool(torbox)


def main():
    st, _ = api("POST", "/auth/login", {"username": "walter", "password": secret(ADMIN_ITEM)})
    if st != 200:
        sys.exit(f"connexion admin refusée ({st})")
    cfg, has_torbox = build_config()
    password = secret(CONFIG_ITEM)
    uuid = open(UUID_FILE).read().strip() if os.path.exists(UUID_FILE) else None
    if uuid:
        # Remplace toute la configuration : les changements faits depuis la page de configuration seraient perdus.
        st, res = api("PUT", "/user", {"config": cfg}, basic=(uuid, password))
    else:
        st, res = api("POST", "/user", {"password": password, "config": cfg})
        if st == 201:
            uuid = res["data"]["uuid"]
            with open(UUID_FILE, "w") as f:
                f.write(uuid + "\n")
    ok = st in (200, 201)
    print(json.dumps({"ok": ok, "status": st, "uuid": uuid, "torbox": has_torbox,
                      "error": None if ok else (res.get("error") or res.get("detail"))}, ensure_ascii=False)[:2000])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
