/**
 * H-014C.1 visual smoke — desktop + mobile twin states.
 * Uses local build + Habitat backend. Demo/sample only; no fabricated geometry.
 */
const fs = require("fs");
const path = require("path");
const http = require("http");
const { spawn } = require("child_process");

const OUT = "/opt/cursor/artifacts/h014c1-smoke";
const BACKEND = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8001";
const PORT = 4173;

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const puppeteer = require("puppeteer-core");

  const buildDir = path.join(__dirname, "..", "build");
  if (!fs.existsSync(buildDir)) {
    throw new Error("frontend/build missing — run CI=true yarn build first");
  }

  const server = spawn("npx", ["--yes", "serve", "-s", buildDir, "-l", String(PORT)], {
    cwd: path.join(__dirname, ".."),
    stdio: "ignore",
  });

  await new Promise((r) => setTimeout(r, 2500));

  const browser = await puppeteer.launch({
    executablePath: "/usr/local/bin/google-chrome",
    headless: "new",
    args: ["--no-sandbox", "--disable-gpu", "--window-size=1440,900"],
  });

  const report = {
    directive: "H-014C.1",
    captured_at: new Date().toISOString(),
    backend: BACKEND,
    screenshots: [],
    console_errors: [],
    notes: [],
  };

  async function shot(page, name) {
    const file = path.join(OUT, `${name}.png`);
    await page.screenshot({ path: file, fullPage: true });
    report.screenshots.push(file);
    return file;
  }

  try {
    const page = await browser.newPage();
    page.on("pageerror", (e) => report.console_errors.push(String(e)));
    page.on("console", (msg) => {
      if (msg.type() === "error") report.console_errors.push(msg.text());
    });

    // Desktop login
    await page.setViewport({ width: 1440, height: 900 });
    await page.goto(`http://127.0.0.1:${PORT}/login`, { waitUntil: "networkidle0", timeout: 60000 });
    await page.waitForSelector('[data-testid="auth-email"]');
    await page.click('[data-testid="auth-email"]', { clickCount: 3 });
    await page.type('[data-testid="auth-email"]', "alex@stratexhabitat.com");
    await page.click('[data-testid="auth-password"]', { clickCount: 3 });
    await page.type('[data-testid="auth-password"]', "Demo123!");
    await Promise.all([
      page.click('[data-testid="auth-submit"]'),
      page.waitForNavigation({ waitUntil: "networkidle0", timeout: 60000 }).catch(() => null),
    ]);
    await page.waitForFunction(() => !window.location.pathname.includes("/login"), { timeout: 30000 }).catch(() => null);
    await page.goto(`http://127.0.0.1:${PORT}/twin`, { waitUntil: "networkidle0", timeout: 60000 });
    await page.waitForSelector(
      '[data-testid="existing-room-twin"], [data-testid="existing-room-twin-loading"], [data-testid="twin-stage"]',
      { timeout: 30000 }
    );
    await page.waitForSelector('[data-testid="existing-room-twin"], [data-testid="model-provenance"]', { timeout: 30000 }).catch(() => null);
    await shot(page, "desktop-ky-demo-twin");

    // Overflow check
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
    report.horizontal_overflow_desktop = overflow;

    // Mobile
    await page.setViewport({ width: 390, height: 844, isMobile: true, hasTouch: true });
    await page.reload({ waitUntil: "networkidle0" });
    await page.waitForSelector('[data-testid="existing-room-twin"], [data-testid="existing-room-twin-loading"], [data-testid="twin-stage"]', { timeout: 30000 });
    await shot(page, "mobile-ky-demo-twin");
    report.horizontal_overflow_mobile = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2
    );

    // Provenance / lifecycle text presence
    const bodyText = await page.evaluate(() => document.body.innerText);
    report.contains_demo_label = /DEMO|SAMPLE ONLY|demo_sample|sample-only/i.test(bodyText);
    report.contains_villa_or_austin = /Villa Horizon|Austin, TX/i.test(bodyText);
    report.notes.push("Approved/draft/needs-recapture visual states covered by Jest fixtures; live seed is demo_sample only.");
    report.notes.push("3D model present state uses test-only fixture in Jest — no authored GLB in demo seed.");
    report.notes.push("Physical LiDAR UNEXECUTED.");
  } finally {
    await browser.close();
    server.kill("SIGTERM");
  }

  fs.writeFileSync(path.join(OUT, "smoke-report.json"), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  if (report.contains_villa_or_austin) process.exitCode = 2;
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
