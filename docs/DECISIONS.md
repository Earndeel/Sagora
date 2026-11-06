# Décisions et règles de Monsieur

Ce qui fait règle pour Sagora, avec sa date. Une décision plus récente remplace l'ancienne (indiqué). À compléter
à chaque nouvelle décision. Le récit complet est dans [HISTORIQUE.md](HISTORIQUE.md).

## Produit

| Date | Décision |
|---|---|
| 2026-11-04 | Une **seule application et une seule interface** pour la famille, sur https://stremio.walter-ai.cloud. Les projets étudiés servent de références ou de services internes, jamais d'applis séparées visibles. |
| 2026-11-04 | **AIOStreams est le socle** (décision architecturale, 16:14). Exploiter au maximum ce qu'il fait ; ne développer que ce qui manque ; ne pas recréer une fonction qui marche déjà. |
| 2026-11-04 | L'ancien Stremio est retiré (« enlève l'ancien »). |
| 2026-11-04 | Expérience inspirée de Netflix et DX.BI : grand bandeau avec bande-annonce, carrousels, cartes qui s'agrandissent, fiches riches, utilisable au Mac, à l'iPad et à la télécommande. De vraies interactions, pas seulement des couleurs. |
| 2026-11-04 | Trois façons de choisir une source : automatique par défaut, choix de la qualité seulement, mode expert avec la liste complète. La liste manuelle des versions reste toujours accessible. |
| 2026-11-04 | Le repli vers une autre version ne réagit qu'aux vraies erreurs du lecteur, pas à un simple chargement. |
| 2026-11-04 | Pas de dépendance payante obligatoire sans alternative gratuite présentée. IA éventuelle : Walter Router, sans modèle fixe. |
| 2026-11-05 | Le projet s'appelle **Sagora**, avec le logo de Monsieur, partout où c'est possible. |
| 2026-11-05 | L'appli Android Sagora est construite par un **dépôt GitHub privé** (`Earndeel/sagora`). |
| 2026-11-06 | **Tout Sagora est dans `/apps/sagora`, qui est aussi le dépôt GitHub `Earndeel/sagora`**, documenté depuis le début. |
| 2026-11-06 | **L'adresse devient https://sagora.walter-ai.cloud** (« remplacer stremio.walter-ai.cloud par sagora.walter-ai.cloud »). L'ancienne adresse reste servie pour les appareils déjà réglés. |

## Sources, TorBox et trackers

| Date | Décision |
|---|---|
| 2026-11-04 | Ne jamais falsifier le ratio d'un tracker privé. |
| 2026-11-04 | TorBox : ne jamais régénérer la clé sans l'accord de Monsieur ; ne jamais montrer identifiants, clés ou jetons (conversations, journaux, modèles). |
| 2026-11-04 | Trackers privés : pas de téléchargement automatique sans avoir vérifié leurs règles de partage et de ratio. |
| ~~2026-11-04~~ | ~~TorBox : versions déjà en cache uniquement~~ → remplacé le 2026-11-05. |
| 2026-11-05 | **En cache en priorité, pas uniquement** : les versions en cache TorBox passent d'abord ; celles à télécharger sont proposées ensuite et téléchargées quand on les choisit. L'interface ne lance jamais seule une version à télécharger. |
| 2026-11-05 | **C411 et TR4KER ouverts même pour les versions à télécharger**, sans attendre TorBox Standard (« laisse passer même maintenant »). Ratios à garder « toujours nickel » sur C411 (48 h de partage ou ratio 1). |
| 2026-11-05 | Filtres de titre et d'année activés. |
| 2026-11-05 | Lire un seul épisode d'un pack de saison : **reporté** (« on réglera ça plus tard »). TorBox télécharge toujours le pack entier. |

## Profils, langues et appareils

| Date | Décision |
|---|---|
| 2026-11-04 | Classement des sources : langues, sous-titres, résolution, HDR / Dolby Vision, codec, débit, taille, disponibilité. |
| 2026-11-05 | La langue de l'interface d'un profil vaut aussi pour titres, synopsis et bandes-annonces, **séparément pour chaque profil**. |
| 2026-11-05 | **Lucas** (Monsieur) : VO sous-titrée en anglais, interface en anglais. **Malika** (sa mère) : VF, TV 4K HDR. **Zoé** (sa sœur) : iPad, lecture par le debrid uniquement. **Invité** : sans 4K. |
| 2026-11-05 | Le **dongle TV** ne lit ni la 4K ni le HDR ; le Mac, si. Lecture : charger le meilleur choix pour la personne et l'appareil, et changer de qualité selon le débit comme Netflix. |

## Bandes-annonces (teasers)

| Date | Décision |
|---|---|
| 2026-11-05 | Démarrage automatique aussi sur la fiche d'un titre ; 720p minimum, 1080p idéalement ; jamais le triangle de lecture de YouTube. |
| 2026-11-05 | Le son arrive progressivement, jamais à l'arrivée sur la page. Le bouton « Bandes-annonces » ouvre la vidéo en plein écran sans coupure, jamais la liste. |
| 2026-11-05 | **Son activé par défaut** sur les teasers automatiques (montée progressive conservée). |
| 2026-11-05 | Une carte qui s'agrandit pousse ses voisines sur le côté au lieu de les recouvrir ; pas de traits ni de bandes autour des vidéos. |
