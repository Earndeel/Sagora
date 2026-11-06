# Historique de Sagora

Comment le projet est né et a évolué, jour par jour. Heures en UTC. Les demandes longues de Monsieur sont
reproduites telles quelles dans [cahiers-des-charges/](cahiers-des-charges/) ; les travaux de la première matinée
(avant AIOStreams) sont gardés dans [origines/](origines/). Les choix qui font règle sont résumés dans
[DECISIONS.md](DECISIONS.md).

Sources de cet historique : les sessions de travail enregistrées par W.Alter (Codex le 4 au matin, Claude Code
ensuite), les commits du dossier `code/`, les sauvegardes datées de `/user/Lucas/backups/changes/` et la mémoire
de W.Alter.

---

## Mardi 4 novembre 2026, matin : un Stremio familial (Codex)

| Heure | Ce qui s'est passé |
|---|---|
| 09:46 | Monsieur : « est-ce que l'on peut installer Stremio sur la VM de Walter ? Dans Apps ? » → serveur de streaming Stremio officiel installé dans `/apps/stremio` (VM ARM64, pas d'accélération matérielle pour le transcodage, ports privés). |
| 10:12 | [Cahier des charges « plateforme familiale »](cahiers-des-charges/2026-11-04-1012-plateforme-familiale.md) : notre propre Stremio Web, synchronisé avec les comptes Stremio officiels, base PostgreSQL de Walter. → Stremio Web officiel dans `/apps/stremio/web/`. |
| 10:28 | [Cahier des charges « accès Internet »](cahiers-des-charges/2026-11-04-1028-acces-internet.md) : accessible depuis Internet, sans tunnel SSH ni réglage pour la famille. → route HTTPS **stremio.walter-ai.cloud** par le tunnel Cloudflare (Monsieur accepte à 10:41 le redémarrage du tunnel partagé), base `stremio_app` isolée avec son propre rôle, sauvegarde quotidienne et restauration testée. |
| 10:50 | Monsieur confirme : connexion, bibliothèque et addons synchronisés sur son appareil. |
| 10:54-10:57 | Lecture : seules les sources TorBox marchent ; sur le Mac, « video is not supported » (Stremio Web officiel compris). Monsieur reporte ce point. |
| 10:57 | Fond de l'interface en noir, pour voir. |
| 11:24 | Monsieur veut ajouter [DX.BI](https://github.com/notdxbi/dxbi-stremio) (thème Netflix pour Stremio). |
| 11:34 | [Complément : multiprofils façon Netflix et lecture en un clic](cahiers-des-charges/2026-11-04-1134-multiprofils-et-lecture-en-un-clic.md). → [audit des architectures](origines/2026-11-04-audit-codex-architectures.md) (Stremio Web, Stremio Enhanced, DX.BI, AIOStreams…) et petite [démonstration de sélection de source](origines/stremio-selection-demo.py). Recommandation de Codex : garder Stremio Web et essayer AIOStreams à côté. |
| 12:06 | [Cahier des charges « une seule application »](cahiers-des-charges/2026-11-04-1206-une-seule-application.md) : une seule appli, une seule interface, sur stremio.walter-ai.cloud ; les projets étudiés ne servent que de références ou de services internes. |
| 12:20 | [QuickPlay réellement intégré](cahiers-des-charges/2026-11-04-1220-quickplay-reel.md) dans Stremio Web, branche `family/quickplay` (le travail est gardé en [patch](origines/2026-11-04-stremio-web-quickplay.patch)). Préproduction sur le port 18081, essais avec les vrais addons de Monsieur. |
| 13:03 | Monsieur : « c'est la version de Stremio classique pour moi, il n'y a pas de nouvelle interface ». |
| 13:25 | [Nouvelles priorités](cahiers-des-charges/2026-11-04-1325-priorite-nouvelle-interface.md) : une vraie expérience familiale inspirée de Netflix et DX.BI d'abord ; QuickPlay ne doit plus bloquer. |
| 13:59 | Fin de la session Codex : préproduction avec un nouvel accueil (grand bandeau, carrousels, fiches avec bouton Lecture) ; QuickPlay écrit et testé mais désactivé. |

## Mardi 4 novembre, après-midi : AIOStreams devient le socle (Claude Code)

| Heure | Ce qui s'est passé |
|---|---|
| 15:44 | « On reprend le développement de Stremio. » Constat : DX.BI est un plugin de ~15 600 lignes conçu pour Stremio Enhanced, pas pour notre Stremio Web ; il n'est pas réellement intégré. |
| 16:14 | [Cahier des charges « AIOStreams comme fondation »](cahiers-des-charges/2026-11-04-1614-aiostreams-comme-fondation.md) : **décision de Monsieur, AIOStreams devient le socle** (agrégateur de sources + application familiale complète : profils, lecteur, applis TV/desktop). Exploiter au maximum ce qu'il fait déjà, ne développer que le nécessaire. |
| 16:41 | Préproduction AIOStreams (port 18090) sur la révision `88b623da` du 4 novembre (la dernière version stable n'avait pas encore les aperçus de cartes). Notre version de l'interface commence : branche `famille`, premier commit = **teasers** (bandeau d'accueil, aperçus de cartes) et **couleurs du titre**. Configuration de départ : modèle officiel « Debrid Starter », TMDB en français, sources TorBox déjà en cache uniquement. |
| 16:51 | [Cahier des charges « finalisation et mise en production »](cahiers-des-charges/2026-11-04-1651-mise-en-production.md). |
| 17:13-17:28 | **Lecture en un clic** : lecture automatique de la première version, **repli** vers la suivante si elle échoue vraiment ; une bande-annonce refusée passe à la suivante. |
| 17:48 | Production prête dans `/apps/aiostreams/production`, en attente de la clé TorBox. |
| 17:52 | Monsieur : retirer l'ancien Stremio et utiliser son compte TorBox (clé rangée dans Bitwarden « AIOStreams · TorBox API »). |
| 18:09 | **En service sur https://stremio.walter-ai.cloud.** L'ancien Stremio est retiré (archive : `/user/Lucas/backups/changes/stremio-before-aiostreams-20261104-174430`). Essais réels : *Coco* en 1080p depuis TorBox, reprise à la bonne seconde, épisode suivant de *Mentalist*. Surveillance toutes les 5 min, sauvegarde quotidienne, test de restauration hebdomadaire. |
| 18:23-18:39 | « Pas de son, pas de choix du doublage, pas de sous-titres » : les navigateurs ne décodent pas le son Dolby (AC3/E-AC3) de la plupart des versions françaises. → **menu Langue** dans le lecteur (change de version au même endroit), sous-titres OpenSubtitles ; pour le son, appli de bureau ou VLC. |
| 18:54 | TorBox est réglé côté serveur : la famille n'a rien à configurer. |
| 19:03-19:25 | Appli officielle AIOStreams 0.13.0 sur le **dongle TV** du salon. Il a fallu mettre à jour son moteur web (WebView 74 → 159). Connexion par Quick Connect. |
| 19:28-20:45 | Le lanceur TV « Paysages » (fait par Codex le 26/10) ne montre que trois applis écrites dans son code : reconstruit depuis ses sources, **AIOStreams en première tuile** (version 1.4). |

## Mercredi 5 novembre : Sagora prend forme (Claude Code)

| Heure | Ce qui s'est passé |
|---|---|
| 08:35-09:00 | **Historique Stremio importé** dans le profil Lucas (l'export officiel était inutilisable ; données lues dans l'appli Stremio du Mac) : 182 films vus, 932 épisodes vus, 85 reprises, 38 favoris. |
| 09:13 | **Langue par profil** : la langue de l'interface du profil commande aussi titres, synopsis, catalogues et bandes-annonces (en-tête `X-AIOStreams-Language` + une variante de configuration par langue). |
| 10:01-10:22 | **Teasers** : HD (720p minimum), sans l'habillage YouTube (triangle lecture), aussi sur la fiche d'un titre, son qui monte progressivement, bouton « Bandes-annonces » = la même vidéo en plein écran, jamais la liste. |
| 10:35-10:50 | Bouton rond **« Versions »** à côté de « Bandes-annonces » ; plus de traits autour du bandeau d'accueil ; le « g » des grands titres n'est plus coupé. |
| 11:04 | **Le projet s'appelle Sagora**, avec le logo de Monsieur (S en pellicule) : nom, logo, icônes, vignette TV. |
| 11:37 | **TorrentClaw** (essai PRO de Monsieur) ajouté comme source. |
| 12:00-12:55 | **Usenet** : moteur Usenet intégré d'AIOStreams + serveur NNTP de l'essai TorrentClaw ; **Prowlarr** installé (index NZBIndex), avec une page à la Torrentio pour Monsieur : https://stremio.walter-ai.cloud/prowlarr, protégée par Cloudflare Access. Trackers **C411** et **TR4KER** ajoutés dans Prowlarr. |
| 13:2x | Koh-Lanta du 3/11 introuvable alors qu'il est sur les trackers : TMDB et les trackers ne numérotent pas pareil. → **relais Torznab** qui retrouve l'épisode par sa date de diffusion. Ling Long en VOSTFR (pack de saison C411) trouvé. |
| 13:22 | **Règle corrigée par Monsieur** : « en cache en priorité », pas « en cache uniquement ». Les versions à télécharger sont proposées après. **StremThru** auto-hébergé comme relais TorBox (les clés et passkeys ne sortent plus). Essai : TorBox Essential ne partage un torrent privé que 24 h (C411 demande 48 h ou un ratio de 1). |
| 13:49 | L'interface ne lance jamais seule une version qui doit encore être téléchargée. |
| 14:08 | **Profils et appareils** : Lucas en VO sous-titrée anglais ; Malika (mère de Monsieur) en VF sur une TV 4K HDR ; Zoé (sœur de Monsieur) sur iPad, debrid seulement ; Invité sans 4K. Dongle sans 4K ni HDR (règle « tv-salon »). |
| 15:00 | **Qualité selon le débit**, façon Netflix : si la connexion cale, passage à une version plus légère au même endroit, et l'appareil s'en souvient. |
| 15:27 | Monsieur : « laisse passer C411 et TR4KER même maintenant. Active les filtres. » → versions à télécharger de ces trackers ouvertes, filtres de titre et d'année activés. Dongle : la piste russe passait avant l'anglais → corrigé. |
| 15:46-16:51 | **Appli Android Sagora** (`cloud.walter.sagora`), pour avoir notre interface sur la TV : dépôt privé GitHub `Earndeel/sagora` (choix de Monsieur), construction GitHub Actions non signée, signature sur la VM (clé dans Bitwarden). Installée sur le dongle, profil Lucas, lanceur 1.6 (tuile Sagora). Correctifs : en-tête de langue autorisé pour l'appli (CORS), teasers par le lecteur YouTube intégré (0.13.0-sagora.2). |
| 18:22 | **Son des teasers activé par défaut** (0.13.0-sagora.3). |
| 18:55 | Les **cartes voisines glissent** au lieu d'être recouvertes par l'aperçu ; plus de **bandes noires** sur les bandes-annonces au format cinéma (0.13.0-sagora.4). |
| soir | Lire un seul épisode d'un pack de saison : TorBox télécharge toujours le torrent entier ; il faudrait notre propre moteur torrent. Monsieur : « on réglera ça plus tard ». |

## Jeudi 6 novembre : un seul dossier, un seul dépôt

Monsieur demande que Sagora soit documenté depuis le début et que tout soit sur son GitHub et dans `/apps/sagora` :

- `/apps/aiostreams` devient **`/apps/sagora`** (un lien garde l'ancien chemin), le code passe dans `code/` ;
- le dossier est le dépôt Git **`Earndeel/sagora`** : code (base AIOStreams + nos 19 commits, gardés un par un avec
  leurs dates), déploiement, scripts de la TV, cette documentation ; rien de secret ni de données de la famille ;
- services système renommés `sagora-health`, `sagora-backup`, `sagora-restore-test` ;
- l'ancien historique Git du code reste dans `/user/Lucas/backups/sagora/code-avant-depot-unique-20261106.bundle`.

Puis : « remplacer stremio.walter-ai.cloud par sagora.walter-ai.cloud ». **Sagora a sa propre adresse,
https://sagora.walter-ai.cloud** (DNS, tunnel, protection de /prowlarr, règle de cache, `BASE_URL`, appli Android pour
ses prochaines versions). L'ancienne adresse continue de servir la même chose : le dongle et les navigateurs déjà
connectés n'ont rien à refaire.

## Ouvert

- Lire un seul épisode dans un pack de saison (reporté par Monsieur).
- TorBox Standard : vérifier que le partage vers les trackers privés dure au moins 48 h (règle C411).
- Qualité selon le débit : à vérifier sur un vrai appareil.
- Règle d'appareil pour la TV de Malika quand son appli sera connectée.
