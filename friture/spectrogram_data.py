#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 Timothée Lecomte

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

from PyQt6 import QtCore
from PyQt6.QtCore import pyqtProperty, pyqtSlot  # type: ignore

from friture.scope_data import Scope_Data

class Spectrogram_Data(Scope_Data):
    pentagram_enabled_changed = QtCore.pyqtSignal(bool)
    staff_lines_changed = QtCore.pyqtSignal()
    # emitted when the user toggles the pentagram from QML
    pentagram_toggled = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._pentagram_enabled = False
        self._staff_lines: list[dict] = []

    @pyqtProperty(bool, notify=pentagram_enabled_changed) # type: ignore
    def pentagram_enabled(self):
        return self._pentagram_enabled

    @pentagram_enabled.setter # type: ignore
    def pentagram_enabled(self, enabled):
        if self._pentagram_enabled != enabled:
            self._pentagram_enabled = enabled
            self.pentagram_enabled_changed.emit(enabled)

    @pyqtSlot(bool) # type: ignore
    def setPentagramEnabled(self, enabled):
        if self._pentagram_enabled != enabled:
            self.pentagram_enabled = enabled
            self.pentagram_toggled.emit(enabled)

    @pyqtProperty('QVariantList', notify=staff_lines_changed) # type: ignore
    def staff_lines(self):
        return self._staff_lines

    @staff_lines.setter # type: ignore
    def staff_lines(self, lines):
        if self._staff_lines != lines:
            self._staff_lines = lines
            self.staff_lines_changed.emit()
