# Reproduce the Claude Code review recording

The walkthrough starts native Claude Code in a temporary Git copy of the public
shipping-threshold fixture. Claude reads Takeoff's review instructions, runs the
fixture test, identifies the source/test mismatch, and writes a receipt. The
fixture source and test remain unchanged; the temporary copy is removed after
the recording. Before cleanup, the recorder copies Claude's generated receipt
to `evidence/takeoff-pass/claude-demo-receipt.md` in this checkout and records
its SHA-256 plus before/after fixture-source hashes in `capture-result.json`.

Install [ttyd](https://github.com/tsl0922/ttyd) and FFmpeg on your PATH, plus
Node.js 20 or later. From this checkout:

```sh
capture_tools="$(mktemp -d)"
npm install --prefix "$capture_tools" playwright@1.62.0
"$capture_tools/node_modules/.bin/playwright" install chromium
PLAYWRIGHT_MODULE="$capture_tools/node_modules/playwright/index.mjs" node docs/capture.mjs
```

The recorder uses local port 8854, closes its browser and Claude session
afterward, and writes `takeoff-help.png`, `takeoff-demo.webm`,
`takeoff-demo.mp4`, and `capture-result.json` here. Keep that port free before
running it. It requires an authenticated local Claude Code installation.

The paper-glider mark is an illustration generated with OpenAI's built-in image
tool, not product evidence. Prompt: a compact origami paper glider, charcoal and
burnt orange on ivory, flat broad shapes, no text, shadows, or gradients.
Space Grotesk is included under the SIL Open Font License in `OFL.txt`.
