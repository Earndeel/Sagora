# Architecture de Sagora

Sagora = **AIOStreams** (agrégateur de sources + serveur compatible Jellyfin + applis) avec **notre interface web**
(dossier `code/`, nos commits par-dessus AIOStreams) et quelques services autour. Tout tourne sur la VM w-alter
(Oracle, ARM64) dans Docker ; les vidéos ne passent pas par la VM, sauf l'Usenet.

## Vue d'ensemble

```
 Appareils de la famille                      VM w-alter (Docker, pile « aiostreams »)
 ─────────────────────                        ─────────────────────────────────────────────────────────
 navigateur, appli Android/TV,  ──HTTPS──▶ tunnel Cloudflare ──▶ aiostreams-front (nginx, :18085)
 appli de bureau                 sagora.walter-ai.cloud               │  /             → notre interface (connexion Lucas)
                                                                      │  /logo.png…    → front/brand/ (logo Sagora)
                                                                      │  /sagora-app/  → mises à jour de l'appli Android
                                                                      │  /prowlarr     → Prowlarr (Cloudflare Access)
                                                                      ▼
                                                     aiostreams (:18090) ── interface web = production/web-dist/
                                                       │  profils, historique, configuration « Famille »
                                                       │  sources : Torrentio, Comet, MediaFusion, Knaben, TorrentClaw…
                                                       ├──▶ aiostreams-stremthru (:18095) ──▶ API TorBox
                                                       ├──▶ aiostreams-torznab-relay ──▶ aiostreams-prowlarr (:19696)
                                                       │                                   ├─ C411, TR4KER (trackers)
                                                       │                                   └─ NZBIndex (Usenet)
                                                       └──▶ TMDB (fiches), OpenSubtitles (sous-titres)

 Lecture : l'appareil lit directement le lien TorBox (CDN TorBox). Usenet : la vidéo passe par la VM.
 Teasers : l'appareil lit YouTube directement.
```

## Les conteneurs (`production/compose.yaml`, projet Docker `aiostreams`)

Les conteneurs gardent leur nom technique `aiostreams-*` : la configuration de la famille les appelle par ce nom.

| Conteneur | Port (VM) | Rôle |
|---|---|---|
| `aiostreams` | 127.0.0.1:18090 | AIOStreams, image officielle `2026.11.04.1410-nightly` (commit `88b623da`) figée par empreinte ; notre interface remplace la sienne (`web-dist/` monté en lecture seule). Base SQLite dans `data/`. 1 Go, 1,5 cœur. |
| `aiostreams-front` | 127.0.0.1:18085 | nginx d'entrée, seule cible du tunnel Cloudflare. Ajoute l'en-tête `X-AIOStreams-Language` à la liste CORS du serveur (sinon l'appli Android ne peut pas se connecter). |
| `aiostreams-stremthru` | 127.0.0.1:18095 | Notre **StremThru** : relais vers TorBox (la clé TorBox et les passkeys ne sortent pas), lit les .torrent privés dans Prowlarr. Fonction `torz` obligatoire. |
| `aiostreams-torznab-relay` | interne | `torznab-relay/relay.py` : relaie les recherches Torznab vers Prowlarr et **renumérote les épisodes** (TMDB ↔ trackers) par date de diffusion (TMDB → TVDB/Skyhook). |
| `aiostreams-prowlarr` | 127.0.0.1:19696 et Tailscale | Index de trackers et Usenet ; page pour Monsieur : https://sagora.walter-ai.cloud/prowlarr (Cloudflare Access « Sagora Prowlarr » puis compte Prowlarr). |

## La configuration « Famille »

Une configuration AIOStreams (identifiant dans `production/data/famille-uuid`, mot de passe dans Bitwarden), lue et
écrite par l'API `/api/v1/user` (un `PUT` remplace tout). Points clés (détail : [EXPLOITATION.md](EXPLOITATION.md)) :

- **Sources** : Torrentio, Comet, MediaFusion, Knaben, TorrentClaw, C411 et TR4KER (par le relais), Prowlarr (Usenet).
- **Service** : TorBox. **Tri** : en cache, type de flux, langue, résolution, sous-titres, puis HDR, audio, codec, taille.
  Les versions à télécharger viennent après celles en cache (`excludeUncached=false`, `cacheAndPlay`).
- **Filtres** : titre et année ; saison/épisode pour toutes les sources sauf C411/TR4KER (déjà renumérotées par le relais).
- **Variantes** (règles conditionnelles, scripts CEL) : `langue-*` (une par langue d'interface, selon l'en-tête
  `X-AIOStreams-Language`), `vo-en` (Lucas), `sans-4k` (Invité), `navigateur` (formats lisibles par un navigateur),
  `tv-salon` (dongle : ni 4K, ni HDR, ni REMUX).
- **Profils** (« personas ») : Lucas (principal), Malika, Zoé, Invité. Pistes audio et sous-titres par défaut :
  `production/config/profile_languages.py`.

## Notre interface (`code/packages/web`)

Construite par `pnpm build` et déployée dans `production/web-dist/`. Ce qu'elle ajoute à AIOStreams :
teasers (bandeau, aperçus de cartes, fiches) en HD avec son progressif, couleurs du titre, lecture en un clic avec
repli, menu Langue du lecteur, langue des fiches par profil, bouton Versions, qualité selon le débit, cartes voisines
qui glissent, nom et logo Sagora. Liste complète, commit par commit : `git log --oneline -- code/` depuis le commit
« AIOStreams 88b623da as Sagora's base ».

## Appli Android Sagora (`cloud.walter.sagora`)

La même interface, embarquée dans l'appli Android d'AIOStreams (`code/packages/android`), à côté de l'appli
officielle. Chaîne : GitHub Actions construit des APK non signés (`.github/workflows/sagora-android.yml`) → la VM
les signe avec la clé de Sagora (Bitwarden) et les publie sous `/sagora-app/android/` (`production/android-app/publish.sh`)
→ l'appli installée s'y met à jour. Sur le dongle, installation par adb depuis le Mac (`tv/`).

## Dongle TV du salon

Android 12, 1080p (960×540 en pixels CSS), 1 Go de RAM, adb sur le réseau de la maison (192.168.1.38, piloté depuis le
Mac). Moteur web mis à jour (WebView 159). Lanceur d'accueil « Paysages » (`tv/launcher/`, version 1.6-sagora) avec
Sagora en première tuile.

## Surveillance, sauvegardes, secrets

- `sagora-health.timer` (5 min) : `production/health.py` vérifie l'app, l'entrée, Prowlarr, StremThru et l'adresse
  publique, relance la pile, alerte Telegram si une panne dure 15 min.
- `sagora-backup.timer` (04:45 UTC) : `production/backup.sh` → `/user/Lucas/backups/aiostreams/` (base SQLite,
  configuration, dépôt Git en bundle), 14 jours ; restic l'emporte chiffré hors site à 05:10.
- `sagora-restore-test.timer` (dimanche 05:30 UTC) : restauration de la dernière sauvegarde dans une instance jetable.
- **Secrets** : uniquement dans Bitwarden, jamais dans ce dépôt. `production/render-secrets.sh` écrit les fichiers
  0600 ignorés par Git (`secrets.env`, `torznab-relay/relay.env`). Éléments Bitwarden : « AIOStreams · TorBox API »,
  « AIOStreams · TMDB », « AIOStreams · TorrentClaw API », « AIOStreams · TorrentClaw Usenet (NNTP) »,
  « AIOStreams préproduction · SECRET_KEY », « AIOStreams préproduction · admin », « AIOStreams préproduction ·
  configuration Famille », « Sagora · Prowlarr admin », « Sagora · Prowlarr API », « Sagora · compte de service
  Usenet », « Sagora · C411 API », « Sagora · TR4KER API », « Sagora · Android signature (mot de passe) »,
  « Sagora · Android signature (keystore base64) », « Sagora · lanceur TV (clé de signature) ».

## Licences

AIOStreams est sous **AGPL-3.0** : `code/` garde sa licence et ses crédits (page « À propos »). Notre version reste
privée (usage familial). Le lanceur TV vient d'un travail de Codex (2026-10-26).
