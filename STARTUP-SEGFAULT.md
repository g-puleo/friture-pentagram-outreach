# Friture startup segfault — handoff

Status: unresolved. You have direct access to the affected machine; the previous
agent did not, and worked only from the source in this repo.

## Symptom

`uv run python main.py` dies with SIGSEGV (exit 139) during startup, before any
window appears. Measured over 5 consecutive runs: **4 × exit 139, 1 × exit 0**.
The exit-0 run is unexplained — nothing in `main()` (`friture/analyzer.py:394`)
exits early, and a GUI app left alone should have hit the 20 s `timeout` and
returned 124.

Machine: Ubuntu, deps via `uv sync`, `libportaudio2` + `libxcb-cursor0`
installed. PortAudio reports **7 input and 15 output devices**, which is high
and suggests ALSA pseudo-devices or PipeWire nodes.

## Established facts

1. It is a **native crash, not a Python exception**. The device loop at
   `friture/audiobackend.py:100` wraps everything in `except Exception` and logs
   `"Failed to open stream"` (`audiobackend.py:108`). That line never appears,
   and Python cannot catch SIGSEGV.
2. The last line logged is `"Found 7 input devices and 15 output devices"`
   (`audiobackend.py:87`).
3. `"Opening the stream for device '%s'"` (`audiobackend.py:347`) does **not**
   appear on the console.
4. No stale Friture process holds the audio device: `pgrep -af "python.*main.py"`
   returns nothing; `fuser -v /dev/snd/*` shows only `controlC0` and `seq`, which
   is normal for PipeWire/PulseAudio. Those are not PCM capture nodes.
5. An earlier theory that it only crashes without `| tee` is **disproved** — the
   teed command had itself segfaulted, and the 5-run test above used no pipe and
   still gave mixed results.

## Inference (unconfirmed)

From facts 2 and 3, the crash was deduced to be at `audiobackend.py:345`, inside
`sounddevice.check_input_settings()` — the call that sits between the two log
lines. That probe validates 12 combinations of sample rate and format, each
requesting `device['max_input_channels']` channels.

Acting on that, commit `c4f65ee` made the probe opt-in behind
`FRITURE_PROBE_FORMATS`, since it is purely diagnostic and nothing reads its
result. **The crash reportedly persists after pulling that commit**, which either
means the inference was wrong, or the commit is not actually present on the
machine. That has not been checked.

## Not yet collected — get these first

The previous agent asked three times and never received them.

1. **The faulthandler stack.** This settles the whole question in one line:
   ```
   uv run python -X faulthandler main.py > /tmp/f.log 2>&1; echo $?
   sed -n '/Fatal Python error/,/Extension modules/p' /tmp/f.log
   ```
2. **Confirm the patch is on the machine:**
   `grep -n FRITURE_PROBE_FORMATS friture/audiobackend.py`
3. **Friture's own log file**, which is DEBUG level while the console is INFO, so
   it may contain lines the console never showed — in particular whether
   `"Opening the stream"` was reached after all, which would invalidate the
   inference above:
   ```
   uv run python -c "import platformdirs,os;print(os.path.join(platformdirs.user_log_dir('Friture',''),'friture.log.txt'))"
   ```
4. **The device table**, from the probe script below. `open_stream` requests every
   channel a device advertises (`audiobackend.py:353`) at a hardcoded 48 kHz
   (`SAMPLING_RATE`, `audiobackend.py:32`). A device claiming 32/64/128 input
   channels is a strong candidate.

## Probe script

Mirrors `open_stream` exactly but prints and flushes before each PortAudio call,
so **the last line printed names the call that crashes** — no traceback needed.
Run it several times; the fault is intermittent.

```bash
cat > /tmp/probe.py <<'EOF'
import sys
def s(m): print("STEP:" + m, flush=True)
s(" import sounddevice"); import sounddevice as sd
s(" import rtmixer");     import rtmixer
s(" query_devices");      devs = sd.query_devices()
for i, d in enumerate(devs):
    print("   [%2d] in=%-3d out=%-3d %-9s %s | %s" % (i, d['max_input_channels'],
          d['max_output_channels'], d['default_samplerate'], d['name'],
          sd.query_hostapis(d['hostapi'])['name']), flush=True)
s(" query default input")
try:
    dflt = sd.query_devices(kind='input'); dflt = dict(dflt, index=devs.index(dflt))
except Exception as e:
    print("  failed:", e, flush=True); dflt = None
order = ([dflt] if dflt else []) + [dict(d, index=i)
         for i, d in enumerate(devs) if d['max_input_channels'] > 0]
for d in order:
    idx, ch = d['index'], d['max_input_channels']
    print("\n=== device %d '%s' (%d ch) ===" % (idx, d['name'], ch), flush=True)
    s("  check_input_settings 48000 float32")
    try:
        sd.check_input_settings(device=idx, channels=ch, dtype='float32', samplerate=48000)
        print("    accepted", flush=True)
    except Exception as e:
        print("    rejected: %s" % e, flush=True)
    s("  rtmixer.Recorder(blocksize=512, samplerate=48000)")
    try:
        st = rtmixer.Recorder(device=idx, channels=ch, blocksize=512, samplerate=48000)
    except Exception as e:
        print("    failed: %s" % e, flush=True); continue
    s("  stream.start()")
    try:
        st.start()
    except Exception as e:
        print("    failed: %s" % e, flush=True); continue
    print("  STARTED OK, latency %.1f ms" % (1000 * st.latency), flush=True)
    st.stop(); break
print("\nDONE", flush=True)
EOF
uv run python /tmp/probe.py; echo "exit: $?"
```

## How to read the result

| Crash site | Meaning | Fix direction |
|---|---|---|
| `check_input_settings` | `c4f65ee` targeted the right call; verify it is present and effective | Keep the probe disabled |
| `rtmixer.Recorder` / `stream.start` | `c4f65ee` fixed nothing real | Skip the offending device in `get_input_devices` (`audiobackend.py:221`), or cap the requested channel count at `audiobackend.py:353` |
| Probe always clean while Friture crashes | Fault is elsewhere in startup | Bisect `Friture.__init__` in `analyzer.py` |

Also worth testing whether the device list is stable, since PipeWire enumerates
dynamically and that would be a concrete mechanism for the intermittency:

```bash
for i in 1 2 3; do uv run python -c "import sounddevice;print(len(sounddevice.query_devices()))"; done
```

## Repo state

Branch `master`, 3 commits ahead of `origin/master` (`origin` is upstream
tlecomte/friture, not a fork):

- `c4f65ee` fix(audio): make the input format probe opt-in ← the attempted fix
- `44fd023` overlay pentagram on the spectrogram (unrelated, user's work)
- `4764127` feat(outreach): add bilingual spectrogram matching game (unrelated)

Note: this bug does **not** block the outreach event. `outreach/che-suono-e.offline.html`
is a self-contained browser page needing no Python, no PortAudio and no network.
