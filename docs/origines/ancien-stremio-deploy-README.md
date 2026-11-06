# Stremio — exploitation

## Frontend

Le frontend officiel est dans `/apps/stremio/web/`, commit local `325de9b0b3bcd8736826c6aedc813e26a24c7139` (fond noir, basé sur l’upstream `55d8b33487e95ab8d67fda3030c7b86dd68f2d99`) ; l'image Nginx est figée par empreinte dans `/apps/stremio/deploy/compose.yaml`. Le conteneur est limité à localhost:18080. Le serveur de streaming existant reste distinct, défini par `/apps/stremio/compose.yaml`, et ses ports ne doivent pas être exposés publiquement.

Le fichier `config/nginx.conf` ajoute une CSP minimale, les protections MIME/referrer et une revalidation des fichiers PWA. La règle Cloudflare `25ad62f4b2214635b9fc333ad9434273` du ruleset `6fd6e32e4b244ead81a85da20b2a4043` applique le cache d'origine aux seuls fichiers d'entrée Stremio ; pour revenir en arrière, supprimer uniquement cette règle après contrôle. Les anciens navigateurs ayant reçu auparavant un cache de 4 h peuvent le conserver jusqu'à son expiration.

Pour actualiser : sauvegarder le dossier `web/build` et noter le commit ; récupérer l'upstream Git et compiler une version contrôlée hors de la VM avec le lockfile, puis vérifier les fichiers et remplacer `web/build` après sauvegarde. Vérifier le frontend, les parcours connectés et le service worker. Retour arrière : remettre l'ancien `web/build` et sa version de source, puis vérifier à nouveau ; les clients PWA peuvent conserver un ancien service worker temporairement. Cette procédure de mise à jour/rollback n'a pas encore été testée en production.

L'URL publique est https://stremio.walter-ai.cloud/ : DNS CNAME proxifié vers le tunnel partagé, ingress vers localhost:18080. Le serveur vidéo et PostgreSQL restent privés. Ne pas modifier globalement CORS pour le serveur vidéo.

Retour arrière de l'accès public : retirer uniquement le CNAME Stremio dans Cloudflare après vérification de son contenu ; pour enlever la route, restaurer `/user/Lucas/backups/changes/cloudflared-before-stremio-20261104.yml` seulement après avoir comparé les autres règles actuelles, puis valider la configuration et effectuer un basculement avec réplique. Les connexions longues du tunnel peuvent être coupées. La configuration candidate `/apps/stremio/config/cloudflared-proposed.yml` est une photographie datée et ne doit pas écraser de futures modifications des autres routes.


## Base PostgreSQL

Base `stremio_app`, rôle `stremio_app`, sans privilèges superuser/CREATEDB/CREATEROLE et sans tables métier. Le mot de passe est dans Bitwarden « Stremio PostgreSQL application ». Les règles de `pg_hba.conf` ciblent ce rôle : connexion SCRAM à sa seule base et rejet des autres ; aucune ACL des bases Walter n'a été modifiée. Le fichier HBA initial est sauvegardé sous `/user/Lucas/backups/changes/stremio-pg-hba-before-20261104.conf`. Toute modification HBA ultérieure doit préserver les règles d'isolation et être validée avant rechargement.

`stremio-pg-backup.timer` lance chaque jour à 04:35 UTC `/apps/stremio/deploy/backup.sh`. Les dumps vérifiés sont sous `/user/Lucas/backups/stremio`, inclus dans le périmètre de dossiers du restic existant ; l'inclusion effective au prochain cycle hors site reste à vérifier. Pas de suppression automatique des dumps : surveiller leur taille. `systemctl start stremio-pg-backup.service` permet une sauvegarde manuelle.

`/apps/stremio/deploy/restore-test.sh <dump>` restaure dans une base temporaire de l'instance de test `walter-memory-testpg` et supprime uniquement cette base temporaire. Premier test réussi. Pour restaurer réellement la production, faire d'abord un nouveau dump et arrêter les clients concernés ; n'exécuter la restauration que dans une base cible explicitement choisie après contrôle du contenu et des droits.

Les futures migrations réversibles vont dans `/apps/stremio/config/migrations/`. Ne pas y stocker les comptes, bibliothèques ou addons officiels de Stremio.

Sauvegarde avant le fond noir : `/user/Lucas/backups/changes/stremio-build-before-black-20261104.tar.gz`. Les fichiers de la version précédente restent disponibles sous leur répertoire versionné.
