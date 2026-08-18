#!/usr/bin/env python3

import os
import sys
import urllib.parse
import urllib.request
import urllib.error


INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
SITE_HOST = "sopjanitech.ch"


def submit_url(url: str) -> None:
    key = os.environ.get("INDEXNOW_KEY")

    if not key:
        print("ERREUR : la variable INDEXNOW_KEY n'est pas définie.")
        sys.exit(1)

    parsed = urllib.parse.urlparse(url)

    if parsed.scheme != "https" or parsed.netloc != SITE_HOST:
        print(f"ERREUR : URL non autorisée : {url}")
        print(f"L'URL doit appartenir à https://{SITE_HOST}")
        sys.exit(1)

    params = urllib.parse.urlencode({
        "url": url,
        "key": key,
    })

    request_url = f"{INDEXNOW_ENDPOINT}?{params}"

    request = urllib.request.Request(
        request_url,
        method="GET",
        headers={
            "User-Agent": "SopjaniTech-IndexNow/1.0"
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status

            print(f"IndexNow HTTP {status}")

            if status in (200, 202):
                print(f"URL envoyée avec succès : {url}")
            else:
                print(f"Réponse inattendue : HTTP {status}")

    except urllib.error.HTTPError as error:
        print(f"IndexNow HTTP {error.code}")

        if error.code == 403:
            print("Clé IndexNow invalide ou fichier de clé inaccessible.")
        elif error.code == 422:
            print("Requête invalide.")
        elif error.code == 429:
            print("Trop de requêtes. Réessayer plus tard.")
        else:
            print(f"Réponse du serveur : {error.reason}")

        sys.exit(1)

    except urllib.error.URLError as error:
        print(f"Impossible de contacter IndexNow : {error.reason}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilisation :")
        print("  python3 scripts/indexnow.py https://sopjanitech.ch/")
        sys.exit(1)

    submit_url(sys.argv[1])