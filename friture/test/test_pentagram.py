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

import unittest

import friture.plotting.frequency_scales as fscales
from friture.pentagram import (note_frequency, note_name, staff_lines,
                               TREBLE_LINES, BASS_LINES, MIDDLE_C,
                               PENTAGRAM_SCALE, PENTAGRAM_MINFREQ, PENTAGRAM_MAXFREQ)


class PentagramTest(unittest.TestCase):

    def test_equal_temperament(self):
        self.assertEqual(note_frequency(69), 440.)
        self.assertAlmostEqual(note_frequency(60), 261.6256, places=3)
        self.assertAlmostEqual(note_frequency(81), 880.)
        self.assertAlmostEqual(note_frequency(70) / note_frequency(69), 2 ** (1 / 12))

    def test_note_names(self):
        self.assertEqual([note_name(m) for m in TREBLE_LINES], ["E4", "G4", "B4", "D5", "F5"])
        self.assertEqual([note_name(m) for m in BASS_LINES], ["G2", "B2", "D3", "F3", "A3"])
        self.assertEqual(note_name(MIDDLE_C), "C4")

    def test_a4_in_second_space_of_treble_staff(self):
        # A4 lies between the second (G4) and third (B4) lines
        self.assertLess(note_frequency(TREBLE_LINES[1]), 440.)
        self.assertGreater(note_frequency(TREBLE_LINES[2]), 440.)

    def test_staff_lines_positions(self):
        lines = staff_lines(PENTAGRAM_MINFREQ, PENTAGRAM_MAXFREQ, PENTAGRAM_SCALE)
        self.assertEqual(len(lines), 11)
        ys = [line["y"] for line in lines]
        self.assertEqual(ys, sorted(ys))
        self.assertEqual([line["kind"] for line in lines], ["bass"] * 5 + ["middle_c"] + ["treble"] * 5)

        by_name = {line["name"]: line["y"] for line in lines}
        # C4 is the log midpoint of C2 and C6
        self.assertAlmostEqual(by_name["C4"], 0.5)
        # each semitone is 1/48 of the height (4 octaves); A3->C4 is 3, C4->E4 is 4
        self.assertAlmostEqual(by_name["C4"] - by_name["A3"], 3 / 48)
        self.assertAlmostEqual(by_name["E4"] - by_name["C4"], 4 / 48)

    def test_staff_lines_out_of_range_are_dropped(self):
        lines = staff_lines(200., 20000., fscales.Logarithmic)
        self.assertEqual([line["name"] for line in lines], ["A3", "C4", "E4", "G4", "B4", "D5", "F5"])
        self.assertEqual(staff_lines(1000., 1000., fscales.Logarithmic), [])


if __name__ == '__main__':
    unittest.main()
