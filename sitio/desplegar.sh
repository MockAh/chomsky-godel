#!/usr/bin/env bash
# Publicar es desplegar: solo con aprobación del admin (spec 04 §5).
#   sitio/desplegar.sh construir   arma la lista cerrada y construye la imagen; no publica
#   sitio/desplegar.sh publicar    pone en línea la imagen del commit actual
# Todos los comandos llevan --project: el gcloud del estudiante tiene activo otro proyecto (P-26).
set -euo pipefail
cd "$(dirname "$0")/.."
PROYECTO=chomsky-godel; REGION=us-central1; SERVICIO=sitio
ETIQUETA=$(git rev-parse --short HEAD)
IMAGEN=$REGION-docker.pkg.dev/$PROYECTO/sitio/sitio:$ETIQUETA
case "${1:-}" in
  construir)
    sitio/.venv/bin/python sitio/armar_imagen.py build/sitio-imagen
    gcloud builds submit build/sitio-imagen --project="$PROYECTO" --region="$REGION" \
      --config=build/sitio-imagen/cloudbuild.yaml --substitutions=_ETIQUETA="$ETIQUETA" ;;
  publicar)
    gcloud artifacts docker images describe "$IMAGEN" --project="$PROYECTO" >/dev/null \
      || { echo "No existe la imagen $ETIQUETA: corre primero «construir»." >&2; exit 1; }
    gcloud run deploy "$SERVICIO" --project="$PROYECTO" --region="$REGION" --image="$IMAGEN" \
      --service-account="sitio-run@$PROYECTO.iam.gserviceaccount.com" \
      --allow-unauthenticated --min-instances=0 --max-instances=2 \
      --cpu=1 --memory=512Mi --concurrency=20 ;;
  *) echo "Uso: $0 construir|publicar" >&2; exit 2 ;;
esac
