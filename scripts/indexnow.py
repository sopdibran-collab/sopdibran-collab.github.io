#!/usr/bin/env python3
"""Publie les URL du sitemap de production vers IndexNow.

La clé est lue dans le fichier commité à la racine. Aucun secret GitHub.

Clé canonique : 4e83fba7d06a413e96b4abe69b2f5256
(même clé que le site gzimmo, fichier servi en HTTPS à la racine).
2a4c1f14188cf21440b6fdbad88d7e38.txt est conservé et n'est pas utilisé ici.

Usage :
  python3 scripts/indexnow.py
  python3 scripts/indexnow.py --dry-run
  python3 scripts/indexnow.py --dry-run --robots-file scripts/fixtures/robots_sopjanitech_live.txt
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HOST = "sopjanitech.ch"
# Fichier clé IndexNow. Le contenu doit être exactement le nom (sans .txt).
CANONICAL_KEY_FILE = "4e83fba7d06a413e96b4abe69b2f5256.txt"
# Autre fichier de vérification, conservé (Search Console ou ancienne clé).
KEPT_KEY_FILE = "2a4c1f14188cf21440b6fdbad88d7e38.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH_SIZE = 10_000
USER_AGENT = "SopjaniTech-IndexNow/1.0"
KEY_RE = re.compile(r"^[a-zA-Z0-9-]{8,128}$")
LOC_RE = re.compile(r"<loc>\s*([^<]+?)\s*</loc>")

# GitHub Pages met souvent un cache d'environ 10 minutes sur robots.txt.
ROBOTS_POLL_ATTEMPTS = 40
ROBOTS_POLL_SECONDS = 15


def key_from_filename(filename: str) -> str:
    if not filename.endswith(".txt"):
        raise ValueError(f"Nom de fichier clé inattendu : {filename}")
    return filename[: -len(".txt")]


def load_canonical_key() -> str:
    path = ROOT / CANONICAL_KEY_FILE
    expected = key_from_filename(CANONICAL_KEY_FILE)
    if not path.is_file():
        print(f"ERREUR : fichier clé manquant : {CANONICAL_KEY_FILE}", file=sys.stderr)
        sys.exit(1)
    body = path.read_text(encoding="utf-8").strip().lstrip("\ufeff")
    if body != expected or not KEY_RE.fullmatch(body):
        print(
            f"ERREUR : {CANONICAL_KEY_FILE} doit contenir exactement la clé "
            f"({expected}).",
            file=sys.stderr,
        )
        sys.exit(1)
    return body


# Groupes robots.txt pris en compte pour IndexNow (Bing / User-agent: *).
INDEXNOW_USER_AGENTS = frozenset({"*", "bingbot"})


def parse_robots_groups(
    robots_text: str,
) -> list[tuple[list[str], list[tuple[str, str]]]]:
    """Découpe robots.txt en groupes (user-agents, directives field/value)."""
    groups: list[tuple[list[str], list[tuple[str, str]]]] = []
    agents: list[str] = []
    directives: list[tuple[str, str]] = []

    def flush() -> None:
        nonlocal agents, directives
        if agents:
            groups.append((agents, directives))
        agents = []
        directives = []

    for raw in robots_text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, _, value = line.partition(":")
        field = field.strip().lower()
        value = value.strip()
        if field == "user-agent":
            if agents and directives:
                flush()
            agents.append(value)
        elif agents:
            directives.append((field, value))
    flush()
    return groups


def _group_targets_indexnow(agents: list[str]) -> bool:
    for agent in agents:
        lowered = agent.strip().lower()
        if lowered in INDEXNOW_USER_AGENTS:
            return True
    return False


def disallow_rules_for_indexnow(robots_text: str) -> list[str]:
    """Règles Disallow des groupes * et Bingbot uniquement (ignore robots IA)."""
    rules: list[str] = []
    for agents, directives in parse_robots_groups(robots_text):
        if not _group_targets_indexnow(agents):
            continue
        for field, value in directives:
            if field == "disallow" and value:
                rules.append(value)
    return rules


def path_is_disallowed(pathname: str, rules: list[str]) -> bool:
    for rule in rules:
        if rule.endswith("/"):
            if pathname.startswith(rule):
                return True
        elif pathname == rule:
            return True
    return False


def assert_local_robots_allows_verification_files() -> list[str]:
    robots_path = ROOT / "robots.txt"
    text = robots_path.read_text(encoding="utf-8")
    rules = disallow_rules_for_indexnow(text)
    blocked = [
        name
        for name in (CANONICAL_KEY_FILE, KEPT_KEY_FILE)
        if path_is_disallowed(f"/{name}", rules)
    ]
    if blocked:
        print(
            "ERREUR : robots.txt interdit encore "
            + ", ".join(f"/{name}" for name in blocked),
            file=sys.stderr,
        )
        sys.exit(1)
    return rules


def decode_xml(value: str) -> str:
    return (
        value.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&apos;", "'")
    )


def accept_loc(loc: str, key: str, rules: list[str]) -> str | None:
    trimmed = decode_xml(loc).strip()
    try:
        url = urlparse(trimmed)
    except ValueError:
        return None
    if url.scheme != "https" or url.hostname != HOST:
        return None
    if url.username or url.password or url.query or url.fragment:
        return None
    if url.path == f"/{key}.txt":
        return None
    if path_is_disallowed(url.path, rules):
        return None
    return trimmed


def parse_sitemap_locs(xml: str, key: str, rules: list[str]) -> list[str]:
    if "<sitemapindex" in xml and "<urlset" not in xml:
        print("ERREUR : sitemap index non géré.", file=sys.stderr)
        sys.exit(1)
    locs: list[str] = []
    seen: set[str] = set()
    for match in LOC_RE.finditer(xml):
        accepted = accept_loc(match.group(1), key, rules)
        if not accepted or accepted in seen:
            continue
        seen.add(accepted)
        locs.append(accepted)
    return locs


class FetchError(Exception):
    pass


def http_get(url: str) -> tuple[int, str, dict[str, str]]:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/xml, text/plain, text/xml, */*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
            headers = {k.lower(): v for k, v in response.headers.items()}
            return response.status, body, headers
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        headers = {k.lower(): v for k, v in error.headers.items()} if error.headers else {}
        return error.code, body, headers
    except urllib.error.URLError as error:
        raise FetchError(f"Impossible de joindre {url} : {error.reason}") from error


def looks_like_challenge(status: int, body: str) -> bool:
    sample = body.lstrip()[:400].lower()
    if status == 403 and ("just a moment" in sample or "cf-challenge" in sample or sample.startswith("<!doctype html") or sample.startswith("<html")):
        return True
    if status == 200 and "just a moment" in sample and sample.startswith("<"):
        return True
    return False


def fetch_text(url: str, *, attempts: int = 4) -> tuple[str, dict[str, str]]:
    last_error = f"{url} inaccessible"
    for attempt in range(1, attempts + 1):
        try:
            status, body, headers = http_get(url)
        except FetchError as error:
            last_error = str(error)
            print(f"{last_error} (tentative {attempt}/{attempts})")
            if attempt < attempts:
                time.sleep(attempt * 2)
            continue
        if status == 200 and not looks_like_challenge(status, body):
            return body, headers
        last_error = f"{url} → HTTP {status}"
        if looks_like_challenge(status, body):
            last_error += " (challenge Cloudflare)"
        print(f"{last_error} (tentative {attempt}/{attempts})")
        if attempt < attempts and (status in (403, 429) or status >= 500 or looks_like_challenge(status, body)):
            time.sleep(attempt * 2)
            continue
        break
    raise FetchError(last_error)


def assert_key_online(key: str) -> None:
    url = f"https://{HOST}/{key}.txt"
    try:
        body, headers = fetch_text(url)
    except FetchError as error:
        print(f"ERREUR : {error}", file=sys.stderr)
        sys.exit(1)
    if body.strip() != key:
        print(f"ERREUR : le fichier clé en ligne ne contient pas la clé ({url}).", file=sys.stderr)
        sys.exit(1)
    tag = headers.get("x-robots-tag", "")
    if tag:
        print(f"Fichier clé en ligne OK ({url}), X-Robots-Tag: {tag}")
    else:
        print(f"Fichier clé en ligne OK ({url})")


def live_robots_blocks_key(key: str) -> bool | None:
    """True si Disallow vise la clé, False si elle est autorisée, None si illisible."""
    url = f"https://{HOST}/robots.txt"
    try:
        body, _headers = fetch_text(url, attempts=2)
    except FetchError as error:
        print(f"robots.txt en ligne illisible : {error}")
        return None
    return path_is_disallowed(f"/{key}.txt", disallow_rules_for_indexnow(body))


def wait_until_live_robots_allows_key(key: str) -> None:
    for attempt in range(1, ROBOTS_POLL_ATTEMPTS + 1):
        blocked = live_robots_blocks_key(key)
        if blocked is False:
            print("robots.txt en ligne autorise le fichier clé.")
            return
        if blocked is True:
            print(
                f"Tentative {attempt}/{ROBOTS_POLL_ATTEMPTS} — "
                "robots.txt en ligne interdit encore le fichier clé."
            )
        else:
            print(
                f"Tentative {attempt}/{ROBOTS_POLL_ATTEMPTS} — "
                "nouvel essai de lecture de robots.txt."
            )
        if attempt < ROBOTS_POLL_ATTEMPTS:
            time.sleep(ROBOTS_POLL_SECONDS)
    print(
        "ERREUR : robots.txt en ligne interdit encore le fichier clé. "
        "Relancer le workflow IndexNow à la main une fois le fichier à jour.",
        file=sys.stderr,
    )
    sys.exit(1)


def load_url_list(key: str, rules: list[str]) -> list[str]:
    sitemap_url = f"https://{HOST}/sitemap.xml"
    try:
        xml, _headers = fetch_text(sitemap_url)
        source = sitemap_url
    except FetchError as error:
        local = ROOT / "sitemap.xml"
        print(
            f"Sitemap en ligne indisponible ({error}). "
            f"Utilisation de {local.name} du commit déployé."
        )
        if not local.is_file():
            print("ERREUR : sitemap.xml local manquant.", file=sys.stderr)
            sys.exit(1)
        xml = local.read_text(encoding="utf-8")
        source = str(local)
    urls = parse_sitemap_locs(xml, key, rules)
    if not urls:
        print(f"ERREUR : aucune URL publiable dans {source}", file=sys.stderr)
        sys.exit(1)
    print(f"IndexNow → {len(urls)} URL(s) depuis {source}")
    return urls


def submit_batch(key: str, url_list: list[str]) -> None:
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"https://{HOST}/{key}.txt",
        "urlList": url_list,
    }
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(1, 5):
        request = urllib.request.Request(
            ENDPOINT,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
                text = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as error:
            status = error.code
            text = error.read().decode("utf-8", errors="replace")
            retryable = status == 429 or status >= 500
            print(f"HTTP {status} ({len(url_list)} URL)")
            if text.strip():
                print(text.strip())
            if retryable and attempt < 4:
                wait_s = attempt * 2
                if error.headers:
                    retry_after = error.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit() and int(retry_after) > 0:
                        wait_s = int(retry_after)
                print(f"Nouvel essai dans {wait_s} s…")
                time.sleep(wait_s)
                continue
            sys.exit(1)
        except urllib.error.URLError as error:
            print(f"Impossible de contacter IndexNow : {error.reason}", file=sys.stderr)
            if attempt < 4:
                time.sleep(attempt * 2)
                continue
            sys.exit(1)

        print(f"HTTP {status} ({len(url_list)} URL)")
        if text.strip():
            print(text.strip())
        if status in (200, 202):
            return
        print(f"ERREUR : réponse inattendue HTTP {status}", file=sys.stderr)
        sys.exit(1)


def print_robots_audit(key: str, rules: list[str], *, label: str) -> None:
    key_path = f"/{key}.txt"
    print(f"Audit robots ({label}) — {len(rules)} règle(s) Disallow (* / Bingbot)")
    samples = [
        ("fichier clé", key_path),
        ("accueil", "/"),
        ("/AGENTS.md", "/AGENTS.md"),
    ]
    for name, path in samples:
        status = "interdit" if path_is_disallowed(path, rules) else "autorisé"
        print(f"  {name}: {status}")


def main(argv: list[str]) -> None:
    dry_run = "--dry-run" in argv
    robots_file: Path | None = None
    if "--robots-file" in argv:
        idx = argv.index("--robots-file")
        if idx + 1 >= len(argv):
            print(
                "Utilisation : python3 scripts/indexnow.py [--dry-run] "
                "[--robots-file CHEMIN]",
                file=sys.stderr,
            )
            sys.exit(1)
        robots_file = Path(argv[idx + 1])
        argv = argv[:idx] + argv[idx + 2 :]
    allowed = [[], ["--dry-run"]]
    if argv not in allowed:
        print(
            "Utilisation : python3 scripts/indexnow.py [--dry-run] "
            "[--robots-file CHEMIN]",
            file=sys.stderr,
        )
        sys.exit(1)

    key = load_canonical_key()
    rules = assert_local_robots_allows_verification_files()
    print(f"Clé lue dans {CANONICAL_KEY_FILE}")
    print(f"keyLocation: https://{HOST}/{key}.txt")
    print(f"{KEPT_KEY_FILE} conservé, non utilisé pour la soumission.")

    if robots_file is not None:
        if not robots_file.is_file():
            print(f"ERREUR : fichier robots introuvable : {robots_file}", file=sys.stderr)
            sys.exit(1)
        fixture_rules = disallow_rules_for_indexnow(
            robots_file.read_text(encoding="utf-8")
        )
        print_robots_audit(key, fixture_rules, label=str(robots_file))
        if path_is_disallowed(f"/{key}.txt", fixture_rules):
            print(
                "ERREUR : le robots fourni interdit encore le fichier clé.",
                file=sys.stderr,
            )
            sys.exit(1)

    assert_key_online(key)
    if dry_run:
        if robots_file is not None:
            print("Dry-run (fixture) : robots en ligne non vérifié pour la clé.")
        else:
            blocked = live_robots_blocks_key(key)
            if blocked is True:
                print(
                    "AVERTISSEMENT : robots.txt en ligne interdit encore le fichier clé. "
                    "Un envoi réel attendra que cette règle disparaisse."
                )
            elif blocked is False:
                print("robots.txt en ligne autorise le fichier clé.")
    else:
        wait_until_live_robots_allows_key(key)

    urls = load_url_list(key, rules)
    for url in urls:
        print(url)

    if dry_run:
        print("Dry-run : aucune requête envoyée à IndexNow.")
        return

    for offset in range(0, len(urls), BATCH_SIZE):
        submit_batch(key, urls[offset : offset + BATCH_SIZE])


if __name__ == "__main__":
    main(sys.argv[1:])
