> Texte de Monsieur, donné dans Codex (session du matin) le 4 novembre 2026 à 10:28 UTC. Reproduit tel quel ; la suite du projet est racontée dans [../HISTORIQUE.md](../HISTORIQUE.md).

On continue. Je veux maintenant que notre installation Stremio devienne une application familiale réellement fonctionnelle, accessible depuis Internet, sans tunnel SSH et sans configuration technique pour les utilisateurs.

Tu peux utiliser les accès Cloudflare déjà présents dans le coffre de Walter, y compris ma Global API Key si nécessaire. Ne m'en demande pas une nouvelle.

L'objectif n'est plus seulement de préparer l'architecture : **je veux un déploiement opérationnel de bout en bout, avec les tests possibles réellement exécutés.**

### 1. Finaliser l'accès Cloudflare HTTPS

Nous disposons déjà d'une infrastructure Cloudflare et d'un tunnel utilisé par d'autres applications.

- Audite le tunnel existant, les domaines disponibles et les routes actuelles.
- Réutilise l'infrastructure existante plutôt que d'installer un nouveau reverse proxy ou tunnel.
- Crée un sous-domaine dédié à Stremio, sur un domaine déjà contrôlé.
- Configure le DNS, l'ingress et HTTPS.
- Déploie publiquement le frontend Stremio Web uniquement après vérification de sa configuration et de ses contrôles de sécurité.
- Ne modifie ni ne perturbe les autres applications.
- Vérifie l'accès depuis Internet, pas seulement localhost.
- Teste également l'accès depuis un navigateur mobile.

Pour Cloudflare :
- Cherche d'abord un API Token limité aux permissions nécessaires.
- Si seul le Global API Key est disponible, je t'autorise à l'utiliser pour les opérations nécessaires.
- Accède aux secrets via les mécanismes existants, sans les afficher, les enregistrer dans les logs ou les intégrer aux fichiers du projet.
- Ne modifie aucun paramètre Cloudflare sans rapport avec Stremio.

### 2. Rendre Stremio Web réellement fonctionnel

Le frontend est déjà installé dans `/apps/stremio/web/` et servi par Nginx.

Je veux vérifier et corriger l'ensemble du parcours utilisateur :

- Chargement complet de l'application.
- Absence d'erreurs bloquantes dans le navigateur.
- Connexion au compte Stremio officiel.
- Connexion par QR code si disponible.
- Synchronisation des addons existants.
- Bibliothèque et favoris.
- Historique et progression de lecture.
- Recherche de films et séries.
- Affichage des catalogues.
- Sélection des sources.
- Sélection des sous-titres.
- Ouverture du lecteur vidéo.

Ne remplace pas les API officielles et ne recrée pas les fonctionnalités de synchronisation déjà fournies gratuitement par Stremio.

Vérifie les contraintes CORS, CSP, HTTPS, cookies, WebAssembly et service workers.

Utilise le Mac et son navigateur distant pour réaliser de véritables tests de rendu et d'interaction, pas uniquement des requêtes HTTP.

Si la connexion au compte nécessite mon intervention, prépare le parcours et indique-moi précisément l'étape à effectuer, sans contourner MFA, CAPTCHA ou consentement.

### 3. Lecture vidéo et compatibilité

Je sais déjà que sur iPad et iPhone, Stremio Web fonctionne avec un lecteur externe.

Je veux conserver ce fonctionnement.

**iPhone / iPad :**
- Interface Web responsive.
- Installation PWA depuis Safari.
- Connexion au compte.
- Synchronisation des addons.
- Lecture via VLC ou un autre lecteur externe compatible.
- Retour propre à l'interface après la lecture.

**Mac / PC :**
- Lecture directe dans le navigateur lorsque possible.
- Lecteur externe lorsque nécessaire.

**Android TV / Smart TV :**
- Préserver la compatibilité avec les applications Stremio officielles et leurs comptes.
- Étudier les possibilités réelles d'utilisation de notre frontend personnalisé sur TV.
- Ne pas développer d'APK personnalisé pour l'instant.

Le serveur de streaming existant doit rester optionnel.

Ne fais pas transiter les vidéos par Oracle ou Cloudflare si elles peuvent être lues directement par l'appareil.

N'utilise pas le tunnel Cloudflare public pour relayer des vidéos ou des fichiers volumineux en violation des conditions du service.

Si certains types de flux nécessitent le serveur Stremio, étudie une solution distincte et sécurisée, en respectant les contraintes de routage réseau de la VM. Ne prétends pas qu'un flux fonctionne sans test réel.

### 4. Finaliser PostgreSQL

Je confirme ma décision : je veux utiliser l'instance PostgreSQL existante, avec une base dédiée à notre application Stremio.

Tu avais identifié des questions d'isolation et de sauvegarde. Je veux maintenant que tu les résolves proprement.

- Crée une base `stremio_app` et un rôle applicatif dédié.
- Isole les permissions : aucune lecture ou modification des données de Walter.
- Analyse les droits `CONNECT` hérités et les privilèges effectifs, sans modifier dangereusement les bases existantes.
- Stocke les identifiants dans le coffre approprié.
- Configure les sauvegardes indépendantes.
- Teste une restauration dans un environnement isolé.
- Prépare des migrations versionnées.

Ne crée aucune table métier inutile.

La base est destinée aux futures fonctions personnalisées. Elle ne doit pas interférer avec l'authentification ou la synchronisation Stremio officielle.

Ne bloque pas la mise en service du frontend pour une fonctionnalité PostgreSQL dont il ne dépend pas.

### 5. Fiabilité et optimisation

L'application doit pouvoir fonctionner en permanence sans dégrader Walter.

- Vérifie les ressources disponibles.
- Analyse le swap presque saturé observé lors du précédent audit, en distinguant occupation historique et activité de swap réelle.
- Mesure CPU et RAM au repos.
- Configure les redémarrages et healthchecks.
- Vérifie le comportement après redémarrage.
- Préserve les fichiers persistants et les volumes existants.
- Ne compile pas lourdement sur Oracle si le Mac ou une CI peut effectuer le travail.
- Évite les services et dépendances supplémentaires inutiles.

L'application doit rester indépendante de `/walter/` et confinée dans `/apps/stremio/`, hors infrastructure mutualisée.

### 6. Sécurité de l'accès familial

Je veux que les membres de ma famille puissent accéder à l'application depuis n'importe quel réseau, simplement avec une URL.

Leur compte Stremio doit rester distinct de Walter.

- Protège l'infrastructure et les éventuelles fonctions d'administration.
- Ne rends pas PostgreSQL ni le serveur de streaming directement publics.
- Vérifie les implications d'une éventuelle couche Cloudflare Access sur le login Stremio, la PWA et les lecteurs externes.
- Ne mets pas en place une double authentification qui rendrait l'utilisation familiale pénible sans bénéfice démontré.
- Préserve les sessions et préférences de chaque utilisateur.

### 7. Tests et critères d'acceptation

L'objectif est d'atteindre le statut « opérationnel » sur les fonctionnalités qui peuvent être testées depuis ton environnement.

Valide réellement :

1. URL HTTPS accessible depuis Internet.
2. Frontend chargé sans erreur bloquante.
3. PWA et fichiers nécessaires accessibles.
4. Connexion Stremio et synchronisation, après mon intervention si nécessaire.
5. Catalogue, bibliothèque et addons utilisables.
6. Sélection d'un contenu et ouverture d'une source de test autorisée.
7. Lecture vidéo ou ouverture du lecteur externe selon l'environnement.
8. Base PostgreSQL isolée, avec sauvegarde et restauration testées.
9. Persistance des services après redémarrage.
10. Absence de régression sur Walter et les autres applications.

Distingue les tests automatisés, les tests réels sur navigateur et ceux qui nécessitent un appareil physique.

Ne considère pas l'application comme fonctionnelle à 100 % si un parcours essentiel n'a pas été validé. Signale précisément les limites restantes.

### 8. Méthode d'exécution

Travaille de manière autonome et incrémentale jusqu'à ce que tous les éléments réalisables soient terminés.

Ne t'arrête pas après chaque petite étape pour proposer un nouveau plan.

Tu peux prendre les décisions techniques nécessaires tant qu'elles sont réversibles et respectent l'architecture existante.

Ne demande mon intervention que pour une action réellement sensible, destructive, nécessitant un consentement ou une authentification humaine.

Ne touche pas au cœur de Walter.

### Livrable attendu

Je veux un compte rendu final court et factuel comprenant :

- L'URL HTTPS opérationnelle.
- Les fonctionnalités réellement testées.
- Le fonctionnement de l'authentification et des addons.
- La situation de la lecture vidéo selon les appareils.
- L'état de PostgreSQL et des sauvegardes.
- Les consommations CPU/RAM.
- Les limitations restantes.
- La procédure de mise à jour et de rollback.

**Priorité : livrer une application familiale utilisable immédiatement, avant toute personnalisation graphique.**