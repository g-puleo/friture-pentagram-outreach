#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

"""Regenerate sounds/gw170817-h1.ogg from the real LIGO open data.

Downloads the 32 s, 4096 Hz LIGO-Hanford strain file around GW170817 from
GWOSC, whitens it by the Hanford amplitude spectral density estimated from
that same stretch, band-passes it, and speeds it up so the audible part fits
the four-second slot the game uses.

Hanford rather than Livingston: the Livingston data contains the well known
instrumental glitch about 1.1 s before the merger, which the GW Open Data
Workshop tutorials remove with TimeSeries.gate().

    pip install numpy h5py          # plus ffmpeg on PATH
    python3 outreach/make-gw170817.py

Data: LIGO/Virgo/KAGRA Gravitational Wave Open Science Center, CC BY 4.0.
"""

from __future__ import annotations

import os
import subprocess
import sys
import urllib.request
import wave

import h5py
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sounds", "gw170817-h1.ogg")
CACHE = os.path.join(HERE, "H-H1_GWOSC_4KHZ_R1-1187008867-32.hdf5")
URL = ("https://gwosc.org/eventapi/json/GWTC-1-confident/GW170817/v3/"
       "H-H1_GWOSC_4KHZ_R1-1187008867-32.hdf5")

T_MERGER_GPS = 1187008882.4     # GW170817 coalescence
BAND = (30.0, 400.0)            # Hz, the band where the BNS inspiral lives
BAND_TAPER = 8.0                # Hz of raised-cosine on each band edge
PSD_SECONDS = 4                 # Welch segment length
WINDOW_SECONDS = 12             # of real time, ending just after the merger
SPEEDUP = 3                     # 12 s of data -> a 4 s clip, pitched up 3x
# The window starts 4 s into the file rather than at sample zero: the whitening
# and band-pass filters ring at the edges of the data, and that transient would
# otherwise show up as a bright stripe down the left of the spectrogram.


def welch_psd(x: np.ndarray, fs: int, nperseg: int):
    """One-sided PSD, Hann windows, 50% overlap."""
    win = np.hanning(nperseg)
    acc = np.zeros(nperseg // 2 + 1)
    n = 0
    for start in range(0, len(x) - nperseg + 1, nperseg // 2):
        acc += np.abs(np.fft.rfft(x[start:start + nperseg] * win)) ** 2
        n += 1
    psd = acc / n * 2.0 / (fs * np.sum(win ** 2))
    return np.fft.rfftfreq(nperseg, 1.0 / fs), psd


def whiten(x: np.ndarray, freqs: np.ndarray, psd: np.ndarray, dt: float) -> np.ndarray:
    """Divide by the amplitude spectral density (the LOSC tutorial convention)."""
    f = np.fft.rfftfreq(len(x), dt)
    norm = 1.0 / np.sqrt(1.0 / (dt * 2))
    return np.fft.irfft(np.fft.rfft(x) / np.sqrt(np.interp(f, freqs, psd)) * norm, n=len(x))


def bandpass(x: np.ndarray, dt: float, lo: float, hi: float, taper: float) -> np.ndarray:
    """Raised-cosine band-pass in the frequency domain, to avoid ringing."""
    f = np.fft.rfftfreq(len(x), dt)
    g = np.zeros_like(f)
    g[(f >= lo) & (f <= hi)] = 1.0
    for a, b, rising in ((lo - taper, lo, True), (hi, hi + taper, False)):
        m = (f > a) & (f < b)
        r = (f[m] - a) / (b - a)
        g[m] = 0.5 * (1 - np.cos(np.pi * r)) if rising else 0.5 * (1 + np.cos(np.pi * r))
    return np.fft.irfft(np.fft.rfft(x) * g, n=len(x))


def write_wav(path: str, x: np.ndarray, rate: int) -> None:
    w = wave.open(path, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(int(rate))
    w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    w.close()


def main() -> int:
    if not os.path.exists(CACHE):
        print("downloading %s" % URL)
        urllib.request.urlretrieve(URL, CACHE)

    with h5py.File(CACHE, "r") as f:
        strain = f["strain/Strain"][()]
        duration = int(f["meta/Duration"][()])
        gps_start = int(f["meta/GPSstart"][()])
        detector = f["meta/Detector"][()].decode()

    fs = len(strain) // duration
    dt = 1.0 / fs
    t_merger = T_MERGER_GPS - gps_start
    print("%s: %d s at %d Hz, merger at t=%.2f s" % (detector, duration, fs, t_merger))

    freqs, psd = welch_psd(strain, fs, PSD_SECONDS * fs)
    x = bandpass(whiten(strain, freqs, psd, dt), dt, BAND[0], BAND[1], BAND_TAPER)

    # the window ends just after the merger, so the clip builds to the coalescence
    end = int(min(len(x), (t_merger + WINDOW_SECONDS - t_merger % 1) * fs))
    seg = x[max(0, end - WINDOW_SECONDS * fs):end].copy()
    peak = np.abs(seg).max()
    if peak > 0:
        seg /= peak
    print("clip: %.1f s of real time -> %.2f s at %dx, band %g-%g Hz -> %g-%g Hz"
          % (len(seg) / fs, len(seg) / fs / SPEEDUP, SPEEDUP,
             BAND[0], BAND[1], BAND[0] * SPEEDUP, BAND[1] * SPEEDUP))

    tmp = os.path.join(HERE, "_gw_tmp.wav")
    write_wav(tmp, seg, fs * SPEEDUP)     # declaring a higher rate *is* the speed-up
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp,
                    "-ar", "22050", "-ac", "1", "-c:a", "libvorbis", "-q:a", "5", OUT],
                   check=True)
    os.remove(tmp)
    print("wrote %s (%.0f KB)" % (os.path.relpath(OUT, HERE), os.path.getsize(OUT) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
