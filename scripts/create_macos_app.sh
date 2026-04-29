#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="TeatrumDB"
APP_ID="cz.jakubmitrega.teatrumdb"
APP_DIR="$HOME/Applications/${APP_NAME}.app"
DESKTOP_APP="$HOME/Desktop/${APP_NAME}.app"
BUILD_DIR="$ROOT_DIR/build/macos"
ICONSET_DIR="$BUILD_DIR/${APP_NAME}.iconset"
SOURCE_ICON="$BUILD_DIR/icon-source.png"
PROJECT_COPY="$APP_DIR/Contents/Resources/project"

PYTHON_BIN="${PYTHON_BIN:-python3}"

rm -rf "$APP_DIR" "$DESKTOP_APP" "$BUILD_DIR"
mkdir -p "$APP_DIR/Contents/MacOS" "$APP_DIR/Contents/Resources" "$PROJECT_COPY" "$ICONSET_DIR"
mkdir -p "$HOME/Applications"

"$PYTHON_BIN" - "$SOURCE_ICON" <<'PY'
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path


def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> None:
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            row.extend(pixels[y * width + x])
        rows.append(bytes(row))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    raw = b"".join(rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def lerp(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


size = 1024
dark_top = (23, 35, 48)
dark_bottom = (12, 24, 36)
red = (124, 31, 37)
red_dark = (94, 23, 29)
gold = (216, 166, 42)
teal = (47, 143, 131)
white = (244, 247, 249)

pixels: list[tuple[int, int, int, int]] = []
for y in range(size):
    t = y / (size - 1)
    bg = tuple(lerp(dark_top[i], dark_bottom[i], t) for i in range(3))
    for x in range(size):
        color = bg
        if x < 215:
            shade = 0.82 + 0.18 * (x / 214)
            color = tuple(round(c * shade) for c in red)
            if x < 42 or x > 172:
                color = red_dark
        elif 215 <= x < 242:
            color = gold

        # Stage floor.
        if 680 <= y <= 710 and 300 <= x <= 840:
            color = gold
        if 736 <= y <= 754 and 375 <= x <= 765:
            color = teal

        # Simple theatre mask dots.
        for cx, cy, r, mask_color in [
            (470, 405, 92, white),
            (675, 405, 92, white),
            (430, 395, 16, dark_top),
            (510, 395, 16, dark_top),
            (635, 395, 16, dark_top),
            (715, 395, 16, dark_top),
            (470, 465, 30, dark_top),
            (675, 465, 30, dark_top),
        ]:
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                color = mask_color

        pixels.append((*color, 255))

write_png(Path(sys.argv[1]), size, size, pixels)
PY

for item in \
  "16 icon_16x16.png" \
  "32 icon_16x16@2x.png" \
  "32 icon_32x32.png" \
  "64 icon_32x32@2x.png" \
  "128 icon_128x128.png" \
  "256 icon_128x128@2x.png" \
  "256 icon_256x256.png" \
  "512 icon_256x256@2x.png" \
  "512 icon_512x512.png" \
  "1024 icon_512x512@2x.png"
do
  size="${item%% *}"
  name="${item#* }"
  sips -z "$size" "$size" "$SOURCE_ICON" --out "$ICONSET_DIR/$name" >/dev/null
done

iconutil -c icns "$ICONSET_DIR" -o "$APP_DIR/Contents/Resources/${APP_NAME}.icns"

for item in app sql scripts docker images; do
  ditto "$ROOT_DIR/$item" "$PROJECT_COPY/$item"
done
for file in run_app.sh docker-compose.yml .env; do
  ditto "$ROOT_DIR/$file" "$PROJECT_COPY/$file"
done
find "$PROJECT_COPY" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$PROJECT_COPY" -name '*.pyc' -delete
rm -rf "$PROJECT_COPY/build" "$PROJECT_COPY/logs" "$PROJECT_COPY/.venv"
chmod +x "$PROJECT_COPY/run_app.sh" "$PROJECT_COPY"/scripts/*.sh

cat > "$APP_DIR/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>cs</string>
  <key>CFBundleDisplayName</key>
  <string>${APP_NAME}</string>
  <key>CFBundleExecutable</key>
  <string>${APP_NAME}</string>
  <key>CFBundleIconFile</key>
  <string>${APP_NAME}</string>
  <key>CFBundleIdentifier</key>
  <string>${APP_ID}</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>${APP_NAME}</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSMinimumSystemVersion</key>
  <string>10.15</string>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
PLIST

cat > "$APP_DIR/Contents/MacOS/${APP_NAME}" <<'LAUNCHER'
#!/bin/zsh

set -u

APP_EXEC_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_CONTENTS_DIR="$(cd "$APP_EXEC_DIR/.." && pwd)"
PROJECT_DIR="$APP_CONTENTS_DIR/Resources/project"
LOG_DIR="$HOME/Library/Logs/TeatrumDB"
LOG_FILE="$LOG_DIR/teatrumdb-launcher.log"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

if [[ "${1:-}" == "--check" ]]; then
  echo "TeatrumDB launcher OK"
  echo "Project: $PROJECT_DIR"
  echo "Run script: $PROJECT_DIR/run_app.sh"
  /bin/bash -n "$PROJECT_DIR/run_app.sh"
  [[ -f "$PROJECT_DIR/.env" ]] && echo ".env: OK" || echo ".env: chybi"
  command -v docker >/dev/null && docker info >/dev/null 2>&1 && echo "Docker: OK" || echo "Docker: neni dostupny"
  exit 0
fi

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR" || exit 1

/usr/bin/osascript -e 'display notification "Spouštím databázi a aplikaci." with title "TeatrumDB"' >/dev/null 2>&1 || true

{
  echo "============================================================"
  echo "TeatrumDB launch: $(date)"
  echo "Project: $PROJECT_DIR"
  echo "PATH: $PATH"
  echo "============================================================"
} >> "$LOG_FILE"

set +e
/bin/bash "$PROJECT_DIR/run_app.sh" >> "$LOG_FILE" 2>&1
STATUS=$?
set -e

if [[ "$STATUS" -ne 0 ]]; then
  /usr/bin/osascript -e 'display alert "TeatrumDB se nepodařilo spustit" message "Detail je v souboru ~/Library/Logs/TeatrumDB/teatrumdb-launcher.log. Pokud je tam chyba Dockeru, zkontrolujte Docker Desktop." as critical' >/dev/null 2>&1 || true
fi

exit "$STATUS"
LAUNCHER

chmod +x "$APP_DIR/Contents/MacOS/${APP_NAME}"
plutil -lint "$APP_DIR/Contents/Info.plist" >/dev/null

cp -R "$APP_DIR" "$DESKTOP_APP"

echo "Vytvoreno:"
echo "  $APP_DIR"
echo "  $DESKTOP_APP"
