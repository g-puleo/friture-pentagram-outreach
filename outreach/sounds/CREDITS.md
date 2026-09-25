# Sound credits

Two of the seven sounds in the game are real recordings. The other five are
synthesized by the page itself and have no source to credit.

## sneeze.ogg

A recording of two sneezes, used unmodified. The page pads it from 3.45 s to
the 4 s slot and normalises it at load time; the file itself is untouched.

- Source: Wikimedia Commons, [File:Sneezing.ogg](https://commons.wikimedia.org/wiki/File:Sneezing.ogg)
- Licence: **Public domain**

## gw170817-h1.ogg

The real gravitational wave event GW170817 — two neutron stars merging
130 million light years away, observed on 17 August 2017.

Derived from LIGO-Hanford (H1) strain data, 32 s at 4096 Hz around
GPS 1187008882.4, as published by GWOSC. Regenerate it with
`python3 outreach/make-gw170817.py`, which documents every step; in summary:

1. whitened by the Hanford amplitude spectral density, estimated by Welch's
   method over 4 s Hann segments of the same stretch of data;
2. band-passed to 30–400 Hz with raised-cosine edges;
3. the 16 s ending just after the coalescence, sped up 4×, so it fills the
   game's four-second slot and lands at 120–1600 Hz where a laptop speaker
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

`synthGW()` in the page remains as a model waveform built from the event's real
parameters, and is still used if this file cannot be loaded.
