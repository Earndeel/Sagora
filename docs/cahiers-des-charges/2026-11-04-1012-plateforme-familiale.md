> Texte de Monsieur, donné dans Codex (session du matin) le 4 novembre 2026 à 10:12 UTC. Reproduit tel quel ; la suite du projet est racontée dans [../HISTORIQUE.md](../HISTORIQUE.md).

Je veux faire évoluer l'installation Stremio existante sur notre VM Oracle ARM64 en une plateforme de streaming familiale, légère, personnalisable et accessible depuis différents appareils.

L'objectif est de disposer de notre propre interface Stremio Web, tout en conservant la synchronisation avec les serveurs officiels de Stremio.

Nous allons également utiliser **l'instance PostgreSQL déjà présente sur la VM**, avec une base dédiée à notre application, afin de préparer les futures fonctionnalités personnalisées.

## 1. Architecture et organisation

Respecter strictement l'organisation existante de la VM :

- `/walter/` : intelligence et infrastructure de Walter, à préserver.
- `/apps/` : applications tierces installées.
- `/projects/` ou chemin réel existant : projets développés.
- `/instances/` : instances et données des utilisateurs.

Stremio doit rester dans `/apps/stremio/`, indépendamment de Walter.

Organiser proprement l'application autour des composants suivants :

- `web/` : fork maintenable de Stremio Web.
- `server/` : serveur de streaming déjà installé.
- `config/` : configurations.
- `deploy/` : conteneurs et déploiement.
- `data/` : données persistantes strictement nécessaires.

Vérifie l'existant avant de déplacer ou modifier quoi que ce soit. Évite les duplications et conserve les conventions déjà utilisées sur la VM.

## 2. PostgreSQL mutualisé

Nous allons utiliser le serveur PostgreSQL existant, sans déployer une seconde instance.

Commence par auditer :
- Les versions et instances PostgreSQL existantes.
- Les bases, schémas, rôles et dépendances actuels.
- Les mécanismes de sauvegarde.
- La charge mémoire et CPU.

Créer ensuite, si les préconditions sont réunies, une base logique dédiée, par exemple `stremio_app`, avec un rôle SQL propre à l'application.

Exigences :
- Isolation stricte vis-à-vis des bases, schémas et permissions de Walter.
- Aucun accès de l'application aux données de Memory ou Context.
- Pas de rôle superutilisateur pour Stremio.
- Connexion privée uniquement.
- Identifiants conservés dans le gestionnaire de secrets existant, sans exposition dans Git ou les logs.
- Migrations versionnées et réversibles.
- Sauvegarde et restauration indépendantes, orchestrables par `ops/`.

Ne pas créer de tables inutiles.

La base pourra accueillir ultérieurement les préférences, profils applicatifs, recommandations et autres fonctionnalités spécifiques à notre frontend.

**Important :** les comptes Stremio, addons, bibliothèques et progressions restent synchronisés via l'infrastructure officielle. Notre PostgreSQL ne doit pas dupliquer ces données sans besoin fonctionnel explicite.

## 3. Frontend Stremio Web

Utiliser le projet officiel :
https://github.com/Stremio/stremio-web

Objectifs :
- Étudier l'architecture actuelle, les licences et les dépendances.
- Déployer une version Web fonctionnelle, sans refonte graphique initiale.
- Conserver les comptes Stremio individuels et leur synchronisation officielle.
- Préserver la connexion par QR code si elle est disponible.
- Préparer un fork maintenable et actualisable depuis l'upstream.
- Privilégier la compilation hors de la VM, puis la distribution de fichiers statiques.
- Prévoir une interface responsive et installable en PWA sur iOS/iPadOS.

Ne modifie pas les API officielles ni les mécanismes de synchronisation sans nécessité démontrée.

## 4. Lecture vidéo

La VM Oracle ne doit pas devenir inutilement un relais vidéo.

Priorités :
1. Lecture directe sur les appareils lorsque c'est possible.
2. Utilisation des lecteurs externes lorsque nécessaire.
3. Recours au serveur Stremio déjà installé uniquement pour les flux qui en ont besoin.
4. Pas de transcodage lourd activé par défaut.

Vérifier les limitations sur Safari iOS/iPadOS, macOS, Windows et Android TV.

Respecter les règles de sortie réseau existantes : ne pas faire sortir de trafic directement par la VM de Singapour lorsque cela contrevient à la politique réseau de Walter.

## 5. Accès familial

Chaque membre de la famille doit pouvoir utiliser son propre compte Stremio, sans devoir se connecter à Walter.

Préparer :
- Une URL HTTPS dédiée.
- Un accès distant simple depuis navigateur.
- Une PWA installable sur iPhone et iPad.
- Une authentification sécurisée compatible avec Stremio.
- Une configuration compatible avec les lecteurs externes lorsque nécessaire.

Examiner le reverse proxy existant avant d'en installer un nouveau.

Ne pas exposer publiquement les ports internes de streaming ou PostgreSQL.

Tout accès public devra être sécurisé et validé avant activation.

## 6. Ressources et exploitation

Walter fonctionne déjà sur cette VM Oracle ARM64. Préserver ses ressources et sa disponibilité.

Mesurer avant et après :
- CPU et RAM utilisés.
- Espace disque disponible.
- Charge de PostgreSQL.
- Consommation des conteneurs Stremio.
- Impact du frontend au repos.

Privilégier une architecture légère et un nombre minimal de services.

Configurer des contrôles de santé, des politiques de redémarrage et des limites de ressources adaptées, sans perturber les autres applications.

## 7. Exécution progressive

**P0 — Audit**
Examiner l'installation Stremio, PostgreSQL, le réseau, les ressources et les mécanismes de déploiement existants.

**P1 — Base et frontend**
Créer la base PostgreSQL isolée et déployer le frontend officiel de Stremio. N'ajouter aucun backend métier ou table applicative tant qu'ils ne sont pas nécessaires.

**P2 — Fonctionnement**
Valider l'authentification, les addons, la synchronisation, la PWA et les possibilités de lecture sur les appareils compatibles.

**P3 — Accès familial**
Préparer HTTPS, l'accès distant sécurisé et les conditions d'utilisation familiale.

**P4 — Personnalisation**
Préparer l'évolution graphique et fonctionnelle, sans entreprendre de refonte pour l'instant.

Tu peux exécuter les opérations réversibles, testées et non perturbatrices. Ne supprime ni ne migre les données existantes sans justification et sauvegarde préalable. Ne modifie pas le cœur de Walter.

## 8. Compte rendu attendu

À la fin, explique succinctement :

1. L'architecture réellement mise en place.
2. Ce qui fonctionne déjà et ce qui reste à faire.
3. La structure PostgreSQL créée et son isolation.
4. Les accès disponibles et leur niveau de sécurité.
5. Les tests exécutés et leurs résultats.
6. Les ressources consommées.
7. Les limites connues, notamment sur iPhone/iPad et Android TV.
8. Les prochaines étapes pour personnaliser l'interface.

**Principe directeur : réutiliser au maximum les fonctionnalités officielles de Stremio, mutualiser l'infrastructure technique existante et garder notre application indépendante de Walter.**