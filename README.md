<p align="center"><img src="production/front/brand/sagora.svg" width="96" alt="Sagora"></p>

# Sagora

L'application de streaming de la famille de Monsieur : une seule appli, façon Netflix, avec des profils (Lucas,
Malika, Zoé, Invité), des bandes-annonces automatiques et une lecture en un clic qui choisit la meilleure version
pour la personne et l'appareil.

- **Adresse** : https://sagora.walter-ai.cloud (navigateur, appli Android/TV, appli de bureau) ; l'ancienne adresse
  https://stremio.walter-ai.cloud sert toujours la même chose pour les appareils déjà réglés.
- **En service depuis** le 4 novembre 2026 ; nommée Sagora le 5 novembre.
- **Socle** : [AIOStreams](https://github.com/Viren070/AIOStreams) (AGPL-3.0), avec notre propre interface et quelques
  services autour (TorBox par StremThru, Prowlarr pour C411/TR4KER et l'Usenet, relais de numérotation des épisodes).
- **Dossier** : `/apps/sagora` sur la VM w-alter = ce dépôt (`Earndeel/sagora`, privé).

## Où trouver quoi

| | |
|---|---|
| [docs/HISTORIQUE.md](docs/HISTORIQUE.md) | L'histoire du projet depuis la première demande, le 4 novembre 2026 à 09:46. |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Les décisions et règles de Monsieur, datées. |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Comment c'est construit : conteneurs, configuration, interface, appli Android, TV, sauvegardes, secrets. |
| [docs/EXPLOITATION.md](docs/EXPLOITATION.md) | Le guide de travail : réglages détaillés, déployer, mettre à jour, revenir en arrière, limites connues. |
| [docs/cahiers-des-charges/](docs/cahiers-des-charges/) | Les demandes de Monsieur, telles qu'il les a écrites. |
| [docs/origines/](docs/origines/) | Le premier Stremio familial (avant AIOStreams) : audit, QuickPlay, ancienne installation. |
| `code/` | AIOStreams + nos changements (interface web dans `code/packages/web`, appli Android dans `code/packages/android`). |
| `production/` | Ce qui tourne sur la VM : conteneurs, entrée nginx, relais, configuration de la famille, surveillance, sauvegardes, tests. |
| `tv/` | Le dongle TV du salon : lanceur d'accueil et scripts adb (exécutés depuis le Mac). |
| `.github/workflows/` | Construction de l'appli Android par GitHub Actions. |

## Ce qui n'est pas dans ce dépôt

Les secrets (dans Bitwarden uniquement, voir [ARCHITECTURE.md](docs/ARCHITECTURE.md#surveillance-sauvegardes-secrets)),
les données de la famille (`production/data/`, profils, historiques), les données de Prowlarr et StremThru, et les
fichiers construits (interface déployée, APK). Ils sont sauvegardés chaque nuit (`sagora-backup`), puis chiffrés hors
site par restic.

## Les gestes courants

| Pour… | Faire |
|---|---|
| Voir si tout va bien | `systemctl start sagora-health` puis `cat production/state/health.json` |
| Déployer l'interface web | [EXPLOITATION.md → Déployer l'interface web](docs/EXPLOITATION.md#déployer-linterface-web) |
| Publier l'appli Android | [EXPLOITATION.md → Appli Android Sagora](docs/EXPLOITATION.md#appli-android-sagora) |
| Mettre à jour AIOStreams | [EXPLOITATION.md → Mettre à jour AIOStreams](docs/EXPLOITATION.md#mettre-à-jour-aiostreams) |
| Revenir en arrière | [EXPLOITATION.md → Retour arrière](docs/EXPLOITATION.md#retour-arrière) |

Chaque changement est commité ici avec un message clair, et une nouvelle décision de Monsieur va dans
[DECISIONS.md](docs/DECISIONS.md) et [HISTORIQUE.md](docs/HISTORIQUE.md).
