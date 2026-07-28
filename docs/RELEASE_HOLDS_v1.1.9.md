# Release HOLDs — eyeWalker (v1.1.9 tag + v1.1.10 tip)

**Tag `v1.1.9`:** eng ship SHA `9f19d54…`  
**Tip `v1.1.10`:** browser dual-loop 30 Hz sim HUD (not Jetson TRT)

| Item | Public stance |
|------|----------------|
| **MCP package** | **HOLD until real.** No `npx eyewalker-mcp@…` until a package exists and is reviewed. Available today: **OGX remote `tool_runtime`** via [ogx-provider-eyewalker](https://github.com/aeyemovment/ogx-provider-eyewalker). |
| **30 Hz browser dual-loop (sim)** | **In tip v1.1.10 PWA** — optional checkbox: ~30 Hz **simulated** HUD/tracker redraw + slower semantic cue path (~1.4 Hz). **Not** live CV; camera pixels are not used for detection; **not** Jetson TensorRT. |
| **Jetson / NVIDIA TRT 30 Hz edge stack** | **Still roadmap only** (PeopleNet/YOLO/FastDepth TRT, etc.). Not claimed as shipped hardware. |
| **Dual-use / aerial surveillance product** | **Not this repo’s product claim.** Inspiration art under `docs/inspiration/` is concept only. |
| **Apple Health / Fitness / Activity** | **Not integrated.** |
| **NemoClaw “secured / never leaves”** | **Forbidden marketing.** Optional unenforced policy notes only. |

When a HOLD is lifted, update this file, the GitHub Release notes, and run claims skim before public statements.
