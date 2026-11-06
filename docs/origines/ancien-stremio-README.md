# Stremio

Serveur officiel Stremio pour ARM64. Interface : https://web.stremio.com/.
Les ports sont accessibles uniquement sur la VM. Depuis le Mac, ouvrir un tunnel :

    ssh -N -L 11470:127.0.0.1:11470 -L 12470:127.0.0.1:12470 root@w-alter

Dans Stremio Web, régler l’URL du serveur de streaming sur http://127.0.0.1:11470 si nécessaire.

    docker compose up -d
    docker compose logs
    docker compose stop

Le volume Docker stremio_stremio-data conserve les réglages et les données du serveur.
