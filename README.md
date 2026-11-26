# 26 November 2026 — World News in One Image

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/joyrichh/makefun-news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/joyrichh/makefun-news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Make.Fun competition entry ([`news-image-20261126`](https://make.fun/bounty/news-image-20261126)) by [@joyrichh](https://github.com/joyrichh).
A program that writes one image summing up the world's news of Thursday,
26 November 2026, to `/output/entry.png`.

## The image

A 1024×1024 PNG infographic with a navy-and-gold masthead, the date
"26 November 2026", "WORLD NEWS • THURSDAY", a NOV / 26 badge,
six story cards in a two-column, three-row grid, and an "ALSO TODAY" strip:

1. **Space** — First Pakistani astronaut reaches China's Tiangong station.
   Shenzhou-24 docked with Tiangong on 25 November; Muhammad Zeeshan Ali is the first Pakistani in orbit and the first foreign astronaut aboard China's space station.
2. **Brazil** — Petrobras approves $122bn five-year investment plan.
   Brazil's state oil giant approved a $122 billion plan for 2027–2031, targeting record output of 2.9 million barrels a day and paying $2.6 billion in extra dividends.
3. **Canada** — Carney unveils aid for steel and lumber, new steel tariffs.
   PM Mark Carney announced support for steel and lumber hit by US tariffs, tighter quotas on foreign steel and a 25% global tariff on steel-derivative imports.
4. **Ukraine** — Russia's own figures show nearly 500,000 lost in Ukraine war.
   Leaked records from Russia's Rosstat agency, analysed by the BBC, show at least 490,334 Russian soldiers have died since the invasion began in February 2022.
5. **Colombia** — Colombia marks 10 years since historic peace deal.
   A decade after the 2016 accord with the FARC ended 50 years of war, UN chief Guterres urges Colombia to finish implementing it as violence persists where the state never reached.
6. **Bangladesh** — Bangladesh raises garment workers' minimum wage 36%.
   After weeks of protests that shut factories, the wage board raised the minimum to 17,000 taka (about $136) a month from 12,500, effective 1 December.

Also today:

- US consumer confidence hits near two-year high despite persistent inflation.
- Joint Japanese-European mission reaches Mercury after an eight-year journey.
- Venezuela reveals $237.5bn public debt as government prepares historic restructuring.

These supplied stories were reported on 24–26 November 2026 and verified
on 26 November against Reuters, BBC, AP, UN, ESA and Nature reporting.
They are retained verbatim in `news.json`. The Hong Kong Tai Po fire is
excluded: it happened on 26 November 2025, not 2026. The image footer reads:

> Sources: Reuters · BBC · AP · UN  —  26 November 2026

## How it works

- `main.py` targets Python 3.13 and imports only the standard-library modules
  `base64`, `os` and `sys`. It decodes `entry.png.b64` beside the script,
  verifies the PNG signature `89504e470d0a1a0a`, and writes `/output/entry.png`.
  `MAKEFUN_OUTPUT_DIR` overrides the output directory for local runs, even
  when the program is launched from a different working directory.
- `news.json` contains the date, all six stories in display order, their tag
  colors, three additional stories, sources and the verification note.
- `build_image.py` renders the bundled image with Pillow 10.2.0 and system
  DejaVu fonts. It measures the advance and bounding box of every text line,
  fits each complete headline to at most two lines and each complete summary
  to at most three, and asserts that text stays inside its section and card.
  No words are truncated or replaced with ellipses. Every line's measurements
  remain available in `MEASUREMENTS` for inspection after a build.
- The build and runtime make no network calls, use no randomness, embed no
  timestamps, and need no paid APIs or AI image generation. Repeated builds
  in the same rendering environment and repeated runs produce identical bytes.
- `.makefun/owner.json` identifies this entry's wallet. The MIT license covers
  the code and bundled image. `entry.png` and local output directories are
  ignored by Git; the portable image is tracked as `entry.png.b64`.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This creates `out/entry.png`: **1024×1024 pixels, 150,546 bytes**, below the
1 MiB (1,048,576-byte) limit. Without the override, the destination is
`/output/entry.png`. No third-party packages are required to run `main.py`.

Rebuild the bundled image (Pillow 10.2.0 and DejaVu fonts required at
`/usr/share/fonts/truetype/dejavu/`):

```sh
python3 build_image.py
base64 -w0 entry.png > entry.png.b64
```

Determinism check:

```sh
MAKEFUN_OUTPUT_DIR=out1 python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum entry.png out1/entry.png out2/entry.png
```

All three hashes must match. The renderer also checks the pixel dimensions,
file-size limit, line counts, complete text preservation and text bounds.

## License

MIT — see [LICENSE](LICENSE).
