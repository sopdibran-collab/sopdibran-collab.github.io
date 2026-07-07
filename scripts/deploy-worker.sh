#!/usr/bin/env bash
# Déploie le Worker de redirections 301 sur Cloudflare.
# Prérequis : zone sopjanitech.ch sur Cloudflare + proxy DNS activé (nuage orange).
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  echo "Erreur : définissez CLOUDFLARE_API_TOKEN ou lancez « npx wrangler login »."
  exit 1
fi

npx wrangler deploy
