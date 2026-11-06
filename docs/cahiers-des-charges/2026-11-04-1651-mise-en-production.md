> Texte de Monsieur, donné dans Claude Code (session « Reprise développement Stremio ») le 4 novembre 2026 à 16:51 UTC. Reproduit tel quel ; la suite du projet est racontée dans [../HISTORIQUE.md](../HISTORIQUE.md).

Finalisation et mise en production définitive de notre application de streaming
Je veux maintenant que tu termines le projet de bout en bout et déploies notre nouvelle application AIOStreams en production sur https://stremio.walter-ai.cloud.
Nous avons suffisamment exploré et développé. Je ne veux plus accumuler des préproductions, prototypes ou phases inachevées.
Objectif final
L'application doit être réellement utilisable par ma famille, avec une expérience fluide, intuitive et aussi proche que possible de Netflix.
Le parcours cible est :
Ouvrir stremio.walter-ai.cloud → Choisir son profil → Choisir un film ou un épisode → Appuyer sur Lecture → Regarder immédiatement.
Tout doit fonctionner de manière cohérente et persistante, sans configuration technique imposée à l'utilisateur.
1. Terminer et stabiliser notre AIOStreams
Reprends la préproduction existante, ses adaptations et sa configuration. Ne repars pas de zéro.
Nous conservons :

* AIOStreams comme socle unique.
* Les teasers automatiques dans le hero et les cartes.
* Les couleurs dynamiques adaptées au contenu.
* Les catalogues et métadonnées en français.
* Les profils familiaux natifs.
* Les lecteurs, l'historique et les fonctionnalités natives d'AIOStreams.

Conserve notre version modifiée dans un fork ou une branche clairement identifiée, avec la révision upstream figée et une procédure de mise à jour fiable.
Ne crée pas de dépendance à DX.BI.
2. Rendre TorBox entièrement fonctionnel
Termine la configuration de TorBox.
Si tu disposes déjà des autorisations nécessaires pour accéder à mes identifiants Bitwarden, récupère la clé API existante depuis mon compte TorBox.
Sinon, indique-moi précisément l'unique intervention nécessaire pour débloquer cette étape.
Ne régénère aucune clé sans mon autorisation.
Ne divulgue jamais les identifiants, clés ou jetons dans les conversations, journaux ou appels LLM.
Vérifie ensuite :

* La connexion à TorBox.
* La récupération réelle des sources.
* Le statut de cache.
* La résolution des liens.
* La lecture vidéo effective.

Conserve par défaut une politique cached-only pour les opérations automatiques. Ne déclenche aucun nouveau téléchargement non autorisé.
3. Finaliser la lecture intelligente en un clic
C'est une fonctionnalité indispensable à la mise en production.
Utilise prioritairement les mécanismes natifs d'AIOStreams :

* Tri et score des sources.
* Auto-play first version.
* Préférences du profil.
* Résolution debrid.
* Failover existant.

Complète uniquement les fonctionnalités manquantes.
Comportement attendu :

1. Identifier précisément le contenu et l'épisode.
2. Récupérer les sources disponibles.
3. Sélectionner automatiquement la meilleure version réellement compatible.
4. Respecter les préférences audio, sous-titres et qualité.
5. Démarrer le lecteur sans menu technique.
6. Détecter les véritables erreurs.
7. Essayer automatiquement une autre version lorsque c'est nécessaire et sûr.
8. Préserver la position de lecture.
9. Proposer un changement manuel de source à tout moment.

Distingue les erreurs de résolution, de décodage, de réseau et le buffering temporaire.
Ne considère pas une source comme compatible ou incompatible sur la seule base d'un nom de fichier.
Teste impérativement la lecture réelle de plusieurs films et épisodes, y compris les changements d'épisodes et les reprises.
Ne présente pas la lecture automatique comme fonctionnelle sur la seule base de tests simulés.
4. Finaliser les profils familiaux
Configure le système natif AIOStreams pour qu'il soit prêt à accueillir plusieurs utilisateurs.
Je veux :

* Écran de sélection du profil.
* Historique indépendant.
* Favoris indépendants.
* Progression indépendante.
* Préférences de langue et de qualité individuelles.
* Synchronisation entre appareils.
* Gestion simple des profils depuis un compte administrateur.

Ne bloque pas le déploiement sur les noms définitifs des membres de la famille : prépare une configuration administrateur fonctionnelle et des profils temporaires de test.
Ne développe pas de système spécifique pour les enfants.
5. Finaliser l'expérience visuelle
Les teasers automatiques et les couleurs dynamiques sont déjà développés.
Conserve-les et finalise leur compatibilité :

* Desktop.
* Mobile.
* Safari sur iPhone/iPad.
* Android TV / Google TV.

Vérifie les deux modes du hero, dont celui qui suit la sélection sur TV.
Les teasers doivent démarrer sans son quand le navigateur l'autorise, sans ralentir l'interface.
Une seule vidéo de prévisualisation doit fonctionner à la fois.
Prévois des fallbacks propres si YouTube refuse la lecture intégrée.
Les couleurs dynamiques doivent rester discrètes, avec un contraste lisible.
Utilise les paramètres natifs AIOStreams pour exposer les réglages sans ajouter une seconde interface.
6. Recommandations et fonctionnalités secondaires
Active et configure les recommandations existantes d'AIOStreams, notamment les catalogues disponibles, More Like This et les suggestions TMDB lorsque les prérequis sont satisfaits.
Ne construis pas maintenant notre futur moteur de recommandations personnalisé.
Ne laisse pas les statistiques ou le masquage individuel des titres bloquer la mise en production. Ces améliorations peuvent être ajoutées ultérieurement.
Walter Router reste facultatif. L'application doit fonctionner sans lui.
7. Corriger et sécuriser l'infrastructure
Notre VM Oracle avait le disque à 91 % et le swap plein.
Avant la bascule :

* Analyse les consommations de stockage et de mémoire.
* Identifie les causes de saturation.
* Corrige les problèmes constatés sans supprimer de données utiles.
* Évite les images Docker, caches et builds redondants.
* Vérifie qu'AIOStreams et Walter peuvent fonctionner simultanément sans dégradation.
* Configure les redémarrages automatiques des services.
* Vérifie les sauvegardes, les secrets et les journaux.
* Mets en place des contrôles de disponibilité utiles.

Aucune suppression destructive sans autorisation.
Ne fais pas transiter les flux vidéo par notre VM ni par Cloudflare Tunnel lorsque les clients peuvent récupérer directement les flux.
Assure-toi que les clés et configurations sensibles ne sont jamais exposées au navigateur.
8. Déployer sur le domaine définitif
Le domaine de production est : https://stremio.walter-ai.cloud
Nous ne voulons pas conserver deux interfaces de streaming en production.
Le domaine est déjà utilisé par notre Stremio actuel : examine sa configuration Cloudflare Tunnel, son routage et ses services.
Ne crée pas un nouveau domaine lorsque la bascule peut être réalisée en modifiant proprement le routage existant.
Procédure attendue :

1. Sauvegarder l'installation Stremio actuelle et ses données.
2. Vérifier qu'une restauration et un retour arrière sont possibles.
3. Finaliser et valider AIOStreams sur la préproduction isolée.
4. Vérifier les paramètres de sécurité et d'authentification.
5. Basculer le routage du domaine existant vers AIOStreams.
6. Tester le fonctionnement réel depuis l'adresse publique.
7. Vérifier les sessions, les profils, les catalogues et la lecture.
8. Conserver temporairement l'ancien Stremio arrêté ou isolé pour pouvoir revenir en arrière.
9. Ne supprimer les anciens composants qu'après validation et selon une procédure explicite.

Si une permission Cloudflare bloque une modification, indique l'autorisation exacte requise. Ne contourne pas les protections.
Ne déclare pas la mise en production terminée tant que le domaine public ne sert pas effectivement la nouvelle application.
9. Validation complète
Je veux une validation de bout en bout.
Teste, dans la mesure où tu disposes d'appareils ou d'environnements de test réels :

* Navigateur desktop.
* Safari iPhone/iPad.
* Client Android TV et navigation télécommande.
* Client desktop natif.
* Profils et synchronisation.
* Lecture TorBox cached.
* Choix automatique des sources.
* Fallback sur une source défaillante.
* Reprise de lecture et épisode suivant.
* Teasers automatiques et couleurs dynamiques.
* Redémarrage des conteneurs et persistance des données.
* Accès public HTTPS et authentification.

Ne confonds pas compilation réussie, tests simulés et validation réelle.
Pour les appareils indisponibles, documente précisément ce qui a été vérifié et ce qui nécessite encore un test physique.
10. Critères de fin de projet
Je considérerai cette version comme terminée lorsque :

* `https://stremio.walter-ai.cloud` affiche notre nouvelle application AIOStreams.
* L'application est accessible de manière sécurisée.
* Les profils familiaux fonctionnent.
* Les catalogues sont correctement chargés.
* TorBox fournit des sources réellement lisibles.
* Le bouton Lecture démarre automatiquement une version compatible.
* Les erreurs sont gérées proprement, avec repli lorsque possible.
* Les langues, sous-titres et reprises fonctionnent.
* Les teasers et les couleurs dynamiques sont opérationnels.
* Les principaux appareils sont pris en charge, avec les limites explicitement documentées.
* Les données sont persistantes.
* La VM reste stable.
* Les services redémarrent correctement.
* La configuration est sauvegardée.
* L'ancien Stremio peut être restauré si nécessaire.

11. Méthode de travail
Je veux que tu exécutes le travail concret jusqu'à la mise en production, plutôt que de t'arrêter après chaque sous-étape.
Ne me demande pas de validation pour chaque opération normale de développement ou de test.
Sollicite-moi uniquement pour une véritable permission manquante, un secret impossible à récupérer légitimement, une opération destructive ou une décision ayant un impact important.
N'invente pas de réussite et ne contourne aucune permission.
Si une dépendance externe bloque une fonctionnalité, avance sur les autres éléments indépendants, puis reviens au blocage.
Livrable final
Je veux un bilan factuel de la production :

* URL définitive.
* Version et commit déployés.
* Fonctionnalités réellement opérationnelles.
* Tests réalisés et résultats.
* Limitations éventuelles selon les appareils.
* État des ressources de la VM.
* Système de sauvegarde et de rollback.
* Procédure simple pour mettre à jour AIOStreams.
* Éventuelles interventions encore nécessaires de ma part.

Notre objectif est maintenant de livrer une application de streaming utilisable au quotidien sur notre domaine définitif, pas de poursuivre une expérimentation indéfinie.
