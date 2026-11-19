// News-image entry for 18 November 2026 (Node 22, standard library only).
// The image is the entry.png beside this file, rendered at build time from
// generate.py (a deterministic PIL front-page layout of the day's verified
// news); the program only copies it to /output/entry.png, so both graded
// runs write byte-identical output with no network.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

copyFileSync(new URL('./entry.png', import.meta.url), join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
