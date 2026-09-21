# START HERE — Ambient Scribing Demo

## Graham / Windows: the easy way

You do **not** need Python, npm, a terminal, or a web server.

1. In GitHub, make sure you are on branch `asvh-harden-011-from-225-baseline`.
2. Click the green **Code** button.
3. Choose **Download ZIP**.
4. Open the downloaded ZIP and choose **Extract all**.
5. Open the extracted `demo-ui` folder.
6. Double-click **START-DEMO-WINDOWS.cmd**.
7. Your normal browser opens the FlowSignal Ambient Scribing Runtime Authority demo.

After that, every time you want the demo, just double-click **START-DEMO-WINDOWS.cmd**.

## What to click in the demo

Run these left to right:

1. **Current standing ACTIVE** → **Attempt represented EPR commit** → expected **COMMITTED**.
2. **Standing withdrawn** → attempt commit → expected **BLOCKED**, represented EPR unchanged.
3. **Earlier capability** → attempt commit → expected **BLOCKED**. This visualises the current AIRP-008 property.
4. **Standing dependency** → use the dropdown. Only **exact typed ACTIVE** should commit; all other AIRP-009 cases should block.

Then point to **Preserved engineering history** and **REFERENCE MODEL ENDS HERE**.

## Important evidence boundary

This browser demo is a visual companion to the executable ASVH/AIRP evidence. It does not turn the browser into an EPR or prove production enforcement. The preserved executable evidence remains in the tests/evidence folders and GitHub Actions run **35500425335**.

## Presenter line

> “The screen makes the evidence easier to see. The evidence itself remains the frozen tests, preserved failures, remediation records and verification runs underneath it.”
