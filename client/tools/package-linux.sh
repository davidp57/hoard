#!/usr/bin/env bash
#
# Build a self-contained Linux archive of the client (BL-104).
#
# Why this exists: media_kit's video plugin links libmpv.so.2 with a RUNPATH
# pointing at the machine that compiled it, so on any other host the loader
# falls back to the system libmpv — and refuses to start when there is none.
# SteamOS is read-only and ships no libmpv-dev, so we bundle our own and put
# bundle/lib ahead of the system through a launcher.
#
# LIBMPV_LIBRARY_PATH, which media_kit documents for this, does NOT solve it:
# it is read by Dart code, long after the dynamic linker has already given up.
#
# This is the workaround for testing. The packaging answer for the lot is a
# Flatpak, which puts libmpv on a standard path inside its sandbox.
#
# Usage:  client/tools/package-linux.sh [output-directory]
#         (defaults to the current directory)
set -eu

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CLIENT=$(dirname "$HERE")
BUNDLE="$CLIENT/build/linux/x64/release/bundle"
DEST=$(cd "${1:-$PWD}" && pwd)

[ -d "$BUNDLE" ] || {
  echo "No release bundle. Run: flutter build linux --release" >&2
  exit 1
}

# Stage outside the repository: the tree is ~250 MB and the build directory is
# wiped by every `flutter build`.
STAGE_ROOT=$(mktemp -d)
trap 'rm -rf "$STAGE_ROOT"' EXIT
STAGE="$STAGE_ROOT/hoard-spike"

mkdir -p "$STAGE"
cp -r "$BUNDLE"/. "$STAGE/"

# Ship ONLY what the target does not already have, listed in
# steamos-missing-libs.txt and measured on the device.
#
# The first attempt used a blacklist — bundle libmpv's whole closure, minus a
# few families expected to come from the host. It did not start at all: the
# blacklist excluded libglib/libgio but not their transitive dependencies, so
# SteamOS's libgio-2.0 met a libmount we had shipped from Ubuntu, demanded
# MOUNT_2_40 that it does not provide, and the loader gave up. A blacklist has
# to name every transitive dependency of everything excluded, and missing one
# fails silently. A whitelist cannot fail that way.
WANTED="$HERE/steamos-missing-libs.txt"
[ -f "$WANTED" ] || { echo "missing $WANTED" >&2; exit 1; }

copied=0
missing=""
while read -r name; do
  case "$name" in ''|\#*) continue;; esac
  # Resolve the name against this machine's linker cache.
  src=$(ldconfig -p | awk -v n="$name" '$1 == n {print $NF; exit}')
  if [ -z "$src" ] || [ ! -e "$src" ]; then
    missing="$missing $name"
    continue
  fi
  cp -L "$src" "$STAGE/lib/$name" && copied=$((copied + 1))
done < "$WANTED"

if [ -n "$missing" ]; then
  echo "NOT FOUND on this build machine:$missing" >&2
  echo "install the packages providing them, or the target will fail the same way" >&2
  exit 1
fi

echo "bundled $copied libraries (libmpv included — it is in the list)"

cat > "$STAGE/run.sh" <<'WRAPPER'
#!/usr/bin/env bash
# Launcher for the Hoard feasibility spike.
#
HOARD_URL="https://hoard.dpierron.synology.me"

# ── AND YOUR CREDENTIALS, if the server asks for them (HTTP 401). ────────────
HOARD_USER=""
HOARD_PASS=""
# ─────────────────────────────────────────────────────────────────────────────
# These pre-fill the app, because in Gaming Mode there may be no way to type
# them — which is precisely what we are here to find out. HTTPS only: never
# point HOARD_URL at http://, the password would travel in clear.
#
# They sit in this file in plain text. It is a throwaway test build on your own
# machine, but treat the file accordingly and delete it when you are done.
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
export HOARD_URL HOARD_USER HOARD_PASS
export LD_LIBRARY_PATH="$HERE/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LIBMPV_LIBRARY_PATH="$HERE/lib/libmpv.so.2"
exec "$HERE/hoard_client" "$@"
WRAPPER
chmod +x "$STAGE/run.sh"

tar czf "$DEST/hoard-spike.tar.gz" -C "$STAGE_ROOT" hoard-spike
echo "archive: $DEST/hoard-spike.tar.gz"
du -sh "$DEST/hoard-spike.tar.gz"
