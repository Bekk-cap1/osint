#!/usr/bin/env bash
# Install Hunter on Kali / Debian / Linux: build, copy to PATH dir, append shell rc if needed.
# Run this script as your normal user — do not use "sudo go build" (can break ~/go cache permissions).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

usage() {
	echo "Usage: $0 [--system]"
	echo "  (default)  install to \$HOME/.local/bin and add it to PATH in .bashrc / .zshrc if missing"
	echo "  --system   sudo install to /usr/local/bin (usually already on PATH)"
	exit "${1:-0}"
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
	usage 0
fi

if ! command -v go &>/dev/null; then
	echo "[!] Go not found. Install Go 1.22+ (apt or https://go.dev/dl/)" >&2
	exit 1
fi

echo "[*] Building..."
go build -o hunter ./cmd/hunter

if [[ "${1:-}" == "--system" ]]; then
	if [[ "${EUID:-}" -ne 0 ]] && command -v sudo &>/dev/null; then
		sudo install -m 755 hunter /usr/local/bin/hunter
	else
		install -m 755 hunter /usr/local/bin/hunter
	fi
	echo "[+] Installed: /usr/local/bin/hunter (should be on PATH already)"
	exit 0
fi

INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"
mkdir -p "$INSTALL_DIR"
install -m 755 hunter "$INSTALL_DIR/hunter"
echo "[+] Installed: $INSTALL_DIR/hunter"

PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'
add_path_to_rc() {
	local rc="$1"
	if [[ ! -f "$rc" ]]; then
		return
	fi
	if ! grep -qsF '.local/bin' "$rc" 2>/dev/null; then
		printf '\n# hunter (local bin)\n%s\n' "$PATH_LINE" >>"$rc"
		echo "[+] Appended PATH hint to $rc"
	else
		echo "[*] $rc already references .local/bin — skipped"
	fi
}

add_path_to_rc "$HOME/.bashrc"
add_path_to_rc "$HOME/.zshrc"

if [[ ! -f "$HOME/.bashrc" && ! -f "$HOME/.zshrc" ]]; then
	echo "[!] No .bashrc or .zshrc — add manually: $PATH_LINE"
fi

echo
# Kali default shell is zsh — sourcing .bashrc from zsh breaks (shopt, complete, …).
if [[ "${SHELL:-}" == */zsh ]]; then
	echo "[*] Your login shell is zsh. Reload config with:"
	echo "    source ~/.zshrc"
	echo "[!] Do NOT run: source ~/.bashrc  (use bash first: bash -l)"
elif [[ "${SHELL:-}" == */bash ]]; then
	echo "[*] Reload:  source ~/.bashrc"
else
	echo "[*] Reload the right rc file for your shell (zsh: ~/.zshrc, bash: ~/.bashrc)"
fi
echo "[*] Then: hunter -h   (or: $INSTALL_DIR/hunter -h)"
