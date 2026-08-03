#!/bin/sh
set -eu

DEXCLI_REPOSITORY=${DEXCLI_REPOSITORY:-GucciGross/DexCLI}
DEXCLI_REF=${DEXCLI_REF:-main}
TMP_ROOT=${TMPDIR:-/tmp}
BOOTSTRAP_TMP=$(mktemp -d "$TMP_ROOT/dex-bootstrap.XXXXXX") || {
    printf 'Dex bootstrap: could not create a temporary directory\n' >&2
    exit 1
}
cleanup() {
    rm -rf "$BOOTSTRAP_TMP"
}
trap cleanup EXIT HUP INT TERM

INSTALLER="$BOOTSTRAP_TMP/install.sh"

fetch_with_gh() {
    gh api \
        -H 'Accept: application/vnd.github.raw+json' \
        "repos/$DEXCLI_REPOSITORY/contents/install.sh?ref=$DEXCLI_REF" \
        > "$INSTALLER"
}

TOKEN=${GH_TOKEN:-${GITHUB_TOKEN:-}}
if command -v gh >/dev/null 2>&1; then
    if ! gh auth status --hostname github.com >/dev/null 2>&1; then
        if [ -r /dev/tty ] && [ -w /dev/tty ]; then
            printf '%s\n' 'DexCLI private beta requires GitHub sign-in once.' >/dev/tty
            gh auth login \
                --hostname github.com \
                --git-protocol https \
                --web \
                </dev/tty >/dev/tty
        fi
    fi
    if gh auth status --hostname github.com >/dev/null 2>&1; then
        TOKEN=$(gh auth token --hostname github.com 2>/dev/null || true)
        if [ -n "$TOKEN" ]; then
            GH_TOKEN=$TOKEN
            export GH_TOKEN
        fi
        fetch_with_gh
    fi
fi

if [ ! -s "$INSTALLER" ] && [ -n "$TOKEN" ]; then
    command -v curl >/dev/null 2>&1 || {
        printf 'Dex bootstrap: curl or an authenticated GitHub CLI is required\n' >&2
        exit 1
    }
    curl -fsSL --proto '=https' --tlsv1.2 \
        -H 'Accept: application/vnd.github.raw+json' \
        -H "Authorization: Bearer $TOKEN" \
        "https://api.github.com/repos/$DEXCLI_REPOSITORY/contents/install.sh?ref=$DEXCLI_REF" \
        -o "$INSTALLER"
fi

if [ ! -s "$INSTALLER" ]; then
    cat >&2 <<'EOF'
Dex bootstrap could not access the private DexCLI beta.

Install GitHub CLI and run `gh auth login`, or export GH_TOKEN/GITHUB_TOKEN,
then rerun the same one-line installer. This authentication step disappears
when public DexCLI release assets are published.
EOF
    exit 1
fi

sh -n "$INSTALLER"
exec sh "$INSTALLER" "$@"
