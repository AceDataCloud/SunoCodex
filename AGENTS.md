# Codex service package

This repository owns this single Codex plugin. Hosted API/MCP implementation stays in AceDataCloud/MCPs; do not duplicate providers or change prices/defaults here. Native plugin ID, marketplace entry and service tool scope must stay aligned. Keep Ace publisher attribution and distinguish third-party installation from official catalog listing.

Use an isolated checkout and check latest branch/PR state before pushing. Run `python3 -m unittest discover -s tests -v`; for native host acceptance run `python3 scripts/native_smoke.py --codex /path/to/codex` in its isolated profile. No paid generation, global Codex edits, new fallback or merge without authorization. Never commit credentials.
