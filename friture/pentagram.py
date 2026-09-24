#!/usr/bin/env python
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

"""Grand staff (pentagram) overlay for the spectrogram.

Staff lines are placed at their equal-temperament frequencies, with A4 = 440 Hz:
raising a note by one semitone multiplies its frequency by 2^(1/12).
Notes are identified by their MIDI number (A4 = 69, middle C = C4 = 60).
"""

from __future__ import annotations

import friture.plotting.frequency_scales as fscales

A4_MIDI = 69
A4_FREQUENCY = 440.

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# lines of the treble (violin) staff, from bottom to top: E4 G4 B4 D5 F5
TREBLE_LINES = [64, 67, 71, 74, 77]
# lines of the bass staff, from bottom to top: G2 B2 D3 F3 A3
BASS_LINES = [43, 47, 50, 53, 57]
# central ledger line between the two staves
MIDDLE_C = 60

# pentagram mode shows two octaves on each side of middle C, on a log2 scale
PENTAGRAM_SCALE = fscales.OctaveC


def note_frequency(midi: int) -> float:
    return A4_FREQUENCY * 2. ** ((midi - A4_MIDI) / 12.)


def note_name(midi: int) -> str:
    return "%s%d" % (NOTE_NAMES[midi % 12], midi // 12 - 1)


# pentagram mode uses a longer FFT window than the settings, for narrower
# frequency bins: at 48 kHz, 4096 -> 8192 points gives 5.9 Hz instead of 11.7 Hz,
# finer than a semitone down to about G2 (98 Hz -> 104 Hz)
PENTAGRAM_FFT_SIZE_FACTOR = 2

PENTAGRAM_MINFREQ = note_frequency(36)  # C2
PENTAGRAM_MAXFREQ = note_frequency(84)  # C6


def staff_lines(minfreq: float, maxfreq: float, scale) -> list[dict]:
    """Return the visible staff lines, with their relative vertical position.

    y is 0 at minfreq (bottom of the plot) and 1 at maxfreq (top of the plot),
    computed with the same scale transform as the spectrogram image.
    """
    if minfreq > maxfreq:
        minfreq, maxfreq = maxfreq, minfreq

    trans_min = float(scale.transform(max(minfreq, 1e-20)))
    trans_max = float(scale.transform(max(maxfreq, 1e-20)))
    if trans_max == trans_min:
        return []

    notes = [(midi, "bass") for midi in BASS_LINES] \
        + [(MIDDLE_C, "middle_c")] \
        + [(midi, "treble") for midi in TREBLE_LINES]

    lines = []
    for midi, kind in notes:
        freq = note_frequency(midi)
        y = (float(scale.transform(freq)) - trans_min) / (trans_max - trans_min)
        if 0. <= y <= 1.:
            lines.append({"y": y, "kind": kind, "name": note_name(midi), "freq": freq})

    return lines
