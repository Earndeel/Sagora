> Texte de Monsieur, donné dans Codex (session du matin) le 4 novembre 2026 à 11:34 UTC. Reproduit tel quel ; la suite du projet est racontée dans [../HISTORIQUE.md](../HISTORIQUE.md).

Complément à notre projet Stremio familial.

Je veux ajouter deux objectifs structurants :

1. Une expérience multiprofils comparable à Netflix.
2. Une lecture véritablement en un clic, avec sélection automatique et intelligente de la meilleure source vidéo.

Avant de développer ces fonctions, réalise un audit technique des projets existants :

- [https://github.com/REVENGE977/stremio-enhanced](https://github.com/REVENGE977/stremio-enhanced)
- [https://github.com/Viren070/AIOStreams](https://github.com/Viren070/AIOStreams)
- [https://github.com/notdxbi/dxbi-stremio](https://github.com/notdxbi/dxbi-stremio)
- Notre Stremio Web officiel déjà déployé dans `/apps/stremio/`.

### A. Profils familiaux

Étudie en priorité la prise en charge native des profils Stremio Supporters, déjà proposée sur Web et Android TV.

Évalue également une alternative avec comptes Stremio gratuits distincts et une couche de profils personnalisée.

Objectifs :

- Sélection simple des profils au lancement.
- Historique et progression indépendants.
- Bibliothèques et recommandations individuelles.
- Préférences audio VF/VOSTFR, sous-titres et qualité.
- Préférences adaptées à chaque appareil.
- Profils enfants avec restrictions.
- Synchronisation entre les différents appareils.
- Configuration facile par un administrateur familial.

Ne recrée pas une fonctionnalité déjà correctement prise en charge par Stremio.

N'intègre pas de dépendance payante obligatoire sans me présenter l'alternative gratuite.

### B. Moteur intelligent de sélection des sources

Audite précisément AIOStreams : architecture, filtres, règles de classement, déduplication, profils, système d'autoplay et compatibilité avec Stremio Web.

Je veux que le bouton Lecture déclenche automatiquement :

1. La récupération des sources fournies par les addons configurés.
2. La vérification du film ou de l'épisode exact.
3. L'élimination des sources incompatibles.
4. Le classement suivant les préférences du profil et les capacités de l'appareil.
5. Le choix de la meilleure source.
6. Le démarrage immédiat du lecteur approprié.
7. Le basculement vers une autre source compatible si la première échoue, sans boucle infinie.

Critères de classement : langue audio, sous-titres, résolution, HDR/Dolby Vision, codec, débit, taille, disponibilité, fiabilité, cache éventuel et préférences utilisateur.

La meilleure source n'est pas nécessairement celle qui possède la résolution maximale.

Prévoir trois modes :

- Automatique, par défaut.
- Choix de la qualité uniquement.
- Expert, avec liste complète des sources.

Les choix manuels peuvent améliorer les futures préférences, sans compromettre les contraintes strictes.

### C. Sécurité des trackers privés

Aucun téléchargement automatique sur un tracker privé sans validation des règles de partage et de ratio.

Une source privée doit être exclue si les informations nécessaires sont absentes ou si sa sélection risque de compromettre le compte.

Ne jamais falsifier le ratio, contourner les règles ou exposer des passkeys.

Respecter les politiques de sortie réseau existantes. Ne pas relayer les vidéos par le tunnel Cloudflare.

### D. Architecture

Compare objectivement trois stratégies :

1. Conserver notre Stremio Web et intégrer un système d'extensions inspiré de Stremio Enhanced, avec AIOStreams comme addon d'agrégation.
2. Réutiliser davantage de composants AIOStreams, notamment son moteur de sélection et son interface.
3. Utiliser directement l'application AIOStreams comme fondation, si cela satisfait mieux nos objectifs multiplateformes.

Analyse la compatibilité des licences, notamment GPL-2.0, MIT et AGPL-3.0, les ressources ARM64, le fonctionnement sur iPad avec lecteur externe, Android TV et la synchronisation Stremio.

Privilégie une architecture modulaire et maintenable.

La base PostgreSQL existante doit être mutualisée avec isolation logique si un backend applicatif est nécessaire.

### E. Exécution

Termine d'abord la mise en service Stremio actuellement en cours.

Puis réalise l'audit comparatif et propose une décision architecturale argumentée.

N'effectue pas de migration ou remplacement irréversible du frontend actuel.

Si une solution peut être testée sans risque, prépare un prototype isolé, avec fonctionnalités activables et désactivables.

Je veux surtout savoir quelle solution nous permet d'atteindre le plus rapidement et proprement l'expérience suivante :

**L'utilisateur ouvre l'application, choisit son profil, clique sur un film ou un épisode, et la lecture démarre directement dans sa langue et dans la meilleure qualité compatible.**

Les menus de sélection des sources doivent rester accessibles, mais ne plus être une étape obligatoire.
