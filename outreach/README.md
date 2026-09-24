# Che Suono È? / What Sound Is It?

A bilingual (Italian / English) spectrogram-matching game for public outreach
events. Seven spectrograms on the left, seven sound names on the right; visitors
match them, submit, then listen to each one to find out whether they were right.

This is **not** part of the Friture application. It is a standalone web page that
borrows Friture's spectrogram pipeline for teaching purposes, and nothing in the
`friture/` package imports it or depends on it.

## Running it

Open `che-suono-e.html` in any modern browser. There is no build step, no server
and no install.

For an event machine with no network, use `che-suono-e.offline.html` instead — it
is the same page with the fonts embedded, so it needs nothing at all. Copy it to a
USB stick and it will work anywhere.

## The sounds

All seven are synthesized by the page itself, in plain JavaScript, at 22,050 Hz
for 4 seconds each: a hand clap, rain, a bird chirping, the GW170817 neutron star
merger, an orchestra, a sneeze and a whistle. Nothing is loaded from disk or from
the network.

GW170817 follows the Newtonian inspiral law, `f(t) = f0 (1 - t/tc)^(-3/8)` with
amplitude proportional to `f^(2/3)`, over a synthetic detector noise floor. It is
sped up and shifted upward in frequency so that it both fits in four seconds and
reproduces on laptop speakers — the page says so on the card.

To replace a synthesized sound with a real recording, each entry in the `SOUNDS`
array carries an `id`, a `synth()` function and a `src` field. Set `src` to a file
URL and the page decodes that instead of calling `synth()`; no game logic changes.

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

`che-suono-e.offline.html` is generated. After editing `che-suono-e.html`, run:

    python3 outreach/build-offline.py

It downloads the IBM Plex latin and latin-ext subsets from Google Fonts and
embeds them as data URIs. A network connection is needed for the build, never to
run the result.

## Licensing

The page itself is part of Friture and is under the GNU GPL v3, like the rest of
the repository.

`che-suono-e.offline.html` embeds the IBM Plex fonts, which are licensed under the
SIL Open Font License 1.1 — see `IBM-Plex-OFL.txt`. The OFL permits this
redistribution; the fonts remain under their own licence, not the GPL.
