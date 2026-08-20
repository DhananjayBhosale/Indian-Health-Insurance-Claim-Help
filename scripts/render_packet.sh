#!/usr/bin/env bash
set -euo pipefail
umask 077

usage() {
  printf 'Usage: %s INPUT_PDF OUTPUT_DIR\n' "$(basename "$0")" >&2
}

if [ "$#" -ne 2 ]; then
  usage
  exit 2
fi

input_pdf=$1
output_dir=$2

if [ -z "$input_pdf" ] || [ "$input_pdf" = "-" ] || [ ! -f "$input_pdf" ]; then
  printf 'Error: INPUT_PDF must be an explicit, existing file.\n' >&2
  exit 2
fi

if [ -z "$output_dir" ] || [ "$output_dir" = "/" ]; then
  printf 'Error: OUTPUT_DIR must be a non-root directory.\n' >&2
  exit 2
fi

if [ -L "$output_dir" ]; then
  printf 'Error: OUTPUT_DIR must not be a symbolic link.\n' >&2
  exit 2
fi

if [ -n "${HOME:-}" ] && [ "$output_dir" = "$HOME" ]; then
  printf 'Error: refusing to use HOME as OUTPUT_DIR.\n' >&2
  exit 2
fi

for required_command in pdfinfo pdftoppm; do
  if ! command -v "$required_command" >/dev/null 2>&1; then
    printf 'Error: required command is unavailable: %s\n' "$required_command" >&2
    exit 127
  fi
done

mkdir -p -- "$output_dir"
output_dir=$(cd -P -- "$output_dir" && pwd)

if [ "$output_dir" = "/" ]; then
  printf 'Error: refusing to use the filesystem root as OUTPUT_DIR.\n' >&2
  exit 2
fi

if [ -n "${HOME:-}" ]; then
  home_dir=$(cd -P -- "$HOME" && pwd)
  if [ "$output_dir" = "$home_dir" ]; then
    printf 'Error: refusing to use HOME as OUTPUT_DIR.\n' >&2
    exit 2
  fi
fi

if find "$output_dir" -mindepth 1 -maxdepth 1 -print -quit | grep -q .; then
  printf 'Error: OUTPUT_DIR must be empty; choose a new render directory.\n' >&2
  exit 2
fi

chmod 700 "$output_dir"

pdf_metadata=$(pdfinfo "$input_pdf")
pages=$(printf '%s\n' "$pdf_metadata" | awk -F: '$1 == "Pages" { sub(/^[[:space:]]+/, "", $2); print $2; exit }')
page_size=$(printf '%s\n' "$pdf_metadata" | awk -F: '$1 == "Page size" { sub(/^[[:space:]]+/, "", $2); print $2; exit }')
file_size=$(printf '%s\n' "$pdf_metadata" | awk -F: '$1 == "File size" { sub(/^[[:space:]]+/, "", $2); print $2; exit }')
output_prefix="$output_dir/page"

printf 'Pages: %s\n' "${pages:-unknown}"
printf 'Page size: %s\n' "${page_size:-unknown}"
printf 'File size: %s\n' "${file_size:-unknown}"
printf 'Output prefix: %s\n' "$output_prefix"

pdftoppm -png -r 150 "$input_pdf" "$output_prefix"
find "$output_dir" -mindepth 1 -maxdepth 1 -type f -name 'page-*.png' -exec chmod 600 {} +
printf 'Rendered packet pages successfully.\n'
