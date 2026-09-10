import { fileURLToPath, pathToFileURL } from "node:url";
import { execFileSync, spawn } from "node:child_process";
import { cp, mkdtemp, mkdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { createHash } from "node:crypto";

const { chromium } = await import(
  process.env.PLAYWRIGHT_MODULE
    ? pathToFileURL(path.resolve(process.env.PLAYWRIGHT_MODULE)).href
    : "playwright"
);
const root = fileURLToPath(new URL("../", import.meta.url));
const output = path.join(root, "docs");
const fixtureSource = path.join(root, "test", "fixtures", "agent-review-demo");
const takeoffPrompt = path.join(root, "PASS.md");
const port = "8854";

execFileSync("ffmpeg", ["-version"], { stdio: "ignore" });
await mkdir(output, { recursive: true });
const fixture = await mkdtemp(path.join(tmpdir(), "takeoff-agent-review-"));
let server;
let browser;

function git(...args) {
  execFileSync("git", ["-C", fixture, ...args], { stdio: "ignore" });
}

async function sourceFingerprint() {
  const files = ["README.md", "shipping.py", "test_shipping.py"];
  return Object.fromEntries(await Promise.all(files.map(async (file) => {
    const bytes = await readFile(path.join(fixture, file));
    return [file, { bytes: bytes.length, sha256: createHash("sha256").update(bytes).digest("hex") }];
  })));
}

try {
  await cp(fixtureSource, fixture, { recursive: true });
  git("init", "-q");
  git("config", "user.email", "takeoff-demo@example.invalid");
  git("config", "user.name", "Takeoff Demo");
  git("add", "README.md", "shipping.py", "test_shipping.py");
  git("commit", "-qm", "fixture: weak shipping threshold test");
  const sourceBefore = await sourceFingerprint();

  server = spawn(
    "ttyd",
    [
      "-p", port, "-i", "127.0.0.1", "-W", "-w", fixture,
      "-t", "fontSize=14", "-t", "screenReaderMode=true", "-t", "fontFamily=Menlo",
      "-t", 'theme={"background":"#f4f2eb","foreground":"#212920","cursor":"#b6532a"}',
      "claude", "--safe-mode", "--strict-mcp-config",
      "--mcp-config", '{"mcpServers":{}}', "--model", "sonnet", "--effort", "low",
      "--tools", "Bash,Read,Write,Edit",
    ],
    {
      env: { ...process.env, PS1: "$ ", BASH_ENV: "/dev/null", BASH_SILENCE_DEPRECATION_WARNING: "1" },
      stdio: ["ignore", "pipe", "pipe"],
    },
  );
  let logs = "";
  const recordServerOutput = (chunk) => (logs += chunk);
  server.stdout.on("data", recordServerOutput);
  server.stderr.on("data", recordServerOutput);
  await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(Error(logs || "ttyd startup timeout")), 10000);
    const ready = () => {
      if (logs.includes("Listening on port")) { clearTimeout(timeout); resolve(); }
    };
    server.stdout.on("data", ready);
    server.stderr.on("data", ready);
    server.once("exit", (code) => { clearTimeout(timeout); reject(Error(`ttyd exited ${code} ${logs}`)); });
  });

  browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1440, height: 980 },
    recordVideo: { dir: output, size: { width: 1440, height: 980 } },
  });
  const page = await context.newPage();
  await page.goto(`http://127.0.0.1:${port}`);
  await page.locator(".xterm-helper-textarea").waitFor({ state: "attached" });
  await page.addStyleTag({
    content: "body{margin:0;background:#e6e4dd!important;padding:60px;box-sizing:border-box}#terminal-container{width:calc(100vw - 120px)!important;height:calc(100vh - 120px)!important;border-radius:12px;overflow:hidden;padding:0;background:#f4f2eb;box-sizing:border-box}.xterm{height:100%;overflow:hidden}",
  });
  await page.setViewportSize({ width: 1441, height: 981 });
  await page.setViewportSize({ width: 1440, height: 980 });
  await page.waitForFunction(() => document.body.textContent.includes("Claude Code"), null, { timeout: 15000 });
  await page.locator(".xterm-helper-textarea").focus();
  if ((await page.locator("body").innerText()).includes("Yes, I trust this folder")) {
    await page.keyboard.press("ArrowDown");
    await page.keyboard.press("Enter");
  }
  const request = [
    `Act as the release reviewer for this tiny public fixture. Read ${takeoffPrompt} and follow its bounded review discipline.`,
    "Do not modify README.md, shipping.py, or test_shipping.py. You may write only evidence/takeoff-pass/claude-demo-receipt.md.",
    "Run python3 -m unittest discover -v. Compare the shipping threshold in README.md with shipping.py, and determine whether the test would catch an order below the documented threshold receiving free shipping.",
    "Do not print tool output or read the receipt back. Finish with exactly two bullets, maximum 35 words total: one mismatch and one weak-test finding; then one RECEIPT: path line and TAKEOFF_DEMO_COMPLETE. Do not push, deploy, publish, install globally, or change account settings.",
  ].join(" ");
  await page.keyboard.type(request, { delay: 8 });
  await page.keyboard.press("Enter");
  await page.waitForFunction(
    () => /done \d{1,2}:\d{2} [AP]M/.test(document.body.textContent),
    null,
    { timeout: 180000 },
  );
  await page.waitForTimeout(3000);
  const terminal = await page.locator("body").innerText();
  await writeFile("/tmp/takeoff-claude-terminal.txt", terminal);
  const receiptPath = path.join(fixture, "evidence", "takeoff-pass", "claude-demo-receipt.md");
  const receipt = await new Promise((resolve, reject) => {
    const deadline = Date.now() + 30_000;
    const check = async () => {
      try { resolve(await readFile(receiptPath, "utf8")); }
      catch (error) {
        if (Date.now() >= deadline) reject(error);
        else setTimeout(check, 250);
      }
    };
    check();
  });
  if (!(receipt.includes("5,000") || receipt.includes("$50")) || !(receipt.includes("7,500") || receipt.includes("$75")))
    throw Error("Claude receipt did not record the observed threshold mismatch");
  const sourceAfter = await sourceFingerprint();
  if (JSON.stringify(sourceAfter) !== JSON.stringify(sourceBefore))
    throw Error("Claude modified fixture source outside its scoped receipt");
  const receiptDestination = path.join(root, "evidence", "takeoff-pass", "claude-demo-receipt.md");
  await mkdir(path.dirname(receiptDestination), { recursive: true });
  await writeFile(receiptDestination, receipt);
  const receiptHash = createHash("sha256").update(receipt).digest("hex");
  await page.screenshot({ path: path.join(output, "takeoff-help.png") });
  const video = page.video();
  await context.close();
  await video.saveAs(path.join(output, "takeoff-demo.webm"));
  await video.delete();
  await writeFile(path.join(output, "capture-result.json"), `${JSON.stringify({
    commands: ["Native Claude Code reads PASS.md and reviews the public shipping-threshold fixture"],
    fixture: "test/fixtures/agent-review-demo",
    receipt: "evidence/takeoff-pass/claude-demo-receipt.md",
    receiptSha256: receiptHash,
    sourceBefore,
    sourceAfter,
    browser: browser.version(),
    recordedAt: new Date().toISOString(),
  }, null, 2)}\n`);
  execFileSync("ffmpeg", ["-y", "-i", path.join(output, "takeoff-demo.webm"), "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path.join(output, "takeoff-demo.mp4")], { stdio: "ignore" });
  for (const name of ["takeoff-help.png", "takeoff-demo.webm", "takeoff-demo.mp4"])
    if ((await stat(path.join(output, name))).size < 1000) throw Error(`Capture missing: ${name}`);
  console.log("Verified native Claude Code Takeoff review screenshot and recording exist.");
} finally {
  if (browser) await browser.close();
  if (server) server.kill("SIGTERM");
  await rm(fixture, { recursive: true, force: true });
}
