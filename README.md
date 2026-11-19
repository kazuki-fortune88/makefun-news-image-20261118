[![make.fun](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/kazuki-fortune88/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/kazuki-fortune88/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

Entry by [kazuki-fortune88](https://github.com/kazuki-fortune88) for the [make.fun bounty news-image-20261118](https://make.fun/bounty/news-image-20261118) — sum up 18 November's world news in one image.
Run: `mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts` · Referral code: `4fxhr3y1`

---

# Wednesday 18 November 2026 — the day's world news on one front page

Entry for the make.fun bounty **news-image-20261118**
("Sum up 18 November's world news in one image").

## The image

`entry.png` (1024×1024, 218,922 bytes) is a newspaper front page with
**46 stories** — 12 illustrated panels + 34 more in a numbered list:

- Masthead naming the day, a region strip (Middle East 4, Americas 11,
  Asia 7, Europe 8, Africa 8, Oceania 4, World 4), a stats strip
  (141 drones / 56–44 Senate / $115.8bn Nvidia / 25.9bn km Voyager 1),
  a dotted world map with numbered pins for stories 1–12,
  and a **DATE CHECK** line saying what was left out on purpose.
- Every panel carries a per-story source (Reuters, AP, AFP, BBC,
  Al Jazeera, NPR, ONS, WHO, NASA, Amnesty — see the footer).

## v2 changes (19 Nov 2026) — gap-hunting rebuild, not a copy of rank 1

Four panel swaps, 1-for-1, so the page stays readable at 46 stories:

1. **Anthropic IPO becomes a panel** (#12, was only a stat): priced
   $83/share, $81.3bn raise (largest ever), 980m shares, ~$1.5tn
   value. First trade Thu 19 Nov — stated in the panel, and in DATE CHECK.
2. **Alaska / US Senate** (#5): AP calls Alaska for Mary Peltola over
   Dan Sullivan; Democrats take the Senate 56–44. Panel says
   "Reported 18 Nov" — the AP call was 17 Nov US time, reported widely
   on the 18th.
3. **Dhoni retires from the IPL** (#9, CSK mentor for 2027) — the page's
   first sport panel; UK inflation moved down to ALSO #35.
4. **Cyclone Xavier** (#6): Category 5 peak near Pukapuka, Cook Islands
   (215 km/h, 922 hPa — strongest November cyclone on record in the
   Southern Hemisphere). Worded as a **peak, not a landfall** — it never
   made landfall. Cyclone Akvan's panel was dropped (its landfall is due
   20 Nov, still named in DATE CHECK).
5. **Ebola upgraded** (ALSO #31): still a WHO global emergency (PHEIC),
   11,000+ cases, 5,400 dead — was one vague line.
6. **Brazil** (ALSO #46): Senate passes Lula's fiscal package,
   saving R$45–56bn in 2027.
7. **Nvidia fixed** (ALSO #32): Q3 revenue $115.8bn (+103% YoY),
   Q4 guide $130bn. The v1 line ("beats forecasts; shares fall ~3%")
   mixed up Tuesday's close with the after-hours reaction (+4.8%).
8. **Quad fixed** (ALSO #14): joint P-8/P-3C patrols in 2027, $85m AI
   Accelerator — was just "leaders meet in Manila".
- Also fixed: An-12 crash now says 13 killed (was "all aboard killed");
  oil now says Brent settled down 1.3% on Wednesday (v1's "slides 3.2%"
  was Tuesday's WTI move); stats strip now 56–44 and $115.8bn Nvidia
  instead of repeating the Anthropic/Jeffries panel numbers.
- Oceania goes 1 → 4 stories (Xavier panel, Australia sanctions,
  ARIA Awards, Fiji drought disaster, ALSO #45). Fiji's disaster
  declaration was announced 17 Nov Fiji time and reported 18 Nov UTC.
- Dropped to make room (6 out, 6 in): GTA VI panel (full launch is
  19 Nov, still named in DATE CHECK), Fed minutes panel, Pew 2035
  forecast, El Salvador raid; Akvan panel and UK-inflation panel
  (UK inflation survives as ALSO #35).

## Verification

Each story was checked against reporting dated 18 November 2026
(Reuters/AP/AFP/BBC/Al Jazeera/NPR/ONS/WHO/NASA and others) before it was
drawn. Stories that could not be verified for the 18th were dropped, not
forced in. The DATE CHECK on the image is honest about near-misses: the
Qeshm strike and the Kerch Bridge collapse were 17 Nov; GTA VI's full
launch and Anthropic's first trade are Thu 19 Nov; Cyclone Akvan's
landfall is due Fri 20 Nov. Deliberately **not** included: the ICJ
Rohingya-genocide ruling (due 19 Nov) and the Trump–Xi–Putin trilateral
(19 Nov).

## Build

`generate.py` (Python 3 + Pillow + DejaVu, build-time only) draws the
image deterministically: fixed fonts, layout and palette, no network, no
timestamps, no randomness. It also self-checks for text overflow and
prints `OVERFLOW ...` warnings if any headline, body or list item wraps
past its allotted lines.

```sh
python3 generate.py            # writes entry.png (218,922 bytes)
python3 generate.py out.png    # writes out.png instead
```

`main.ts` (Node 22, standard library only) is the graded program: it
only copies the shipped `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output`), so both graded runs write byte-identical output
with no network.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## Tests run

- `generate.py` run twice (and twice more after each fix round):
  identical SHA-256
  (`c038cafe56cb5e15d53789547816cdd96608f0961bd2ceb838ba7cb53b5d4ddf`).
- `main.ts` twice into different output dirs: byte-identical to each
  other and to `entry.png` (`cmp` clean).
- PNG valid, 1024×1024, 218,922 bytes ≤ 1 MiB.
- No `OVERFLOW` warnings on the final run.
- Visual check at full size, in panel crops (Senate, Xavier, Anthropic,
  Gulf, Jeffries), and at 300 px: all 46 stories legible, no text
  clipped or overflowing its panel. Three overlap defects found in
  crops during QA were fixed and re-verified (Senate "DEMOCRATS" vs
  illustration label, Anthropic "A SHARE" vs label, kicker/source
  collisions on panels 2, 6, 11, 12).

## License

See `LICENSE`.
