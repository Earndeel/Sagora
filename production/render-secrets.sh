#!/bin/sh
# Écrit secrets.env (0600) à partir de Bitwarden. Aucune valeur n'est affichée.
set -eu
cd "$(dirname "$0")"
umask 077
key=$(walter-secret get 5043a723-0324-4e03-9e01-7a869688acf4 password)
pass=$(walter-secret get 60fd7166-82ec-48e6-ac6d-6e6c25fd7805 password)
# « sagora » : compte de service (lecture Usenet par le moteur intégré), sans droit d'administration.
svc=$(walter-secret get "Sagora · compte de service Usenet" password)
printf "SECRET_KEY='%s'\nAIOSTREAMS_AUTH='walter:%s,sagora:%s'\nAIOSTREAMS_AUTH_PERMISSIONS='walter=admin,sagora=service'\n" "$key" "$pass" "$svc" > secrets.env.tmp
# Connexion « Lucas » (ou « lucas ») + mot de passe Famille = la configuration Famille (2026-11-06). Le mot de passe est
# toujours demandé ; les raccourcis sans mot de passe par alias sont fermés dans front/nginx.conf.
uuid=$(cat data/famille-uuid)
enc=$(walter-secret get "Sagora · alias Lucas (mot de passe chiffré)" password)
printf "ALIASED_CONFIGURATIONS='Lucas:%s:%s,lucas:%s:%s'\n" "$uuid" "$enc" "$uuid" "$enc" >> secrets.env.tmp
mv secrets.env.tmp secrets.env
echo "secrets.env écrit"
# Relais Torznab (2026-11-05) : clé de Prowlarr, dans son propre fichier.
printf "PROWLARR_API_KEY='%s'\nTMDB_API_KEY='%s'\n" "$(walter-secret get "Sagora · Prowlarr API" password)" "$(walter-secret get "AIOStreams · TMDB" password)" > torznab-relay/relay.env.tmp
mv torznab-relay/relay.env.tmp torznab-relay/relay.env
echo "torznab-relay/relay.env écrit"
