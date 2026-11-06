> Texte de Monsieur, donné dans Codex (session du matin) le 4 novembre 2026 à 12:06 UTC. Reproduit tel quel ; la suite du projet est racontée dans [../HISTORIQUE.md](../HISTORIQUE.md).

Nous poursuivons la construction de notre Stremio familial personnalisé.

Je veux une **seule application et une seule interface utilisateur**, actuellement accessible sur https://stremio.walter-ai.cloud/.

Les projets open source étudiés doivent servir de références techniques, de composants compatibles ou de services internes. Ils ne doivent pas devenir des applications séparées visibles par la famille.

L'objectif final est une expérience de streaming aussi fluide que Netflix, avec une interface cinématographique, plusieurs profils, des recommandations personnalisées et une lecture automatique intelligente.

Tu disposes déjà de l'audit précédent. Ne recommence pas une étude générale : vérifie uniquement les points techniques nécessaires à l'intégration, puis implémente.

# 1. État existant à conserver

Notre installation actuelle :

- Répertoire : `/apps/stremio/`
- Frontend : `/apps/stremio/web/`
- Déploiement : `/apps/stremio/deploy/`
- Domaine : `https://stremio.walter-ai.cloud/`
- Base PostgreSQL dédiée : `stremio_app`
- Stremio Web officiel, branche development.
- Dernier commit relevé par l'audit : `325de9b0b3bcd8736826c6aedc813e26a24c7139` (revérifier le HEAD).
- Authentification et synchronisation Stremio fonctionnelles.
- Lecture via TorBox déjà confirmée.
- Problèmes de compatibilité de certains flux constatés sur Stremio Web officiel.

Conserver les fonctionnalités existantes et ne pas modifier Walter ni ses autres services.

Travailler sur une branche dédiée et un environnement de préproduction de **notre propre interface**, avec tests et retour arrière.

Les déploiements doivent rester peu gourmands sur notre VM Oracle ARM64. Compiler sur le Mac si nécessaire.

# 2. Sources techniques vérifiées

## DX.BI

https://github.com/notdxbi/dxbi-stremio

Le projet intègre déjà :

- Interface Netflix et bandeaux cinématographiques.
- Teasers au survol et navigation enrichie.
- Profils « Who's watching? ».
- Lecteur amélioré.
- Recommandations et rangées personnalisées.
- « Just press Play » depuis la version 2.26.0.
- Classement automatique des sources.
- Mémorisation de la qualité, langue, fournisseur et parfois release.
- Repli automatique vers deux autres releases distinctes.
- Bouton pour changer de source après sélection.

Références prioritaires :

- `dxbi.plugin.js`
- `tools/quick-play-test.mjs`
- `CHANGELOG.md`, section 2.26.0
- `dxbi.theme.css`

J'ai vérifié le mécanisme `streamChoice`, `quickPlay` et ses tests.

Attention : le QuickPlay actuel présente des limites qu'il ne faut pas reproduire :

1. La langue du profil n'est pas une contrainte explicite dès la première lecture.
2. Une limite de résolution peut être dépassée lorsqu'aucune meilleure alternative n'est présente.
3. Les informations techniques sont en grande partie déduites des descriptions des addons.
4. Les règles des trackers privés et leurs ratios ne sont pas prises en charge par le moteur.
5. Les mécanismes de détection d'erreur diffèrent selon les appareils.

## Stremio Enhanced

https://github.com/REVENGE977/stremio-enhanced

Utiliser son approche des thèmes, plugins, paramètres et extensions comme référence.

Ne pas intégrer Electron côté serveur ou navigateur.

Ne pas reprendre aveuglément les injections JavaScript, le pont Node.js, les réglages Electron désactivant la sécurité Web ou les sélecteurs CSS fragiles.

Créer des modules React et des adaptateurs explicites autour du système existant.

## AIOStreams

https://github.com/Viren070/AIOStreams

AIOStreams sait agréger, dédupliquer, filtrer et classer les résultats de plusieurs addons.

Il propose des règles avancées, des groupes, variantes, classements pondérés et filtres sur les caractéristiques des releases.

Utilise-le seulement si ses capacités ajoutent une valeur réelle à notre moteur QuickPlay.

Privilégie son interface de protocole addon ou un service séparé plutôt qu'un portage massif de code.

Son interface utilisateur ne doit pas apparaître dans notre application familiale.

## Autres projets

- SkipDB : https://github.com/SkipDB-TV/skipdb
- AniSkip : https://aniskip.com/
- Watchly : https://github.com/TimilsinaBimal/Watchly
- Stremio For You : https://github.com/Joshuabastiaans/stremio-for-you
- Stremio AI Search : https://github.com/itcon-pty-au/stremio-ai-search

Réutiliser les APIs et composants adaptés plutôt que recréer leurs fonctionnalités sans raison.

# 3. Point juridique et architecture

Stremio Web est déclaré GPL-2.0, Stremio Enhanced MIT, DX.BI actuel GPL-3.0-or-later et AIOStreams AGPL-3.0.

La fonction Just press Play de DX.BI a été introduite après l'abandon de sa licence MIT.

**Ne copie donc pas directement son implémentation GPL-3 dans le frontend GPL-2 tant que la compatibilité n'est pas établie.**

Reproduis de manière indépendante le comportement attendu, avec une implémentation adaptée à notre code et à nos interfaces. Les spécifications fonctionnelles et les tests de comportement peuvent servir de référence.

Pour AIOStreams, privilégie la communication par protocole addon/service clairement séparé, avec vérification des obligations AGPL applicables.

Respecte les notices, les licences et les marques.

# 4. Priorité P1 — QuickPlay intelligent

C'est l'une de nos fonctionnalités principales.

L'utilisateur sélectionne un film ou un épisode, clique sur « Lecture » et la meilleure source compatible démarre directement.

Aucune liste de torrents ne doit être obligatoire dans le parcours normal.

Créer un module de sélection automatique propre à notre frontend, avec une architecture testable et déterministe.

## Pipeline

1. Identifier exactement le film ou l'épisode voulu.
2. Récupérer les résultats des addons Stremio configurés.
3. Exploiter les résultats au fur et à mesure de leur arrivée, sans attendre indéfiniment les addons lents.
4. Normaliser et dédupliquer les résultats.
5. Appliquer les contraintes strictes.
6. Appliquer les préférences du profil et de l'appareil.
7. Classer les sources restantes.
8. Sélectionner la meilleure.
9. Lancer directement le lecteur.
10. En cas d'échec confirmé, essayer une autre release compatible, avec une limite de deux alternatives.
11. Si aucune source ne fonctionne, présenter un choix manuel et une explication claire.

## Critères de sélection

- Film, saison et épisode exacts.
- Audio VF, VOSTFR ou VO.
- Sous-titres.
- Résolution.
- HDR, HDR10+ et Dolby Vision.
- Codec et compatibilité réelle du lecteur.
- Débit et connexion.
- Taille et type de release.
- Seeders si pertinents.
- État de disponibilité ou cache.
- Historique de fiabilité.
- Préférences déjà exprimées.
- Capacité réelle de l'appareil.

Les critères stricts doivent être séparés des préférences souples.

Exemple : « VF obligatoire » ne peut pas devenir VO parce qu'une version 4K obtient un meilleur score.

Une version 1080p compatible doit pouvoir battre une 4K incompatible ou inutile sur l'appareil.

Ne considère pas une langue, un codec ou un statut de cache déduit du nom comme une certitude. Gère explicitement les valeurs inconnues.

## Apprentissage

Mémoriser, par profil et par appareil :

- Langue préférée.
- Qualité maximale.
- Types de releases.
- Formats compatibles.
- Sources choisies manuellement.
- Sources ayant échoué.
- Préférences par série si nécessaires.

Il ne faut pas appeler un LLM pour cette sélection. Un moteur de règles et de scores suffit.

## Modes

- **Automatique** : par défaut, un clic suffit.
- **Qualité** : choix simplifié de qualité/langue.
- **Expert** : liste complète des sources avec filtres et informations.

Un bouton « Changer de source » doit rester accessible dans le lecteur.

## Fiabilité

Gérer les réponses tardives des addons, l'annulation d'une recherche, les changements d'épisode, les erreurs de décodage et les tentatives de secours.

Ne pas passer à une autre vidéo simplement parce qu'un buffering normal est momentanément lent.

Ne jamais réessayer indéfiniment la même release.

Mesurer le temps entre le clic et le démarrage effectif.

# 5. Protection des trackers privés

La lecture automatique doit prendre en compte les contraintes des trackers privés.

Prévoir une couche d'éligibilité des sources avant leur sélection, avec :

- Identification du tracker et du compte.
- Suivi du ratio et du crédit disponible lorsque techniquement accessible.
- Réserve de ratio configurable.
- Prise en compte des obligations de partage.
- Distinction entre torrent direct, source en cache et téléchargement debrid susceptible de déclencher une nouvelle opération.
- Blocage des actions automatiques si elles risquent de compromettre le compte ou si les informations critiques manquent.
- Aucune falsification du ratio.
- Secrets et passkeys protégés.

Ne pas déclencher automatiquement des téléchargements privés pour effectuer des vérifications techniques.

Cette protection doit être intégrée au moteur QuickPlay, et pas seulement ajoutée visuellement à l'interface.

# 6. Priorité P2 — Interface Netflix

Refondre notre Stremio Web avec une identité visuelle cohérente et une interface premium.

Objectif : une application qui se comporte comme Netflix, pas seulement une application aux mêmes couleurs.

Implémenter :

- Grand bandeau d'accueil cinématographique.
- Bande-annonce automatique après un délai configurable.
- Lecture muette par défaut et activation du son sur demande.
- Carrousel de contenus mis en avant.
- Cartes animées et agrandissement au survol.
- Mini-teasers au survol sur ordinateur.
- Focus et prévisualisation adaptés à la télécommande.
- Fiches immersives avec arrière-plans, synopsis, casting, bandes-annonces, notes et épisodes.
- Rangées horizontales personnalisables.
- Navigation fluide entre accueil, fiches et lecteur.
- Transitions et animations soignées.
- Gestion de la performance, du chargement différé et de l'économie de données.
- Une seule vidéo d'aperçu active à la fois.

Prendre DX.BI comme référence fonctionnelle, sans importer son plugin complet ni dépendre d'Electron.

Sur iOS, respecter les contraintes d'autoplay et d'ouverture des lecteurs externes.

# 7. Priorité P3 — Profils familiaux

Ajouter un écran « Qui regarde ? » dans notre interface.

Chaque profil doit disposer de :

- Nom et avatar.
- Historique et progression.
- Bibliothèque personnelle.
- Recommandations individuelles.
- Préférences audio et sous-titres.
- Préférences QuickPlay.
- Paramètres de qualité par appareil.
- Paramètres des bandes-annonces et génériques.
- Restrictions enfants et PIN lorsque nécessaires.

Étudier l'utilisation des profils Stremio Supporters, déjà annoncés officiellement, mais ne pas imposer d'abonnement.

Si les profils officiels ne conviennent pas, privilégier des comptes Stremio distincts avec un sélecteur familial sécurisé dans notre propre interface.

Ne pas mélanger les historiques ni les tokens d'authentification.

Ne pas considérer les profils DX.BI ou AIOStreams comme automatiquement compatibles avec les profils Stremio.

L'objectif est une synchronisation fiable entre les appareils, dans les limites réellement prises en charge.

Utiliser notre PostgreSQL `stremio_app` pour les préférences et données propres à notre application, sans dupliquer inutilement les données Stremio.

# 8. Priorité P4 — Lecteur enrichi

Ajouter :

- Reprise automatique.
- Sélection audio/sous-titres selon le profil.
- Saut des introductions, récapitulatifs et génériques.
- Prochain épisode et compte à rebours.
- Préchargement raisonnable du prochain épisode.
- Changement de source sans perdre la progression lorsque possible.
- Miniatures de recherche temporelle lorsque disponibles.
- Messages d'erreur compréhensibles.
- Paramètres de lecture mémorisés.

Vérifie d'abord les fonctions déjà présentes dans Stremio, notamment les fonctions Supporters, puis utilise SkipDB ou AniSkip lorsque nécessaire.

L'intégration avec les lecteurs externes iOS doit être honnête : ne pas promettre un saut automatique des génériques ni une récupération précise de la progression si l'application externe ne les permet pas.

Le navigateur et l'appareil doivent lire les médias directement ou via le mécanisme de lecture approprié, sans utiliser le tunnel Cloudflare comme relais vidéo.

# 9. Priorité P5 — Découverte et recommandations

Intégrer dans notre interface :

- Continuer à regarder.
- Parce que vous avez aimé…
- Recommandé pour vous.
- Nouvelles saisons.
- Films similaires.
- Tendances et nouveautés.
- Sélections par genre, durée et humeur.
- Recommandations pour plusieurs membres de la famille.

Étudier Watchly et Stremio For You pour réutiliser leurs méthodes ou leurs interfaces d'addons.

Ajouter une recherche en langage naturel inspirée de Stremio AI Search.

Les recommandations courantes doivent utiliser de préférence les historiques, métadonnées, similarités et scores classiques, sans appel LLM systématique.

# 10. Architecture modulaire

Garder une seule interface visible et une architecture technique simple.

Organiser logiquement les fonctionnalités en modules :

- Interface et navigation.
- Profils.
- Catalogues et recommandations.
- Recherche.
- Sources et QuickPlay.
- Player.
- Préférences.
- Intégrations.

Ne crée pas un microservice ou un conteneur par fonction.

Privilégie les composants React, les adaptateurs typés, les tests et les fonctionnalités activables/désactivables.

Évite les dépendances directes aux classes CSS générées ou aux variables globales instables de Stremio. Intègre-toi aux points de données et aux composants React appropriés.

Maintiens une séparation claire entre l'interface, le moteur de décision et le moteur de lecture.

Toute modification doit rester compatible avec les mises à jour futures de Stremio autant que possible.

# 11. Méthode de livraison

Je veux de l'implémentation réelle, pas un troisième audit général.

Travaille progressivement, en livrant des fonctionnalités testables dans **notre unique interface**.

Pour chaque priorité :

1. Implémente la fonctionnalité sur une branche de développement.
2. Fournis des tests unitaires et d'intégration.
3. Vérifie le comportement réel dans le navigateur.
4. Vérifie l'absence de régression sur l'authentification, les addons et la bibliothèque.
5. Mesure l'impact sur les ressources.
6. Déploie sur une préproduction de notre propre interface.
7. Active en production une fois les critères vérifiés, avec rollback possible.

Pour QuickPlay, teste au minimum :

- Première lecture avec préférence VF.
- Même série après choix manuel.
- Film 4K sur appareil 1080p.
- Dolby Vision incompatible.
- Source sans langue renseignée.
- Addon lent.
- Mauvais épisode dans un résultat.
- Première source illisible.
- Deuxième source fonctionnelle.
- Aucune source exploitable.
- Tracker privé non éligible.
- Changement de profil.
- Annulation d'une lecture.

Ne prétends jamais qu'un test simulé valide la lecture réelle.

Ne change pas le fonctionnement de l'APK Android TV officielle déjà installée. Nous traiterons plus tard la distribution de notre interface sur TV, mais prévois dès maintenant une architecture responsive et pilotable à la télécommande.

# 12. Résultat attendu

La famille ne doit voir ni AIOStreams, ni DX.BI, ni Stremio Enhanced, ni des menus techniques de torrents dans son parcours normal.

Elle doit seulement vivre cette expérience :

**Ouvrir notre Stremio → choisir son profil → voir un accueil cinématographique personnalisé → cliquer sur un film → lecture automatique dans la meilleure version compatible → saut des génériques → prochain épisode.**

Les fonctionnalités techniques restent accessibles dans les paramètres ou un mode expert.

Tu peux commencer immédiatement par P1 QuickPlay, puis construire le reste progressivement.

Je veux que tu accomplisses le maximum de travail vérifiable dans cette session, sans remplacer notre application existante ni demander de nouvelles validations pour chaque étape réversible.

À la fin, indique les fonctionnalités réellement livrées, les tests exécutés, l'URL de préproduction, les limites restantes et la prochaine étape de développement.