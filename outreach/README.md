# Che Suono È? / What Sound Is It?

A bilingual (Italian / English) spectrogram-matching game for public outreach
events. Seven spectrograms on the left, seven sound names on the right; visitors
match them, submit, then listen to each one to find out whether they were right.

This is **not** part of the Friture application. It is a standalone web page that
borrows Friture's spectrogram pipeline for teaching purposes, and nothing in the
`friture/` package imports it or depends on it.

## Running it

**At an event, use `che-suono-e.offline.html`.** It is a single self-contained
file with the fonts and the recordings embedded, so it needs no network and no
server. Copy it to a USB stick and it works anywhere.

`che-suono-e.html` is the source, and it reads its recordings from `sounds/`.
Browsers refuse to `fetch` from `sounds/` when a page is opened straight from
disk as a `file://` URL, so opening it that way falls back to the synthesized
sounds and shows a notice saying so. To work on it, serve it:

    cd outreach && python3 -m http.server
    # then open http://localhost:8000/che-suono-e.html

## The sounds

Seven, all 4 seconds at 22,050 Hz. Five are real recordings loaded from
`sounds/` — a Northern cardinal, rain, GW170817, the opening of Beethoven's
Fifth, and a sneeze. Two are synthesized by the page itself in plain
JavaScript — the hand clap and the whistle. See `sounds/CREDITS.md` for the
provenance and licence of every recording; **the cardinal's attribution line is
still a placeholder** and must be completed before the page is published.

`sounds/gwosc/` holds four GWOSC sonifications that the game does not use, kept
as alternative material for the GW card; `sounds/CREDITS.md` explains the
trade-off.

Each entry in the `SOUNDS` array carries an `id`, a `synth()` function, and
optionally a `src` (a file under `sounds/`) plus a `fit` mode saying how to cut
it down to the four-second slot — `peak` centres on the loudest moment, `end`
keeps the tail, `start` takes it from the beginning. When `src` is present the page fetches and decodes it, resampling
through a 22,050 Hz `OfflineAudioContext`; **if that fails for any reason it
falls back to `synth()`**, so the game always works. To swap in another recording,
drop a file in `sounds/` and set `src`; no game logic changes.

### A warning about the GW170817 card

`sounds/gw170817-h1.ogg` is the real event: LIGO-Hanford strain, whitened by the
Hanford spectral density, band-passed to 30–400 Hz, sped up 3×. Regenerate it
from GWOSC with `python3 outreach/make-gw170817.py`.

**It does not show a chirp, and it is not supposed to.** GW170817's
signal-to-noise ratio is accumulated by matched filtering over roughly 100 s in
band, so in any individual time-frequency pixel the signal sits below the noise.
The card reads as a sharp-edged band of noise between about 90 Hz and 1.2 kHz —
the band-pass limits — with nothing above. That distinguishes it from the rain
card, which fills the full height, but it is a card that visitors will find hard
to guess. The blurb turns this into the teaching point: this is why gravitational
wave astronomy needs matched filtering, and why the GW Open Data Workshop
tutorial reaches for a Q-transform at Q≈100 to make the track visible.

`synthGW()` remains in the page as a model waveform built from the event's real
parameters. It is what you get if the recording fails to load, and reverting the
card to it is a one-line change: delete the `src` on the `gw` descriptor.

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

## Rebuilding the offline file

`che-suono-e.offline.html` is generated. After editing `che-suono-e.html` or
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
| IBM Plex, embedded in the offline build | SIL Open Font License 1.1 — see `IBM-Plex-OFL.txt` |
| `sounds/bird-cardinal.ogg` | Creative Commons (Xeno-canto XC1151504) — **variant and recordist still to be recorded** |
| `sounds/rain.ogg` | Public domain (Wikimedia Commons) |
| `sounds/orchestra-beethoven5.ogg` | Public domain (Wikimedia Commons) |
| `sounds/sneeze.ogg` | Public domain (Wikimedia Commons) |
| `sounds/gw170817-h1.ogg`, derived from LIGO open data | CC BY 4.0 (GWOSC) |
| `sounds/gwosc/*.wav`, not used by the game | CC BY 4.0 (GWOSC) |

GWOSC asks that use of their data be acknowledged, and the page carries the
acknowledgement in its footer:

> This research has made use of data obtained from the Gravitational Wave Open
> Science Center (gwosc.org), a service of the LIGO Scientific Collaboration, the
> Virgo Collaboration, and KAGRA.
