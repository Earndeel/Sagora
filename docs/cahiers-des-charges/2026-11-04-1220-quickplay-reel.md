> Texte de Monsieur, donné dans Codex (session du matin) le 4 novembre 2026 à 12:20 UTC. Reproduit tel quel ; la suite du projet est racontée dans [../HISTORIQUE.md](../HISTORIQUE.md).

J'ai examiné ton retour.

Le travail initial est utile, mais nous devons maintenant passer de tests sur des objets fictifs à une fonctionnalité réellement intégrée à notre Stremio Web.

Je veux que tu poursuives sur la branche existante `family/quickplay`, sans recommencer le développement depuis zéro.

**Première priorité : raccorder QuickPlay aux véritables données des addons et au lecteur Stremio.**

Pour cela :

1. Utilise les interfaces et structures réellement exposées par notre version de Stremio Web (`meta_details`, résultats des addons, identités des épisodes, `deepLinks.player`, événements et états du lecteur).
2. Construis un adaptateur qui normalise les sources existantes, sans perdre les métadonnées utiles ni les informations d'origine.
3. Corrige le filtrage trop restrictif :
   - Ne limite pas les sources à `public_verified`.
   - Distingue source incompatible, information inconnue et restriction effective.
   - Accepte les sources dont certaines caractéristiques sont inconnues lorsque leur lecture est possible.
   - Utilise les métadonnées et noms de releases comme indices avec un degré de confiance, pas comme preuves absolues.
   - Respecte les règles propres aux trackers privés, notamment les contraintes de ratio et de partage.
   - Ne déclenche pas d'opération supplémentaire non souhaitée pour vérifier une source.
4. Implémente une sélection progressive :
   - Collecte les résultats des addons en parallèle.
   - Dès qu'une source suffisamment bien classée et compatible est disponible, lance-la.
   - Garde une courte fenêtre de collecte configurable si cela améliore sensiblement le choix.
   - N'attends pas systématiquement les addons les plus lents.
5. Branche le moteur au véritable bouton Lecture et aux épisodes de notre interface.
6. Branche le mécanisme de repli aux erreurs réellement détectées du lecteur. Ne considère pas un simple buffering comme un échec.
7. Conserve l'accès manuel à la liste des sources et un moyen de changer de release.
8. Ajoute une préférence VF/VOSTFR/VO configurable ainsi qu'un plafond de qualité par appareil. Distingue les préférences fortes des préférences souples.
9. Teste le parcours de bout en bout avec les addons déjà configurés sur notre installation, notamment TorBox, sans modifier leurs identifiants ni leurs paramètres existants.
10. Active QuickPlay uniquement dans la préproduction au départ, avec un interrupteur permettant de revenir immédiatement au fonctionnement classique.

Je veux un résultat vérifiable : **clic sur un vrai film ou épisode → récupération des sources réelles → sélection → lancement effectif de la vidéo.**

Une fois ce parcours fonctionnel, nous continuerons les priorités restantes : interface Netflix, profils familiaux, lecteur enrichi et recommandations.

Pour l'IA, respecte notre décision d'utiliser Walter Router comme fournisseur partagé. N'intègre pas de modèle fixe ni de second routeur IA. La lecture et QuickPlay doivent rester entièrement fonctionnels sans LLM.

Conserve la production existante, ses sauvegardes et l'isolation des services.

Ne me livre pas simplement davantage de tests fictifs ou un nouveau rapport. Poursuis l'intégration jusqu'à obtenir un parcours fonctionnel, puis présente les tests réellement effectués et les limites restantes.
