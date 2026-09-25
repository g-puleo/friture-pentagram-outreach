# Che Suono È? / What Sound Is It?

A bilingual (Italian / English) spectrogram-matching game for public outreach
events. Seven spectrograms on the left, seven sound names on the right; visitors
match them, submit, then listen to each one to find out whether they were right.

This is **not** part of the Friture application. It is a standalone web page that
borrows Friture's spectrogram pipeline for teaching purposes, and nothing in the
`friture/` package imports it or depends on it.

## Running it

**`che-suono-e.html` is the whole game — just open it.** It is a single
self-contained file with the fonts and the recordings embedded, so it needs no
network, no server and nothing else from this folder. Copy that one file to a
USB stick and it works anywhere. It is a build output, generated from the two
files below.

`che-suono-e.src.html` is the source. It reads its recordings from `sounds/`,
and browsers refuse to `fetch` from `sounds/` when a page is opened straight
from disk as a `file://` URL, so **opening the source from disk falls back to
the synthesized sounds** and shows a notice saying so. That is the one trap
here: edit the source, but open the built file. To try the source as you work,
serve it:

    cd outreach && python3 -m http.server
    # then open http://localhost:8000/che-suono-e.src.html

## The sounds

Seven, all 4 seconds at 22,050 Hz. Four are real recordings loaded from
`sounds/` — a Northern cardinal, rain, the opening of Beethoven's Fifth, and a
sneeze. Three are synthesized by the page itself in plain JavaScript — the hand
clap, the whistle, and GW170817. See `sounds/CREDITS.md` for the
provenance and licence of every recording; **the cardinal's attribution line is
still a placeholder** and must be completed before the page is published.

`sounds/gwosc/` holds four GWOSC sonifications and `sounds/gw170817-h1.ogg`
holds real processed LIGO-Hanford strain. Neither is used by the game; both are
kept as alternative material for the GW card, and `sounds/CREDITS.md` explains
the trade-off.

Each entry in the `SOUNDS` array carries an `id`, a `synth()` function, and
optionally a `src` (a file under `sounds/`) plus a `fit` mode saying how to cut
it down to the four-second slot — `peak` centres on the loudest moment, `end`
keeps the tail, `start` takes it from the beginning. When `src` is present the page fetches and decodes it, resampling
through a 22,050 Hz `OfflineAudioContext`; **if that fails for any reason it
falls back to `synth()`**, so the game always works. To swap in another recording,
drop a file in `sounds/` and set `src`; no game logic changes.

### About the GW170817 card

The card is **synthesized** — `synthGW()` builds a Newtonian inspiral from the
event's real parameters (chirp mass ≈ 1.188 M☉, `f ∝ (t_c − t)^(−3/8)`) over a
coloured noise floor, sped up and shifted upward to be audible. It shows the
iconic rising chirp, which is what makes the card teachable.

It is a model, not a measurement, and the page's colophon says so.

`sounds/gw170817-h1.ogg` is the alternative: real LIGO-Hanford strain, whitened
by the Hanford spectral density, band-passed to 30–400 Hz and sped up 3×.
Regenerate it from GWOSC with `python3 outreach/make-gw170817.py`. Switching the
card to it is a one-line change — add `src: "sounds/gw170817-h1.ogg", fit: "end"`
to the `gw` descriptor and drop `dr` to about 30 — **but be warned that it shows
no chirp at all.** GW170817's signal-to-noise ratio is accumulated by matched
filtering over roughly 100 s in band, so in any individual time-frequency pixel
the signal sits below the noise; the card reads as a sharp-edged band of noise.
That is physics, not a processing error, and it is exactly why the GW Open Data
Workshop tutorial reaches for a Q-transform at Q≈100 to make the track visible.
It makes an honest but very hard card. If you make the swap, restore the GWOSC
acknowledgement to the page colophon as well.

## The spectrograms

They are computed in the browser from the very samples that get played, using the
same chain as Friture's live display, ported to JavaScript:

| Step | Ported from |
|---|---|
| Hann window, 1024-point FFT, 75% overlap | `friture/audioproc.py` |
| Power to dB, `10·log10(p + 1e-30)`, then normalised over a dynamic range | `friture/spectrogram.py`, `log_spectrogram` / `scale_spectrogram` |
| Mel frequency axis, `2595·log10(1 + f/700)`, rows evenly spaced in mel | `friture/plotting/frequency_scales.py`, `Mel` |
| Row interpolation between FFT bins | `friture/signal/frequency_resampler.py` |
| CMRmap colour table, interpolated from the 9 reference anchors | `friture/plotting/cmrmap_generate.py`, `CMRref` |
| High frequencies at the top | `friture/spectrogram_image.py`, `addData` |

The one value that is not a straight port is the dynamic range: Friture's fixed
-140/0 dB suits its own input normalisation, while here each clip sets its floor
relative to its own peak (the per-sound `dr` field), tuned so that all seven read
well side by side.

## Visitor statistics

After each submit the page shows how everyone who has played on that machine
has done: number of rounds, average score, and the per-spectrogram accuracy as
a sorted bar chart, hardest first, with the most-missed one called out by name.

It is deliberately local. The tally lives in `localStorage` under
`che-suono-e/stats/v1`, so it accumulates across rounds and survives reloads,
but it never leaves the machine and there is no server. Two consequences worth
knowing at an event:

- **Each machine has its own tally.** Two laptops do not pool their numbers.
- **Storage can be unavailable** — a private window, or a browser set to block
  site data. Every access is wrapped, and the page falls back to an in-memory
  tally that lasts as long as the tab stays open, so nothing breaks.

The panel only appears after a visitor submits, never while they are still
matching, so it cannot hint at an answer. The operator can clear the tally with
the small **azzera / reset** link in the panel footer, which asks first; do that
once before the doors open, since testing inflates the numbers.

## Rebuilding the offline file

`che-suono-e.html` is generated. After editing `che-suono-e.src.html` or
changing anything in `sounds/`, run:

    python3 outreach/build-offline.py

It embeds the IBM Plex latin and latin-ext subsets from Google Fonts and every
`sounds/` file as data URIs, and refuses to write a file that would still need a
network. A connection is needed for the build, never to run the result.

## Licensing

The page itself is part of Friture and is under the GNU GPL v3, like the rest of
the repository. The embedded and bundled third-party material is not:

| What | Licence |
|---|---|
| IBM Plex, embedded in the built file | SIL Open Font License 1.1 — see `IBM-Plex-OFL.txt` |
| `sounds/bird-cardinal.ogg` | Creative Commons (Xeno-canto XC1151504) — **variant and recordist still to be recorded** |
| `sounds/rain.ogg` | Public domain (Wikimedia Commons) |
| `sounds/orchestra-beethoven5.ogg` | Public domain (Wikimedia Commons) |
| `sounds/sneeze.ogg` | Public domain (Wikimedia Commons) |
| `sounds/gw170817-h1.ogg` and `sounds/gwosc/*.wav`, neither used by the game | CC BY 4.0 (GWOSC) |

GWOSC asks that use of their data be acknowledged. The page itself no longer
uses GWOSC data, so it no longer carries the acknowledgement; the repository
does ship GWOSC files, so it is recorded here and in `sounds/CREDITS.md`, and it
must go back into the page colophon if the GW card is ever pointed at one of
them:

> This research has made use of data obtained from the Gravitational Wave Open
> Science Center (gwosc.org), a service of the LIGO Scientific Collaboration, the
> Virgo Collaboration, and KAGRA.
