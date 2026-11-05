#!/bin/sh
# Renders PNG icons and favicon.ico from the SVGs with headless Chrome (no extra installs).
# Usage: brand/logo/render.sh <scratch-dir>
set -eu
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WORK="$1"

render() { # src size out
  printf '<html><body style="margin:0"><img src="%s" width="%s" height="%s"></body></html>' \
    "$PWD/$1" "$2" "$2" > "$WORK/page.html"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --default-background-color=00000000 --window-size="$2,$2" \
    --screenshot="$3" "file://$WORK/page.html" >/dev/null 2>&1
  echo "wrote $3"
}

render favicon.svg 16 "$PWD/favicon-16.png"
render favicon.svg 32 "$PWD/favicon-32.png"
render favicon.svg 48 "$WORK/favicon-48.png"
render crest.svg 180 "$PWD/apple-touch-icon.png"
render crest.svg 512 "$PWD/icon-512.png"
python3 -I make_ico.py favicon.ico favicon-16.png favicon-32.png "$WORK/favicon-48.png"
