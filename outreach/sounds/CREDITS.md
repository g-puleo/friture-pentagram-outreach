# Sound credits

Four of the seven sounds in the game are real recordings. The hand clap, the
whistle and GW170817 are synthesized by the page itself and have no source to
credit.

`gw170817-h1.ogg` and everything in `gwosc/` are **not used by the game**. They
are kept here as alternative material for the GW card and for an explainer to
play from a laptop. See the last two sections.

## bird-cardinal.ogg

A Northern cardinal (*Cardinalis cardinalis*) singing: seven slurred descending
whistles followed by a fast trill.

Cut from 12.2 s to 16.2 s of the source recording, high-passed at 900 Hz to
remove the wind and traffic floor of the field recording, and loudness
normalised. The high-pass is a presentation choice, not a correction: without it
the bottom third of the card is a wash of background noise that hides the song.

- Source: [Xeno-canto](https://xeno-canto.org) recording **XC1151504**
- Recordist / licence: **TO BE FILLED IN** — Xeno-canto serves its pages behind a
  proof-of-work bot wall and its v3 API needs an account key, so the recordist's
  name and the exact Creative Commons variant could not be read automatically.
  They are printed on <https://xeno-canto.org/1151504>. Xeno-canto recordings are
  all under some Creative Commons licence, and every variant requires
  attribution, so this must be completed before the material is published.

Chosen because of *No hair but plenty of feathers: are birds black holes?*
(Laeuger & Knapp, [arXiv:2603.29064](https://arxiv.org/abs/2603.29064), an April
Fools' paper), which fits a time-reversed *Cardinalis cardinalis* chirp with a
precessing black hole binary waveform, using Xeno-canto data.

## rain.ogg

Steady rain, cut from 10 s to 14 s of the source recording.

- Source: Wikimedia Commons, [File:Rain (1).ogg](https://commons.wikimedia.org/wiki/File:Rain_(1).ogg)
- Licence: **Public domain**

## orchestra-beethoven5.ogg

The opening of the first movement of Beethoven's Fifth Symphony — the four-note
motif and the phrase that follows. Cut from 0.4 s to 4.4 s of the source
recording.

- Source: Wikimedia Commons, Beethoven, Symphony No. 5 in C minor, Op. 67,
  1st movement
- Licence: **Public domain** (the work, the performance and the recording)

## sneeze.ogg

A recording of two sneezes, used unmodified. The page pads it from 3.45 s to
the 4 s slot and normalises it at load time; the file itself is untouched.

- Source: Wikimedia Commons, [File:Sneezing.ogg](https://commons.wikimedia.org/wiki/File:Sneezing.ogg)
- Licence: **Public domain**

## gw170817-h1.ogg — not used by the game

The real gravitational wave event GW170817 — two neutron stars merging
130 million light years away, observed on 17 August 2017.

Derived from LIGO-Hanford (H1) strain data, 32 s at 4096 Hz around
GPS 1187008882.4, as published by GWOSC. Regenerate it with
`python3 outreach/make-gw170817.py`, which documents every step; in summary:

1. whitened by the Hanford amplitude spectral density, estimated by Welch's
   method over 4 s Hann segments of the same stretch of data;
2. band-passed to 30–400 Hz with raised-cosine edges;
3. the 12 s ending just after the coalescence, sped up 3×, so it fills the
   game's four-second slot and lands at 90–1200 Hz where a laptop speaker
   and the game's Mel axis can both reach it.

Hanford rather than Livingston because the Livingston data carries the
instrumental glitch about 1.1 s before the merger, which the GW Open Data
Workshop tutorials remove with `TimeSeries.gate()`.

- Source: [GWOSC](https://gwosc.org/eventapi/html/GWTC-1-confident/GW170817/v3/),
  file `H-H1_GWOSC_4KHZ_R1-1187008867-32.hdf5`
- Licence: **CC BY 4.0**
- Acknowledgement, as GWOSC requests: *This research has made use of data or
  software obtained from the Gravitational Wave Open Science Center
  (gwosc.org), a service of the LIGO Scientific Collaboration, the Virgo
  Collaboration, and KAGRA.*

### What it looks like, and why

Be aware of this before showing it: whitened and band-passed real strain does
**not** show a visible chirp in the game's STFT. GW170817's signal-to-noise
ratio is accumulated by matched filtering over roughly 100 s in band, so in any
individual time-frequency pixel the signal sits below the noise. The card reads
as a textured noise band rather than a rising curve. This is physics, not a
processing error — it is exactly why the ODW tutorial reaches for a Q-transform
at Q≈100 to make the track appear.

This is why the game's card is `synthGW()` instead: a model waveform built from
the event's real parameters, which does show the chirp. The page's colophon says
plainly that it is a model and not the measurement.

## gwosc/ — sonifications, not used by the game

Four sound files published by GWOSC alongside the event pages, copied here
**unmodified**. All are 4.00 s at 4096 Hz, which happens to be exactly the
game's slot length.

| File | What it is |
|---|---|
| `GW150914_H1_whitenbp.wav` | GW150914 as actually measured by LIGO-Hanford, whitened and band-passed |
| `GW150914_template_shifted.wav` | the matched-filter template for GW150914, frequency-shifted upward to be audible |
| `GW151226_template_shifted.wav` | the same for GW151226 |
| `GW170104_template_shifted.wav` | the same for GW170104 |

- Source: [GWOSC](https://gwosc.org/audio/), event pages for GW150914, GW151226
  and GW170104
- Licence: **CC BY 4.0**, with the acknowledgement quoted above

The templates are *models*, not data, which is why the game's card uses real H1
strain instead. They are worth knowing about anyway: because a template carries
no noise, **`GW151226_template_shifted.wav` shows a clean rising chirp in the
game's spectrogram**, the textbook curve that the real-strain card cannot show.
Pointing the `gw` descriptor at it is a one-line change, and it would make the
card easy and beautiful at the cost of showing a simulation rather than a
measurement.
