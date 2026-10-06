#!/bin/sh
set -eu

DATA_DIR="${VISUAL_AI_DATA_DIR:-/data}"
BACKUP_DIR="${VISUAL_AI_BACKUP_DIR:-/backups}"
KEEP_DAYS="${VISUAL_AI_BACKUP_KEEP_DAYS:-14}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVE="$BACKUP_DIR/ia-art-studio-pro-$STAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

if [ ! -d "$DATA_DIR" ]; then
  echo "Data directory not found: $DATA_DIR" >&2
  exit 1
fi

tar -C "$DATA_DIR" -czf "$ARCHIVE" .

find "$BACKUP_DIR" -type f -name 'ia-art-studio-pro-*.tar.gz' -mtime "+$KEEP_DAYS" -delete

echo "$ARCHIVE"
