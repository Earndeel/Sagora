# Audit du projet Stremio familial

État au 4 novembre 2026. Analyse des sources disponibles et de l'installation existante. Les capacités annoncées par les projets ne remplacent pas un essai avec les comptes et appareils de la famille.

## Décision proposée

Conserver Stremio Web comme installation de référence. Examiner d'abord les profils officiels Supporters sur notre déploiement, puis essayer AIOStreams séparément comme agrégateur et comme application, sur des sources de démonstration autorisées. Sa propre application est le chemin le plus court à évaluer pour une expérience familiale avec profils et choix automatique déjà intégrés. Elle ne garantit cependant pas la continuité complète des comptes, bibliothèques et historiques Stremio. Si cette continuité est indispensable, garder le frontend officiel et ajouter progressivement une orchestration de lecture limitée et désactivable, alimentée par AIOStreams. Aucun remplacement en production n'est justifié avant les essais.

DX.BI n'a pas été installé : c'est une application ou une extension prévue pour Stremio Enhanced, pas un addon Stremio ordinaire. Son intégration complète modifierait sensiblement le client et peut interagir avec les addons et les identifiants. Elle nécessite un essai isolé et un examen de sécurité avant toute activation familiale.

## État existant

Le site officiel adapté est servi à https://stremio.walter-ai.cloud/ depuis `/apps/stremio/web` ; son fond noir est en place. La connexion et la synchronisation ont été confirmées par l'utilisateur. La lecture TorBox fonctionne ; d'autres sources affichent « Video is not supported » aussi sur Stremio Web officiel. Ce problème a été reporté et la compatibilité dépend notamment du format et du lecteur. Une base `stremio_app` séparée existe sur PostgreSQL, avec sauvegarde et essai de restauration local. La sauvegarde distante n'a pas été vérifiée par une restauration.

Révisions auditées : Stremio Web local `325de9b0b3bcd8736826c6aedc813e26a24c7139` ; [Stremio Enhanced 1.2.0](https://github.com/REVENGE977/stremio-enhanced/tree/ea64b250929f48b4cf26b8ea05180083d664b7fb) ; [AIOStreams 2.37.0](https://github.com/Viren070/AIOStreams/tree/49cc6fa39af54a5bdb244d897cdf6008a7ebb594) ; [DX.BI 2.30.0](https://github.com/notdxbi/dxbi-stremio/tree/3190de1c3a78125b70d1ba375a6bc2ba6c9adf71). Les projets évoluent rapidement ; les observations de code concernent ces révisions.

## Profils : ne pas reconstruire l'existant

| Solution | Apport | Limites à vérifier |
|---|---|---|
| Profils Stremio Supporters | Solution officielle payante, profils et PIN ; gestion annoncée sur Web et prise en charge Android TV. Stremio annonce aussi des catalogues enfants. | L'article officiel qualifie ces fonctions d'expérimentales. Tester notre build précis, l'isolation réelle des historiques, bibliothèques, recommandations, réglages et restrictions enfants, et le passage entre appareils. Le code source local ne montre pas clairement de sélecteur natif ; cela ne suffit pas à conclure qu'il est absent à l'exécution. |
| Comptes Stremio gratuits distincts | Chaque personne conserve son compte, sa bibliothèque et son historique synchronisés par Stremio. Aucun abonnement imposé. | Le changement simple de compte sur un appareil partagé et la gestion familiale ne sont pas acquis. Un sélecteur maison doit gérer les sessions sans exposer ni conserver imprudemment les identifiants ; il ne se réplique pas automatiquement dans l'application Android TV officielle. Restrictions enfants à vérifier. |
| Profils AIOStreams | Profils familiaux avec historiques distincts ou partagés, PIN facultatif et variantes de filtres. | Ce sont des profils AIOStreams distincts des profils natifs Stremio. La synchronisation d'historique avec Stremio dépend d'un addon de suivi compatible ; elle n'est pas acquise pour tous les appareils. Un PIN ne prouve pas une protection parentale complète. |
| Profils DX.BI | L'application propose sa propre expérience de profils. | Ne pas les assimiler aux profils officiels Stremio ni supposer une séparation complète des comptes. La synchronisation optionnelle de profils fait intervenir un service tiers et la clé de connexion Stremio pour vérification, selon le projet. |

Sources : [Stremio Supporters](https://blog.stremio.com/stremio-supporters-a-way-to-sustain-our-development/), [profils et synchronisation AIOStreams](https://docs.aiostreams.viren070.me/apps/media-server/), [DX.BI](https://github.com/notdxbi/dxbi-stremio/tree/3190de1c3a78125b70d1ba375a6bc2ba6c9adf71).

Les préférences audio, sous-titres, qualité et appareil doivent être vérifiées séparément : leur présence dans un produit ne prouve pas leur isolation par profil et par appareil, ni leur synchronisation sur toutes les plateformes. Pour les enfants, tester l'application effective des restrictions sur les catalogues, la recherche, les liens directs et les changements de profil ; ne pas promettre un contrôle parental robuste sur la seule présence d'un PIN.

## AIOStreams : ce qui existe et ce qui manque

AIOStreams est à la fois un addon d'agrégation et, dans cette version, une application et un serveur compatibles avec des clients Jellyfin. Les addons doivent être configurés ou importés dans AIOStreams : il ne faut pas supposer qu'il récupère automatiquement tous les addons de chaque compte Stremio. Son moteur analyse les métadonnées, propose filtres, classement pondéré, groupes et variantes, et déduplique des résultats. Il traite notamment titre, année, saison/épisode, langue, qualité, codec, HDR, taille, débit et disponibilité lorsque les informations sont disponibles. Ce sont souvent des informations déclaratives ou déduites des noms : elles ne prouvent pas le contenu réel du fichier.

Dans l'application Web AIOStreams, le code du [sélecteur de versions](https://github.com/Viren070/AIOStreams/blob/49cc6fa39af54a5bdb244d897cdf6008a7ebb594/packages/web/src/components/version-picker.tsx) choisit une version mémorisée ou la première version renvoyée. Cette présélection et les mécanismes de reprise existants ne démontrent pas qu'après une erreur de lecture le client essaie automatiquement la source distincte suivante, avec limite de tentatives. Le repli entre services de téléchargement et le repli entre vidéos lisibles sont deux comportements différents. Les modes « qualité seulement » et « expert » restent à valider sur chaque client.

Le moteur est une base solide pour filtrer et classer, mais une lecture fiable en un clic demande une couche complémentaire ou une validation pratique pour :

1. Associer strictement le film ou l'épisode et rejeter les métadonnées insuffisantes lorsqu'elles sont nécessaires ; éviter de confondre une saison complète et l'épisode demandé.
2. Vérifier les contraintes absolues, l'origine autorisée, le transport et les capacités de l'appareil avant de classer. Une capacité ou langue inconnue n'est pas une garantie de compatibilité.
3. Classer selon la langue et les sous-titres souhaités, la qualité utile, HDR/Dolby Vision, codecs, débit, taille, cache et fiabilité. Une version 1080p compatible peut primer sur une 4K incompatible.
4. Tenter un nombre borné de sources distinctes, sans boucle, puis montrer un choix clair. Garder les modes automatique, qualité et expert ; les choix manuels ne peuvent jamais assouplir les interdictions strictes.
5. Mesurer les résultats et apprendre éventuellement les préférences avec transparence, par profil et par appareil, sans transmettre de secrets ni de données de visionnage inutilement.

La récupération de métadonnées techniques ou le sondage d'un média peuvent eux-mêmes provoquer des accès réseau : les désactiver ou vérifier explicitement leur chemin et leur effet avant utilisation. Un résultat indiqué « en cache » n'est pas une garantie de lecture ou d'autorisation.

Références : [filtres](https://github.com/Viren070/AIOStreams/blob/49cc6fa39af54a5bdb244d897cdf6008a7ebb594/packages/core/src/streams/filterer.ts), [classement](https://github.com/Viren070/AIOStreams/blob/49cc6fa39af54a5bdb244d897cdf6008a7ebb594/packages/core/src/streams/sorter.ts), [déduplication](https://github.com/Viren070/AIOStreams/blob/49cc6fa39af54a5bdb244d897cdf6008a7ebb594/packages/core/src/streams/deduplicator.ts), [classement pondéré](https://docs.aiostreams.viren070.me/guides/scored-sorting/), [variantes et groupes](https://docs.aiostreams.viren070.me/guides/groups/).

## Comparaison des architectures

| Stratégie | Points forts | Coût et risques |
|---|---|---|
| 1. Stremio Web existant + extension ciblée + addon AIOStreams | Préserve le site actuel et la synchronisation Stremio ; limite les changements ; solution modulaire. Les profils officiels restent la priorité. | L'addon classe les sources mais ne contrôle pas à lui seul toute l'expérience du lecteur officiel. Sélection en un clic, adaptation par appareil et repli borné demandent intégration et tests. L'extension d'Enhanced est liée à son environnement Electron et ne se branche pas directement sur notre site. |
| 2. Réutiliser des composants AIOStreams | Peut réutiliser davantage de filtres, de logique et d'interface. | Fort couplage possible, maintenance des mises à jour et licence AGPL ; les éléments UI ne deviennent pas automatiquement compatibles avec Stremio Web et ses sessions. Évaluer une interface de service séparée avant toute copie de code. |
| 3. Application AIOStreams comme fondation | Présente déjà profils familiaux, agrégation et sélection d'une version ; candidat le plus rapide à tester pour le parcours global. Application Web et clients annoncés pour plusieurs plateformes. | Historiques et comptes distincts de Stremio ; intégration de suivi à confirmer ; fonctionnalités et ergonomie variables selon client ; lien direct nécessaire et pas de transcodage. Remplacement actuel prématuré. |

Stremio Enhanced charge Stremio Web dans Electron et expose des mécanismes privilégiés pour ses extensions : ce n'est pas un SDK de navigateur interchangeable. DX.BI dépend de cet environnement et inclut des opérations sensibles sur les addons ; ne pas injecter son script complet dans notre domaine de production. Sources : [Enhanced](https://github.com/REVENGE977/stremio-enhanced/tree/ea64b250929f48b4cf26b8ea05180083d664b7fb), [DX.BI](https://github.com/notdxbi/dxbi-stremio/tree/3190de1c3a78125b70d1ba375a6bc2ba6c9adf71).

## Appareils et infrastructure

- **ARM64 :** l'image AIOStreams publiée annonce `linux/arm64`, vérifié dans son manifeste. Cela ne prouve ni performance ni consommation sur notre VM ; mesurer CPU, RAM, stockage et accès concurrents avant service familial.
- **iPad :** tester Safari/PWA et le passage vers un lecteur externe tel que VLC ou Outplayer, notamment interaction utilisateur, retour de progression, sous-titres, codec et authentification du lien. Le lancement réellement automatique n'est pas garanti par les navigateurs. [Instructions Stremio iOS](https://blog.stremio.com/using-stremio-web-on-iphone-ipad/).
- **Android TV :** tester le client officiel avec profils Supporters et les clients AIOStreams disponibles, télécommande comprise. Un comportement du navigateur Web ne garantit pas le même parcours sur TV.
- **PostgreSQL :** AIOStreams prend en charge PostgreSQL mais utilise SQLite par défaut. Si un service persistant est retenu, mutualiser l'instance existante avec une base et un rôle dédiés, droits et accès réseau limités, sauvegarde et restauration testées ; tenir compte de la règle d'authentification existante. Placer les secrets dans un fichier d'environnement protégé et vérifier que les URL de connexion ne sont jamais journalisées. Ne pas exposer PostgreSQL publiquement. [Configuration AIOStreams](https://github.com/Viren070/AIOStreams/blob/49cc6fa39af54a5bdb244d897cdf6008a7ebb594/packages/docs/content/docs/configuration/environment-variables.mdx).
- Conserver les politiques de sortie réseau existantes. Les médias doivent être lus directement par l'appareil ou le lecteur autorisé, sans transit vidéo par le tunnel Cloudflare ; vérifier les redirections et le chemin réseau réel avant toute mise en service.

## Trackers privés : blocage par défaut

Interdire la sélection automatique de toute source privée ou d'origine inconnue tant que les règles applicables, les effets sur le compte et la conformité du partage/ratio ne sont pas établis. Cette règle s'applique aussi aux sources indiquées en cache. Ne pas ajouter automatiquement un torrent privé ni tenter de contourner ses règles ; aucune falsification du ratio.

Le blocage doit intervenir en amont, au niveau des connecteurs et des recherches elles-mêmes, pas seulement au clic : AIOStreams peut récupérer des fichiers `.torrent` pour résoudre certains hash et leurs URL peuvent contenir une passkey. Éviter l'exposition de passkeys dans URL, journaux et diagnostic ; masquer les secrets. AIOStreams ne sème pas lui-même et le lancement d'un résultat non en cache peut déclencher un téléchargement chez le fournisseur ; ses protections ne démontrent pas à elles seules le respect de toutes les règles d'un tracker. [Documentation trackers privés](https://docs.aiostreams.viren070.me/guides/private-trackers/).

## Licences

Les métadonnées locales de Stremio Web indiquent GPL-2.0 ; vérifier auprès des titulaires si une option « version ultérieure » s'applique effectivement avant une combinaison de code. Enhanced est MIT ; AIOStreams est AGPL-3.0 uniquement ; la version actuelle de DX.BI indique GPL-3.0 ou ultérieure. MIT peut généralement être réutilisée sous les conditions de sa licence ; en revanche, une œuvre combinant du GPL-2.0-only avec du code GPL-3+/AGPL-3 pose normalement une incompatibilité. Une communication entre services séparés n'établit pas à elle seule la qualification juridique. Vérifier les obligations de distribution, de fourniture des sources et, pour l'AGPL, d'accès par réseau, ainsi que les dépendances et marques, avant intégration ou publication. Ce point exige un examen juridique si les composants sont combinés.

## Ordre des essais et critères de décision

1. Tester les profils officiels sur le site familial et Android TV avec un compte disposant de l'option, puis comparer à des comptes gratuits distincts. Vérifier isolation, appareils et enfants.
2. Monter si souhaité une instance AIOStreams isolée, aucun compte personnel ni tracker privé initialement, avec sources libres contrôlées. Comparer l'application et l'addon, sans remplacer le site.
3. Mesurer la qualité du classement et tester chaque étape : mauvais épisode, métadonnées absentes, codecs/HDR incompatibles, audio FR, sous-titres, échec de lecture et nombre d'essais, cache, changement d'appareil. Tester aussi les trois modes et la synchronisation réelle des progrès.
4. Contrôler explicitement que les recherches et lectures respectent les règles réseau et ne transitent pas par Cloudflare. Évaluer les licences et ressources réelles avant toute intégration.
5. Choisir l'application AIOStreams si ses profils et son historique suffisent à la famille ; sinon privilégier l'extension ciblée du site actuel avec addon AIOStreams, après validation de faisabilité. Maintenir le frontend actuel et un retour arrière tant que les essais ne sont pas concluants.

## Démonstration fournie

`stremio-selection-demo.py` est une simulation locale autonome, désactivée par défaut, qui ne contacte aucun service. Elle ne modifie pas Stremio et n'est pas un lecteur. Elle illustre un filtrage strict sur des données fictives, l'exclusion des sources privées/inconnues, la préférence pour une qualité compatible et jusqu'à trois tentatives simulées. Elle ne couvre pas encore les modes d'interface, les appareils réels ni la totalité des critères demandés. `test_stremio_selection_demo.py` vérifie ces propriétés sur des exemples fictifs.
