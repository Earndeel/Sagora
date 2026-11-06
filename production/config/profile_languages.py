#!/usr/bin/env python3
"""Préférences de langue de chaque profil (mêmes réglages que l'app : Réglages → Audio / Sous-titres).
Lucas : VO, sous-titres anglais toujours (2026-11-05). Malika, Zoé, Invité : VF d'abord, sous-titres français quand le
son n'est pas en français."""
import json, subprocess, sys, urllib.request
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18085") + "/jellyfin"
UA = "Mozilla/5.0 Chrome/130"
uuid = open("/apps/sagora/production/data/famille-uuid").read().strip()
pw = subprocess.run(["walter-secret", "get", "AIOStreams préproduction · configuration Famille", "password"], capture_output=True, text=True).stdout.strip()
def call(m, p, b=None, tok=None):
    A = 'MediaBrowser Client="walter-config", Device="vm", DeviceId="profile-languages", Version="1"' + (f', Token="{tok}"' if tok else "")
    r = urllib.request.Request(BASE + p, method=m, data=json.dumps(b).encode() if b is not None else None, headers={"Content-Type": "application/json", "User-Agent": UA, "Authorization": A})
    with urllib.request.urlopen(r, timeout=60) as f:
        raw = f.read(); return json.loads(raw) if raw else None
# PlayDefaultAudioTrack=False : la langue choisie passe avant la piste par défaut du fichier (sinon une sortie
# russe MULTi démarre en russe). VF : sans piste française, la langue originale puis l'anglais (2026-11-05).
VF = {"AudioLanguagePreference": "fre", "AudioLanguages": ["fre", "OriginalLanguage", "eng"], "SubtitleLanguagePreference": "fre", "PlayDefaultAudioTrack": False,
      "SubtitleLanguages": ["fre", "eng"], "SubtitleMode": "Smart", "ListPreferredSubtitlesOnly": True}
VO = {"AudioLanguagePreference": "OriginalLanguage", "AudioLanguages": ["OriginalLanguage", "fre"], "SubtitleLanguagePreference": "fre", "PlayDefaultAudioTrack": False,
      "SubtitleLanguages": ["fre", "eng"], "SubtitleMode": "Always", "ListPreferredSubtitlesOnly": True}
VO_EN = {"AudioLanguagePreference": "OriginalLanguage", "AudioLanguages": ["OriginalLanguage", "eng", "fre"], "SubtitleLanguagePreference": "eng", "PlayDefaultAudioTrack": False,
         "SubtitleLanguages": ["eng", "fre"], "SubtitleMode": "Always", "ListPreferredSubtitlesOnly": True}
PREFS = {"Lucas": VO_EN}
a = call("POST", "/Users/AuthenticateByName", {"Username": uuid, "Pw": pw}); tok = a["AccessToken"]
for u in call("GET", "/AIOStreams/Users", tok=tok):
    name, uid = u["user"]["Name"], u["user"]["Id"]
    t = call("POST", "/AIOStreams/Token", {"UserId": uid}, tok=tok)["AccessToken"]
    me = call("GET", "/Users/Me", tok=t)
    conf = {**(me.get("Configuration") or {}), **PREFS.get(name, VF)}
    call("POST", f"/Users/Configuration?userId={me['Id']}", conf, tok=t)
    back = call("GET", "/Users/Me", tok=t)["Configuration"]
    print(f"{name:16} audio={back.get('AudioLanguages')} sous-titres={back.get('SubtitleLanguages')} mode={back.get('SubtitleMode')} piste-du-fichier={back.get('PlayDefaultAudioTrack')}")

# Langue de l'interface (réglage « Langue de l'application » de l'app, synchronisé par profil) : français partout,
# sinon l'app suit la langue de l'appareil (anglais sur le dongle TV).
PREFS = "aiostreams-web"
SAVED = "saved"
for u in call("GET", "/AIOStreams/Users", tok=tok):
    name, uid = u["user"]["Name"], u["user"]["Id"]
    t = call("POST", "/AIOStreams/Token", {"UserId": uid}, tok=tok)["AccessToken"]
    me = call("GET", "/Users/Me", tok=t)["Id"]
    cur = call("GET", f"/DisplayPreferences/{PREFS}?client={PREFS}&userId={me}", tok=t) or {}
    # Français seulement si le profil n'a pas déjà choisi sa langue (Lucas : anglais, 2026-11-05).
    if (cur.get("CustomPrefs") or {}).get("language"):
        print(f"{name:16} interface = {(cur.get('CustomPrefs') or {}).get('language')} (inchangée)")
        continue
    custom = {**(cur.get("CustomPrefs") or {}), "language": "fr", SAVED: "1"}
    call("POST", f"/DisplayPreferences/{PREFS}?client={PREFS}&userId={me}", {**cur, "Id": PREFS, "Client": PREFS, "CustomPrefs": custom}, tok=t)
    print(f"{name:16} interface =", (call("GET", f"/DisplayPreferences/{PREFS}?client={PREFS}&userId={me}", tok=t).get("CustomPrefs") or {}).get("language"))
