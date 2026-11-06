#!/usr/bin/env python3
"""Relais Torznab de Sagora, entre Sagora (AIOStreams) et le Prowlarr de la pile.

Pourquoi : TMDB, d'où Sagora tire ses fiches, ne numérote pas toujours les épisodes comme les trackers. Koh-Lanta :
TMDB découpe chaque émission en deux (l'émission du 3/11/2026 = S34E21 et S34E22), les trackers et TVDB disent S34E11.

Pour chaque index Prowlarr (/<id>/api) :
- t=caps : les séries se cherchent par identifiant IMDb seulement, pour que Sagora l'envoie toujours avec la saison et
  l'épisode TMDB (il l'a pour toutes les séries, contrairement à l'identifiant TVDB) ;
- t=tvsearch avec imdbid, saison et épisode : date de diffusion de l'épisode chez TMDB, puis numéro de l'épisode de
  cette date chez TVDB (Skyhook, le service gratuit de Sonarr). Si les numéros diffèrent, on cherche avec celui de TVDB
  (celui des trackers) et on remet dans les titres renvoyés le numéro TMDB attendu par Sagora, qui sinon les écarterait ;
- tout le reste (films, recherche par texte, packs de saison) passe tel quel.
Les clés (PROWLARR_API_KEY, TMDB_API_KEY) restent ici ; rien n'est renvoyé à Sagora.
"""
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROWLARR = os.environ.get("PROWLARR_URL", "http://aiostreams-prowlarr:9696/prowlarr").rstrip("/")
PROWLARR_KEY = os.environ["PROWLARR_API_KEY"]
TMDB_KEY = os.environ["TMDB_API_KEY"]
UA = "Sagora-torznab-relay/2"
TTL = 6 * 3600

_cache: dict[str, tuple[float, object]] = {}
_lock = threading.Lock()


def fetch_json(url: str, ttl: int = TTL):
    """GET JSON, gardé `ttl` secondes ; None si indisponible."""
    with _lock:
        hit = _cache.get(url)
        if hit and time.time() - hit[0] < ttl:
            return hit[1]
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=10) as r:
            data = json.load(r)
    except Exception:
        data = None
    with _lock:
        _cache[url] = (time.time(), data)
    return data


def tmdb(path: str):
    sep = "&" if "?" in path else "?"
    return fetch_json(f"https://api.themoviedb.org/3{path}{sep}api_key={TMDB_KEY}")


def tvdb_numbering(imdbid: str, season: int, episode: int) -> tuple[int, int] | None:
    """(saison, épisode) TVDB de l'épisode TMDB (season, episode), par sa date de diffusion ; None si inconnu."""
    imdb = imdbid if imdbid.startswith("tt") else "tt" + imdbid
    found = tmdb(f"/find/{imdb}?external_source=imdb_id") or {}
    shows = found.get("tv_results") or []
    if not shows:
        return None
    tmdb_id = shows[0]["id"]
    tvdb_id = (tmdb(f"/tv/{tmdb_id}/external_ids") or {}).get("tvdb_id")
    season_data = tmdb(f"/tv/{tmdb_id}/season/{season}") or {}
    air = next((e.get("air_date") for e in season_data.get("episodes", []) if e.get("episode_number") == episode), None)
    if not tvdb_id or not air:
        return None
    show = fetch_json(f"https://skyhook.sonarr.tv/v1/tvdb/shows/en/{tvdb_id}") or {}
    same_day = [e for e in show.get("episodes", []) if e.get("airDate") == air and e.get("seasonNumber")]
    if not same_day:
        return None
    # Le même jour, l'épisode TVDB de même saison d'abord, puis le premier.
    pick = next((e for e in same_day if e["seasonNumber"] == season), same_day[0])
    return pick["seasonNumber"], pick["episodeNumber"]


def renumber_titles(xml: bytes, frm: tuple[int, int], to: tuple[int, int]) -> bytes:
    """Dans les <title> renvoyés, S{frm}E{frm} devient S{to}E{to} (numérotation de Sagora)."""
    text = xml.decode("utf-8", "replace")
    pattern = re.compile(r"(?i)\bS0*%d([ ._-]?)E0*%d(?!\d)" % frm)

    def fix_title(m: re.Match) -> str:
        return m.group(1) + pattern.sub(lambda t: "S%02dE%02d" % to, m.group(2)) + m.group(3)

    return re.sub(r"(<title>)(.*?)(</title>)", fix_title, text, flags=re.S).encode()


def tv_caps_by_imdb(xml: bytes) -> bytes:
    """Dans les caps, la recherche de séries n'annonce plus que q, season, ep et imdbid."""
    text = xml.decode("utf-8", "replace")

    def fix(m: re.Match) -> str:
        tag = m.group(0)
        params = re.search(r'supportedParams="([^"]*)"', tag)
        if not params:
            return tag
        kept = [p for p in params.group(1).split(",") if p and p not in ("imdbid", "tmdbid", "tvdbid", "tvmazeid", "rid")]
        return tag.replace(params.group(0), 'supportedParams="%s"' % ",".join(kept + ["imdbid"]))

    return re.sub(r"<tv-search\b[^>]*>", fix, text).encode()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # une ligne courte par requête, sans les clés
        print("%s %s" % (self.command, re.sub(r"apikey=[^&]+", "apikey=…", self.path)[:200]), flush=True)

    def do_GET(self):
        if self.path in ("/health", "/ping"):
            return self.reply(200, b"ok", "text/plain")
        m = re.match(r"^/(\d+)/api(\?.*)?$", self.path)
        if not m:
            return self.reply(404, b"not found", "text/plain")
        indexer = m.group(1)
        query = dict(urllib.parse.parse_qsl((m.group(2) or "?")[1:], keep_blank_values=True))
        query["apikey"] = PROWLARR_KEY
        t = query.get("t", "")
        renumber = None
        if t == "tvsearch" and query.get("imdbid") and query.get("season", "").isdigit() and query.get("ep", "").isdigit():
            asked = (int(query["season"]), int(query["ep"]))
            tvdb = tvdb_numbering(query["imdbid"], *asked)
            if tvdb and tvdb != asked:
                query["season"], query["ep"] = str(tvdb[0]), str(tvdb[1])
                renumber = (tvdb, asked)
                print("  renuméroté S%02dE%02d → S%02dE%02d (date de diffusion)" % (asked + tvdb), flush=True)
        url = "%s/%s/api?%s" % (PROWLARR, indexer, urllib.parse.urlencode(query))
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                body, ctype, status = r.read(), r.headers.get("Content-Type", "application/xml"), r.status
        except urllib.error.HTTPError as e:
            body, ctype, status = e.read(), e.headers.get("Content-Type", "text/plain"), e.code
        except Exception as e:  # Prowlarr injoignable
            return self.reply(502, str(e).encode(), "text/plain")
        if status == 200 and t == "caps":
            body = tv_caps_by_imdb(body)
        elif status == 200 and renumber:
            body = renumber_titles(body, *renumber)
        self.reply(status, body, ctype)

    def reply(self, status, body, ctype):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 9797), Handler).serve_forever()
