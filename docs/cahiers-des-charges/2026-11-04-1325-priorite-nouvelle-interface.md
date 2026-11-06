> Texte de Monsieur, donné dans Codex (session du matin) le 4 novembre 2026 à 13:25 UTC. Reproduit tel quel ; la suite du projet est racontée dans [../HISTORIQUE.md](../HISTORIQUE.md).

Je comprends pourquoi tu as commencé par QuickPlay : c'était l'ordre initial du prompt.

Mais je veux maintenant corriger les priorités. Notre objectif n'est pas d'améliorer marginalement l'interface classique de Stremio. Nous construisons notre propre expérience familiale, inspirée de Netflix et DX.BI, sur le moteur Stremio existant.

**Ne laisse plus QuickPlay bloquer le développement de la nouvelle interface.**

### 1. Priorité immédiate : nouvelle interface

Commence maintenant la véritable refonte visuelle de notre Stremio Web.

Référence fonctionnelle et visuelle principale :\
[https://github.com/notdxbi/dxbi-stremio](https://github.com/notdxbi/dxbi-stremio)

Je veux une transformation visible dès la prochaine version de préproduction, avec au minimum :

- Un accueil entièrement repensé.
- Un grand hero cinématographique avec bande-annonce automatique.
- Des carrousels horizontaux immersifs.
- Des cartes agrandies et animées au survol.
- Des fiches de films et séries repensées, avec bande-annonce, informations et bouton Lecture.
- Une navigation moderne et cohérente, adaptable au Mac, à l'iPad et à la TV.

Les interactions doivent fonctionner réellement. Ne te limite pas à changer les couleurs, les bordures ou à ajouter quelques contrôles.

Réutilise le moteur, les données, les catalogues et les routes de Stremio. Ne réécris pas inutilement ce qui fonctionne déjà.

Respecte les licences des projets de référence.

### 2. QuickPlay : poursuivre sans bloquer l'interface

Conserve tout le travail existant sur la branche `family/quickplay`.

Le blocage actuel se situe dans l'admission des sources Torrentio/TorBox.

Je veux que tu identifies précisément :

- Si la source est un flux HTTP directement lisible.
- Si TorBox indique qu'elle est déjà en cache.
- Si la lecture déclenche ou non un nouveau téléchargement.
- Si elle nécessite réellement une activité P2P ou une opération sur un tracker privé.
- Quelles informations sont fiables et lesquelles restent inconnues.

Ne classe pas automatiquement un lien TorBox en téléchargement P2P à risque simplement parce que son origine torrent initiale est inconnue.

Mais ne considère pas non plus une source comme sûre sur la seule présence du nom TorBox.

Une fois son comportement identifié, adapte la politique d'admission et teste la lecture automatique réelle, avec repli vers le mode manuel lorsque nécessaire.

### 3. Intégration finale

QuickPlay et la nouvelle interface sont deux modules du même produit, pas deux applications.

Le bouton Lecture de la nouvelle fiche immersive doit être connecté à QuickPlay dès qu'il sera opérationnel.

En attendant, il doit conserver le comportement de lecture Stremio existant. Il ne faut pas bloquer le développement visuel.

### 4. Méthode de travail

Conserve la production actuelle, sa synchronisation, ses addons et son système d'authentification.

Travaille en préproduction avec un déploiement réversible.

Privilégie l'implémentation plutôt que de nouveaux audits ou de longues séries de tests sur des objets fictifs.

Évite de mobiliser inutilement mon Mac ou de manipuler son interface graphique quand des tests locaux suffisent.

Je veux voir rapidement un résultat tangible : **en ouvrant la préproduction, l'application doit immédiatement se distinguer du Stremio classique.**

Une fois cette première refonte fonctionnelle, nous continuerons avec les profils familiaux, l'enrichissement du lecteur et les recommandations via Walter Router.

À la fin de cette étape, donne-moi l'URL de préproduction, les fonctionnalités réellement visibles et utilisables, et les problèmes encore ouverts. Ne présente pas QuickPlay comme terminé tant qu'une lecture automatique réelle n'a pas fonctionné.
