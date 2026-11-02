#!/bin/bash
# Script de execução e publicação diária da Bancada Comentada
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "=== Executando rotina diária em $(date) ==="
python3 scripts/rotina_diaria_completa.py

echo "=== Sincronizando alterações com o GitHub ==="
git add data/ index.html
if ! git diff --quiet || ! git diff --staged --quiet; then
  git commit -m "chore(auto): edicao diaria da Bancada Comentada [$(date +'%Y-%m-%d')] [skip ci]"
  git push origin main
  echo "✅ Publicado com sucesso no GitHub Pages!"
else
  echo "ℹ️ Sem alterações para commitar."
fi
