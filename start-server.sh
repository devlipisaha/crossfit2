#!/bin/sh
cd "$(dirname "$0")" || exit 1
command -v node >/dev/null || { echo "Node.js is not installed: https://nodejs.org"; exit 1; }
node server.js
