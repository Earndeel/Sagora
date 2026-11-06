> Texte de Monsieur, donné dans Claude Code (session « Reprise développement Stremio ») le 4 novembre 2026 à 16:14 UTC. Reproduit tel quel ; la suite du projet est racontée dans [../HISTORIQUE.md](../HISTORIQUE.md).

Projet Stremio familial — AIOStreams comme fondation, expérience Netflix enrichie
1. Objectif
Nous construisons une application de streaming familiale unifiée, auto-hébergée, multiplateforme, offrant une expérience plus fluide, intuitive et personnalisable que Stremio classique.
Décision architecturale : AIOStreams devient notre candidat principal pour constituer le socle de l'application.
Nous souhaitons exploiter au maximum ses fonctionnalités natives et ne développer que les améliorations réellement nécessaires.
Références :

* AIOStreams : https://github.com/Viren070/AIOStreams
* DX.BI : https://github.com/notdxbi/dxbi-stremio
* Installation existante : https://stremio.walter-ai.cloud/
* Walter Router : https://github.com/Earndeel/w.Alter

Le parcours utilisateur cible est :
Ouverture → Choix du profil → Sélection d'un film ou épisode → Lecture immédiate de la meilleure source compatible.
L'utilisateur ne doit pas avoir à manipuler des releases, codecs, trackers ou configurations techniques.
Nous ne voulons pas juxtaposer plusieurs interfaces : le produit final doit constituer une seule expérience cohérente.
2. Préserver et examiner l'existant
Avant toute intervention :

1. Examine notre installation Stremio actuelle sur la VM Oracle, ses services, configurations, addons, authentification, données et sauvegardes.
2. Vérifie les travaux déjà réalisés sur QuickPlay et DX.BI, notamment les branches de développement existantes.
3. Examine la version actuelle d'AIOStreams, son architecture et les fonctions déjà implémentées.
4. Identifie ce qui peut être réutilisé directement.
5. Vérifie les ressources nécessaires sur notre environnement Oracle ARM64.

Ne recommence pas les fonctionnalités déjà développées et opérationnelles.
L'installation actuelle doit rester accessible, intacte et immédiatement récupérable.
Développe AIOStreams dans un environnement de préproduction isolé, avec sa propre configuration, ses secrets et ses données.
Vérifie les chemins réels et les conventions de déploiement existantes plutôt que de supposer leur structure.
3. AIOStreams : notre socle applicatif
Exploite au maximum ce qu'AIOStreams possède déjà :

* Agrégation des addons Stremio.
* Intégration de TorBox et des autres fournisseurs configurés.
* Centralisation des sources.
* Déduplication, filtrage et classement pondéré.
* Catalogues et métadonnées.
* Interface Web et PWA.
* Clients desktop et Android TV.
* Profils familiaux et historiques séparés.
* Bibliothèques, favoris et progression.
* Lecture automatique.
* Sous-titres et préférences linguistiques.
* Passage automatique à l'épisode suivant.
* Saut des introductions et génériques.
* Lecteurs et paramètres multimédias.
* Recherche et recommandations déjà existantes.

Ne construis aucun second système lorsqu'AIOStreams fournit une fonctionnalité équivalente.
Privilégie la configuration native, puis des extensions ciblées, et ne modifie le cœur qu'en dernier recours.
Conserve une architecture maintenable, compatible autant que possible avec les futures mises à jour upstream.
4. Lecture intelligente : objectif fonctionnel prioritaire
Le bouton Lecture doit lancer directement la meilleure source disponible, sans afficher la liste technique des releases.
Commence par exploiter :

* Le classement natif des sources AIOStreams.
* Les filtres et préférences.
* L'option « Auto-play the first version ».
* La reprise de la version précédemment utilisée.
* Le failover existant, lorsqu'il s'applique.

Configure ces fonctionnalités avant d'en développer de nouvelles.
Le classement doit tenir compte notamment :

* De la langue audio : VF, VO, VOSTFR.
* Des sous-titres disponibles.
* De la résolution et du bitrate.
* De la compatibilité des codecs avec l'appareil.
* Du HDR et Dolby Vision.
* De la qualité de la release.
* Du statut de cache debrid.
* De la fiabilité et des performances de lecture.
* Des préférences du profil.

Distingue les contraintes strictes des préférences souples.
Une information technique inconnue ne doit pas être automatiquement interprétée comme une incompatibilité.
Le lancement doit être rapide et éviter d'attendre inutilement les fournisseurs les plus lents.
Fallback
Vérifie précisément les limites du failover natif d'AIOStreams, notamment avec les flux externes Torrentio/TorBox.
Si une source ne démarre pas ou échoue réellement, le système doit pouvoir tenter une autre source compatible lorsque c'est techniquement possible, sans créer une boucle infinie.
Ne réimplémente pas le moteur de sélection de DX.BI si AIOStreams suffit.
Préserve un mode manuel permettant de choisir une autre version.
Sécurité des sources
Respecte les règles des trackers privés et des services debrid.
La sélection automatique ne doit pas déclencher involontairement un téléchargement non mis en cache ou une opération compromettant le ratio d'un tracker privé.
Ne confonds pas un flux HTTP direct déjà disponible avec une opération P2P nécessitant un nouveau téléchargement.
5. Améliorations inspirées de DX.BI
Nous ne voulons plus intégrer DX.BI intégralement.
Ses fonctionnalités sont désormais une référence d'expérience utilisateur. Nous souhaitons développer directement dans AIOStreams les améliorations réellement manquantes.
5.1. Teasers automatiques façon Netflix — priorité visuelle principale
C'est la fonctionnalité de DX.BI qui nous intéresse le plus.
Implémente la lecture automatique des bandes-annonces et teasers dans les composants React existants d'AIOStreams.
Références à examiner :

* `packages/web/src/components/hero.tsx`
* `packages/web/src/components/card-preview.tsx`
* Les mécanismes existants de récupération et de lecture des trailers.

Comportement attendu :
Bandeau d'accueil :

* Afficher immédiatement l'illustration du film ou de la série.
* Après un court délai, lancer automatiquement le teaser s'il existe.
* Démarrer sans son.
* Permettre d'activer ou désactiver le son.
* Conserver le titre, le synopsis et les actions par-dessus la vidéo.
* Réaliser une transition douce entre image et vidéo.
* Arrêter la vidéo quand le contenu mis en avant change.

Cartes des films et séries :

* Agrandir la carte au survol ou au focus télécommande, en réutilisant le composant natif existant.
* Après un délai raisonnable, remplacer son illustration par le teaser.
* Arrêter immédiatement la lecture lorsque la prévisualisation est fermée.
* Ne jamais démarrer plusieurs teasers simultanément.

Optimisation :

* Respecter les politiques d'autoplay des navigateurs.
* Prévoir un fallback vers l'image lorsqu'un teaser est indisponible ou interdit à l'intégration.
* Éviter toute consommation excessive de bande passante.
* Ne pas faire transiter les bandes-annonces par notre VM.
* Ne charger que les vidéos nécessaires.
* Respecter les préférences de réduction des animations.
* Prévoir une option de désactivation.

L'expérience doit rester fluide sur desktop, iPad, mobile et Android TV.
5.2. Couleurs dynamiques — priorité visuelle secondaire
DX.BI propose « Match each title's colours ».
Nous souhaitons reproduire ce comportement dans AIOStreams.
Pour chaque film ou série affiché, extraire une couleur pertinente de son artwork et l'utiliser pour adapter subtilement :

* Les boutons principaux.
* Certains accents de l'interface.
* La barre de progression du lecteur.
* Éventuellement des halos ou dégradés discrets autour du visuel.

Exemple :

* Dune : accents orange/sable.
* Avatar : accents bleus/turquoise.

Le fond principal doit rester sombre, élégant et cohérent.
Ne transforme pas complètement la palette de l'application à chaque changement de contenu.
Garantis un contraste suffisant et des transitions fluides.
Prévois la possibilité de désactiver cette fonctionnalité et de conserver une couleur d'accent fixe.
L'implémentation doit être légère et mutualisée entre les composants.
5.3. Masquage individuel des titres
Vérifie d'abord si AIOStreams propose déjà un mécanisme équivalent.
Sinon, ajoute la possibilité de sélectionner « Ne plus me proposer ce titre » depuis une carte ou une fiche.
Le titre doit être exclu des recommandations personnalisées et des carrousels concernés, sans être supprimé de la recherche générale.
Ce choix doit être enregistré par profil, synchronisé entre appareils et réversible.
5.4. Statistiques personnelles
Réutilise l'historique de lecture existant pour proposer ultérieurement :

* Temps total de visionnage.
* Films et épisodes regardés.
* Genres les plus fréquents.
* Séries terminées.
* Récapitulatif annuel.

Cette fonction est secondaire : ne la laisse pas retarder la lecture et la refonte visuelle.
N'ajoute pas de collecte de données redondante si l'historique existant suffit.
6. Recommandations : utiliser l'existant, moteur avancé reporté
Décision importante : nous développerons un moteur de recommandations plus puissant ultérieurement.
Pour cette première version, exploite les systèmes déjà présents dans AIOStreams :

* « More Like This ».
* Recommandations TMDB.
* Catalogues de suggestions.
* AI Search, si pertinent et fonctionnel.
* Favoris, historique et fonctionnalités natives déjà disponibles.

Vérifie les capacités et limites réelles de ces systèmes.
Ne confonds pas une recommandation liée à un film avec une recommandation réellement personnalisée selon l'historique entier d'un utilisateur.
Walter Router
Notre objectif futur sera de construire un moteur de personnalisation capable d'exploiter les goûts, évaluations, habitudes et historiques de chaque profil.
Il pourra utiliser `walter/router` pour des tâches de raisonnement ou de recommandation.
Mais ce moteur n'est pas à développer maintenant.
Pour l'instant :

* Conserve les données nécessaires à une future personnalisation.
* Garantit leur séparation par profil.
* Réutilise les mécanismes existants.
* Ne crée pas un nouveau système de recommandation LLM.
* Ne multiplie pas les modèles, fournisseurs ou API inutiles.
* N'introduis aucune dépendance obligatoire à Walter.

Si une intégration IA existante est activée, elle doit rester optionnelle, correctement authentifiée et maîtrisée en coût.
7. Profils familiaux
Utilise le système de profils natif d'AIOStreams.
Nous voulons :

* Un écran « Qui regarde ? ».
* Un historique propre à chaque profil.
* Une reprise individuelle.
* Des favoris individuels.
* Des préférences linguistiques propres.
* Des préférences de qualité et de lecture.
* Une synchronisation entre appareils.

Ne développe pas de système spécifique de profils enfants ou de contrôle parental avancé. Ce n'est pas un besoin de ce projet.
Évite également d'importer le système de profils DX.BI si AIOStreams couvre nos besoins.
8. Compatibilité multiplateforme
Les plateformes prioritaires sont :

1. Web desktop.
2. iPhone et iPad.
3. Android TV / Google TV.
4. Mac et Windows via les clients natifs disponibles.
5. Android mobile.

Réutilise les clients déjà existants d'AIOStreams.
Ne développe pas de nouveaux clients natifs sans nécessité démontrée.
L'interface doit rester cohérente entre les appareils, même si les moteurs de lecture diffèrent.
Sur iOS, tiens compte des limites de Safari/PWA, des codecs et de la synchronisation des lecteurs externes.
Sur TV, vérifie la navigation complète à la télécommande.
9. Infrastructure, sécurité et licences
La solution doit fonctionner sur notre VM Oracle ARM64, avec une consommation maîtrisée.
Principes :

* AIOStreams comme socle principal après validation.
* Pas de backend métier redondant.
* PostgreSQL réutilisé si pertinent, avec isolation des données.
* Secrets protégés.
* Services isolés.
* Sauvegardes et restauration vérifiables.
* Déploiement réversible.
* Journalisation sans exposition des identifiants.
* Versions upstream identifiées et figées pour les déploiements.

Les flux vidéo doivent être lus directement par les clients lorsque c'est possible.
Ne transporte pas les vidéos à travers Cloudflare Tunnel ou notre VM lorsque cela n'est pas nécessaire.
AIOStreams est sous AGPL-3.0 et DX.BI sous GPL-3.0-or-later. Vérifie les obligations applicables à toute réutilisation effective de code. Préserve les attributions.
Ne copie pas le plugin DX.BI entier simplement pour obtenir les teasers.
10. Plan d'exécution
Phase 1 — Vérification courte de l'existant
Examine l'installation actuelle et les fonctionnalités AIOStreams réellement disponibles.
Identifie les éléments que nous avons déjà développés et les risques d'intégration.
Ne produis pas un long audit redondant : concentre-toi sur les décisions qui influencent l'implémentation.
Phase 2 — Installer AIOStreams en préproduction
Prépare une instance isolée sur la VM.
Configure les sources existantes, dont TorBox, sans exposer les identifiants.
Teste l'authentification, les profils, les catalogues et les flux.
Conserve l'application Stremio actuelle intacte.
Phase 3 — Valider la lecture en un clic
Configure le classement et l'autoplay natifs.
Teste sur des films, séries et anime réels, avec nos sources existantes.
Vérifie les préférences VF/VO/VOSTFR et les formats compatibles.
Teste le fallback et identifie uniquement les lacunes effectives.
Phase 4 — Expérience Netflix
Développe les teasers automatiques dans le hero et les cartes.
Ajoute les couleurs dynamiques.
Intègre ces comportements à l'interface AIOStreams existante, sans recréer l'accueil.
Cette phase doit produire un résultat immédiatement visible et utilisable.
Phase 5 — Personnalisation légère
Configure les recommandations natives.
Ajoute le masquage individuel des titres si absent.
Prépare les statistiques personnelles seulement si les phases prioritaires sont stables.
Reporte explicitement le moteur de recommandations avancé.
Phase 6 — Validation et adoption
Vérifie les principaux parcours sur les plateformes disponibles.
Mesure :

* Temps d'ouverture.
* Temps entre Play et la première image.
* Fiabilité des sources.
* Fluidité des carrousels et teasers.
* Consommation CPU/RAM.
* Bande passante consommée.
* Reprise de lecture et synchronisation.

Ne remplace pas la production sans validation du parcours utilisateur complet.
11. Critères de réussite
La première version sera satisfaisante lorsque :

1. L'application possède une interface cohérente et agréable.
2. Les membres de la famille disposent de profils indépendants.
3. Les catalogues et sources existants sont accessibles.
4. Un clic sur Lecture démarre automatiquement une source compatible.
5. Les préférences audio et sous-titres sont respectées autant que le permettent les métadonnées disponibles.
6. Les sources défaillantes sont gérées proprement.
7. Les épisodes suivants et la reprise fonctionnent.
8. Le hero et les cartes peuvent lancer automatiquement des teasers.
9. Les couleurs de l'interface s'adaptent subtilement au contenu.
10. L'application reste fluide sur nos appareils.
11. Les recommandations natives sont utilisables.
12. Aucun service IA supplémentaire n'est obligatoire.
13. L'installation précédente reste entièrement récupérable.

12. Livrables
À la fin de chaque phase, présente uniquement :

* Ce qui fonctionne réellement.
* Ce qui a été réutilisé sans modification.
* Ce qui a été modifié et pourquoi.
* Les tests effectivement exécutés.
* Les limitations restantes.
* L'URL de préproduction lorsque disponible.
* Les conséquences sur les ressources de la VM.
* Les prochaines actions prioritaires.

Je veux une implémentation concrète, pas une succession d'audits théoriques.
Priorité générale : réutiliser au maximum AIOStreams, garantir la lecture en un clic et obtenir une expérience Netflix enrichie par les teasers et les couleurs dynamiques.
Ne surdéveloppe pas les systèmes déjà disponibles.
Le futur moteur de recommandations intelligentes fera l'objet d'une phase distincte, après stabilisation de l'application.
