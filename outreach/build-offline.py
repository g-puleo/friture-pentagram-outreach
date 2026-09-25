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

"""Build the single-file offline version of the spectrogram game.

che-suono-e.html pulls IBM Plex from Google Fonts and reads its two real
recordings from sounds/. Neither works at an outreach event: the machine often
has no network, and browsers refuse to fetch sounds/ when the page is opened
straight from disk as a file:// URL.

This embeds both — the latin and latin-ext font subsets, downloaded once, and
the recordings from sounds/ — as data: URIs, producing a page that needs
nothing but a browser.

    python3 outreach/build-offline.py

Writes che-suono-e.offline.html next to the source. Requires a network
connection at build time only.
"""

from __future__ import annotations

import base64
import io
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "che-suono-e.html")
TARGET = os.path.join(HERE, "che-suono-e.offline.html")

# Google serves one @font-face per unicode subset; these two cover Italian and
# English, and dropping the rest saves about 1.5 MB.
SUBSETS = ("latin", "latin-ext")

# a real browser UA, or the API answers with .ttf instead of the smaller .woff2
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

LINK_RE = re.compile(
    r'[ \t]*<link rel="preconnect" href="https://fonts\.googleapis\.com">\n'
    r'[ \t]*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\n'
    r'[ \t]*<link rel="stylesheet" href="(?P<url>https://fonts\.googleapis\.com/css2\?[^"]+)">\n')

FACE_RE = re.compile(r"/\*\s*(?P<subset>[\w-]+)\s*\*/\s*(?P<face>@font-face\s*\{.*?\})", re.S)
AUDIO_RE = re.compile(r'src: "(?P<path>sounds/[^"]+)"')
AUDIO_TYPES = {".ogg": "audio/ogg", ".mp3": "audio/mpeg", ".wav": "audio/wav",
               ".flac": "audio/flac", ".m4a": "audio/mp4", ".opus": "audio/ogg"}
WOFF2_RE = re.compile(r"url\((?P<url>https://fonts\.gstatic\.com/[^)]+\.woff2)\)\s*format\('woff2'\)")


def fetch(url: str) -> bytes:
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()


def inline_fonts(css_url: str) -> str:
    css = fetch(css_url).decode("utf-8")
    faces, cache, raw = [], {}, 0

    for match in FACE_RE.finditer(css):
        if match.group("subset") not in SUBSETS:
            continue
        woff2 = WOFF2_RE.search(match.group("face"))
        if woff2 is None:
            continue
        url = woff2.group("url")
        if url not in cache:
            data = fetch(url)
            raw += len(data)
            cache[url] = base64.b64encode(data).decode("ascii")
        faces.append(WOFF2_RE.sub(
            "url(data:font/woff2;base64,%s) format('woff2')" % cache[url], match.group("face")))

    if not faces:
        raise SystemExit("no @font-face rules matched subsets %s" % (SUBSETS,))
    print("  %d faces, %d files, %.0f KB of woff2" % (len(faces), len(cache), raw / 1024))
    return "\n".join(faces)


def inline_audio(html: str) -> str:
    """Replace each  src: "sounds/x.ogg"  with the file as a data: URI."""
    total = [0, 0]

    def swap(match: "re.Match[str]") -> str:
        rel = match.group("path")
        path = os.path.join(HERE, rel)
        ext = os.path.splitext(path)[1].lower()
        if ext not in AUDIO_TYPES:
            raise SystemExit("unknown audio type for %s" % rel)
        with open(path, "rb") as fh:
            data = fh.read()
        total[0] += 1
        total[1] += len(data)
        print("  %s (%.0f KB)" % (rel, len(data) / 1024))
        return 'src: "data:%s;base64,%s"' % (AUDIO_TYPES[ext],
                                             base64.b64encode(data).decode("ascii"))

    out = AUDIO_RE.sub(swap, html)
    if total[0] == 0:
        raise SystemExit("no sounds/ references found; has the page changed?")
    print("  %d recordings, %.0f KB" % (total[0], total[1] / 1024))
    return out


def main() -> int:
    print("reading %s" % os.path.relpath(SOURCE))
    html = io.open(SOURCE, encoding="utf-8").read()

    link = LINK_RE.search(html)
    if link is None:
        raise SystemExit("could not find the Google Fonts <link> block in %s" % SOURCE)

    print("embedding fonts from Google Fonts")
    style = "<style>\n%s\n</style>\n" % inline_fonts(link.group("url"))
    html = html[:link.start()] + style + html[link.end():]

    if "https://fonts." in html:
        raise SystemExit("a font request survived; the page would still need a network")

    print("embedding recordings from sounds/")
    html = inline_audio(html)
    if AUDIO_RE.search(html):
        raise SystemExit("a sounds/ reference survived; the page would still need them")

    io.open(TARGET, "w", encoding="utf-8").write(html)
    print("wrote %s (%.0f KB, no network required)"
          % (os.path.relpath(TARGET), os.path.getsize(TARGET) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
