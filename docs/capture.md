# Reproduce the terminal recording

The walkthrough records actual `takeoff --help` and `takeoff prompt` output in
an isolated local shell. It demonstrates the launcher, not an agent completing
a release review. The commands require no model account.

Install [ttyd](https://github.com/tsl0922/ttyd) and FFmpeg on your PATH, plus
Node.js 20 or later. From this checkout:

```sh
capture_tools="$(mktemp -d)"
npm install --prefix "$capture_tools" playwright@1.62.0
"$capture_tools/node_modules/.bin/playwright" install chromium
PLAYWRIGHT_MODULE="$capture_tools/node_modules/playwright/index.mjs" node docs/capture.mjs
```

The recorder uses local port 8832, closes its browser and shell afterward, and
writes `takeoff-help.png`, `takeoff-demo.webm`, `takeoff-demo.mp4`, `cover.png`,
and `capture-result.json` here. Keep that port free before running it.

[VHS](https://github.com/charmbracelet/vhs) was tried first. Version 0.12.0 exited
successfully on the capture machine but created no requested output files.
The direct ttyd + Playwright recording is the verified fallback.

The paper-glider mark is an illustration generated with OpenAI's built-in image
tool, not product evidence. Prompt: a compact origami paper glider, charcoal and
burnt orange on ivory, flat broad shapes, no text, shadows, or gradients.
Space Grotesk is included under the SIL Open Font License in `OFL.txt`.
