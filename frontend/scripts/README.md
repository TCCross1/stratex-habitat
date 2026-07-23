# Frontend validation scripts

Browser smoke for Central Kentucky demo (optional):

```bash
yarn add -D puppeteer-core
# serve build on :3000 with backend on :8001, then run a headless login/screenshot
# against /twin asserting [data-testid=twin-image] src contains
# habitat-central-kentucky-demo-home and data-origin=demo.
```
