#!/usr/bin/env python3
"""
AI词曲创作引擎 V2.5 - Audio Demo Generator
Converts Layer 4 JSON metadata to MIDI + HTML player demo.
Supports three JSON formats: structure nested, sections array, and flat.

Usage:
  python generate_demo.py --json song.json --output-dir ./output
  echo '{"song_title":"..."}' | python generate_demo.py --output-dir ./output

Dependencies:
  mido (pip install mido) - for MIDI generation (optional, HTML works without it)
"""

import json
import os
import sys
import argparse
import re
import math

try:
    from mido import MidiFile, MidiTrack, Message, MetaMessage
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

# ==================== Note & Chord Maps ====================

NOTE_BASE = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}

CHORD_INTERVALS = {
    "":     [0, 4, 7],        # Major triad
    "m":    [0, 3, 7],        # Minor triad
    "7":    [0, 4, 7, 10],    # Dominant 7th
    "maj7": [0, 4, 7, 11],    # Major 7th
    "m7":   [0, 3, 7, 10],    # Minor 7th
    "dim":  [0, 3, 6],        # Diminished
    "dim7": [0, 3, 6, 9],     # Diminished 7th
    "sus4": [0, 5, 7],        # Suspended 4th
    "sus2": [0, 2, 7],        # Suspended 2nd
    "add9": [0, 4, 7, 14],    # Added 9th
    "5":    [0, 7],           # Power chord
    "9":    [0, 4, 7, 10, 14],# 9th
    "m9":   [0, 3, 7, 10, 14],# Minor 9th
    "6":    [0, 4, 7, 9],     # 6th
    "m6":   [0, 3, 7, 9],     # Minor 6th
}

# Drum patterns: 16 steps per bar (4/4 time)
DRUM_PATTERNS = {
    "pop": {
        "kick":  [1,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
        "snare": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "hihat": [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
    },
    "hip_hop": {
        "kick":  [1,0,0,0, 0,0,1,0, 0,0,0,0, 1,0,0,0],
        "snare": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "hihat": [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
    },
    "folk": {
        "kick":  [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
        "snare": [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
        "hihat": [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
    },
    "electronic": {
        "kick":  [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
        "snare": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "hihat": [0,1,0,1, 0,1,0,1, 0,1,0,1, 0,1,0,1],
    },
}

# MIDI drum notes
DRUM_MIDI = {"kick": 36, "snare": 38, "hihat": 42}

# Default bars per section type
BARS_PER_SECTION = {
    "intro": 4, "verse": 8, "verse_1": 8, "verse_2": 8,
    "pre_chorus": 4, "pre": 4, "chorus": 8,
    "bridge": 4, "outro": 4, "hook": 4,
    "drop": 8, "build": 4,
}

# Song form template: (lyrics_keys, chord_keys, bars, label)
SONG_FORM_TEMPLATE = [
    (["verse_1", "verse1", "verse"], ["verse", "verse_1"], 8, "Verse 1"),
    (["pre_chorus", "prechorus", "pre"], ["pre_chorus", "pre"], 4, "Pre-Chorus"),
    (["chorus"], ["chorus"], 8, "Chorus"),
    (["verse_2", "verse2"], ["verse", "verse_2"], 8, "Verse 2"),
    (["bridge"], ["bridge"], 4, "Bridge"),
    (["chorus"], ["chorus"], 8, "Chorus"),
    (["outro"], ["outro"], 4, "Outro"),
]

# Structure format: fixed section ordering and metadata
STRUCTURE_KEY_ORDER = ["verse1", "chorus", "verse2", "bridge", "outro"]
STRUCTURE_KEY_LABEL = {
    "verse1": "Verse 1", "verse2": "Verse 2",
    "chorus": "Chorus", "bridge": "Bridge", "outro": "Outro",
    "intro": "Intro", "pre_chorus": "Pre-Chorus", "pre": "Pre-Chorus",
    "hook": "Hook", "drop": "Drop", "build": "Build",
}
STRUCTURE_KEY_BARS = {
    "verse1": 8, "verse2": 8, "chorus": 8,
    "bridge": 4, "outro": 4, "intro": 4,
    "pre_chorus": 4, "pre": 4, "hook": 4, "drop": 8, "build": 4,
}


# ==================== Parsing Functions ====================

def parse_key(key_str):
    """Parse key string to root note name and mode.
    'A minor / C major' -> ('A', 'minor')
    'Am' -> ('A', 'minor')
    """
    if not key_str:
        return "A", "minor"
    key_str = key_str.strip()
    if "/" in key_str:
        key_str = key_str.split("/")[0].strip()
    parts = key_str.split()
    if len(parts) >= 2:
        root = parts[0]
        mode = parts[1].lower()
        return root, "minor" if "min" in mode or mode == "m" else "major"
    if key_str.endswith("m"):
        return key_str[:-1], "minor"
    return key_str, "major"


def parse_chord(chord_str):
    """Parse chord symbol to MIDI notes (octave 3 root).
    'Am' -> [57, 60, 64]
    'F' -> [53, 57, 60]
    'G7' -> [55, 59, 62, 65]
    """
    chord_str = chord_str.strip()
    if "/" in chord_str:
        chord_str = chord_str.split("/")[0].strip()
    if not chord_str:
        return [60, 64, 67]

    # Try 2-char root (C#, Db, etc.)
    root = None
    quality = ""
    for rlen in [2, 1]:
        if len(chord_str) >= rlen and chord_str[:rlen] in NOTE_BASE:
            root = chord_str[:rlen]
            quality = chord_str[rlen:]
            break

    if root is None:
        return [60, 64, 67]

    intervals = CHORD_INTERVALS.get(quality)
    if intervals is None:
        # Try matching known suffixes
        for suffix in ["maj7", "m7", "dim7", "dim", "sus4", "sus2", "add9", "m9", "9", "7", "m", "6", "5"]:
            if quality == suffix:
                intervals = CHORD_INTERVALS[suffix]
                break
        if intervals is None:
            intervals = [0, 4, 7]

    root_midi = 48 + NOTE_BASE[root]
    return [root_midi + i for i in intervals]


def parse_chord_progression(prog):
    """Parse chord progression string to list of chord symbols.
    'vi-IV-I-V (Am-F-C-G)' -> ['Am', 'F', 'C', 'G']
    'Am-F-C-G' -> ['Am', 'F', 'C', 'G']
    ['Am','F'] -> ['Am', 'F']
    """
    if isinstance(prog, list):
        return prog
    if not isinstance(prog, str):
        return []

    match = re.search(r'\(([^)]+)\)', prog)
    if match:
        chord_str = match.group(1)
    else:
        chord_str = prog

    parts = re.split(r'[-,\s>+]+', chord_str.strip())
    chords = []
    for p in parts:
        p = p.strip()
        if p and p[0] in "ABCDEFGabcdefg#b":
            chords.append(p)

    return chords if chords else []


def parse_melody(melody_str, key_root_name="A"):
    """Parse melody note names to MIDI notes using nearest octave.
    'A-C-D-C-A-G-A' -> [69, 72, 74, 72, 69, 67, 69]
    """
    if not melody_str:
        return []

    note_names = re.split(r'[-,\s>+]+', melody_str.strip())
    note_names = [n.strip() for n in note_names if n.strip()]

    midi_notes = []
    prev = 60 + NOTE_BASE.get(key_root_name, 9)

    for name in note_names:
        if name not in NOTE_BASE:
            continue
        base = 60 + NOTE_BASE[name]
        while base < prev - 6:
            base += 12
        while base > prev + 6:
            base -= 12
        midi_notes.append(base)
        prev = base

    return midi_notes


def parse_lyrics(lyrics_str):
    """Parse lyrics string to list of lines.
    'line1 / line2 / line3' -> ['line1', 'line2', 'line3']
    """
    if isinstance(lyrics_str, list):
        return lyrics_str
    if not isinstance(lyrics_str, str):
        return []

    lines = re.split(r'\s*/\s*', lyrics_str.strip())
    cleaned = []
    for line in lines:
        line = line.strip()
        line = re.sub(r'[\u3010\u3011].*?[\u3010\u3011]', '', line)
        line = re.sub(r'【.*?】', '', line).strip()
        if line:
            cleaned.append(line)

    return cleaned


# ==================== Song Building ====================

def build_song_form(song_data):
    """Build ordered song form from JSON sections.

    Supports three JSON formats (checked in order):
    1. structure nested: {"structure": {"verse1": {"lyrics":[...], "chord_progression":[...]}, ...}}
    2. sections array:   {"sections": [{"label":"Verse 1", "lyrics":[...], "chord_progression":[...]}, ...]}
    3. flat:             {"lyrics": {"verse1":"..."}, "chord_progression": {"verse1":"..."}}
    """
    key_root, mode = parse_key(song_data.get("key", "Am"))

    # --- Format 1: structure nested format ---
    structure = song_data.get("structure")
    if structure and isinstance(structure, dict):
        form = _build_form_from_structure(structure)
        if form:
            return form, key_root, mode

    # --- Format 2: sections array format ---
    sections = song_data.get("sections")
    if sections and isinstance(sections, list):
        form = _build_form_from_sections(sections)
        if form:
            return form, key_root, mode

    # --- Format 3: flat format (original) ---
    lyrics = song_data.get("lyrics", {})
    chords = song_data.get("chord_progression", song_data.get("chord_progressions", {}))

    form = []
    for lyrics_keys, chord_keys, default_bars, label in SONG_FORM_TEMPLATE:
        lyric_text = None
        for lk in lyrics_keys:
            if lk in lyrics and lyrics[lk]:
                lyric_text = lyrics[lk]
                break

        chord_prog = None
        for ck in chord_keys:
            if ck in chords and chords[ck]:
                chord_prog = chords[ck]
                break

        if lyric_text or chord_prog:
            bars = BARS_PER_SECTION.get(lyrics_keys[0], default_bars)
            form.append({
                "label": label,
                "lyrics": parse_lyrics(lyric_text) if lyric_text else [],
                "chords": parse_chord_progression(chord_prog) if chord_prog else [],
                "bars": bars,
            })

    return form, key_root, mode


def _build_form_from_structure(structure):
    """Parse structure nested format.

    Expected:
        {"verse1": {"lyrics": [...], "chord_progression": [...]}, "chorus": {...}, ...}

    Builds: Intro(auto) -> Verse 1 -> [Pre-Chorus] -> Chorus -> Verse 2 -> Bridge -> Chorus(repeat) -> Outro
    """
    # Collect existing sections
    found = {}
    for key in STRUCTURE_KEY_ORDER:
        sec = structure.get(key)
        if sec and isinstance(sec, dict):
            found[key] = sec
    # Pre-chorus variants
    for pk in ["pre_chorus", "pre"]:
        sec = structure.get(pk)
        if sec and isinstance(sec, dict):
            found[pk] = sec
            break

    if not found:
        return []

    def _extract_chords(sec_data):
        return (sec_data.get("chord_progression")
                or sec_data.get("chords")
                or sec_data.get("chord_prog"))

    def _make_entry(key, sec_data, label_override=None):
        lyrics_raw = sec_data.get("lyrics", [])
        chords_raw = _extract_chords(sec_data)
        return {
            "label": label_override or STRUCTURE_KEY_LABEL.get(key, key.replace("_", " ").title()),
            "lyrics": parse_lyrics(lyrics_raw) if lyrics_raw else [],
            "chords": parse_chord_progression(chords_raw) if chords_raw else [],
            "bars": STRUCTURE_KEY_BARS.get(key, 8),
        }

    form = []

    # 1. Auto Intro from first available chords
    for key in STRUCTURE_KEY_ORDER:
        if key in found:
            cp = _extract_chords(found[key])
            if cp:
                form.append({
                    "label": "Intro",
                    "lyrics": [],
                    "chords": parse_chord_progression(cp),
                    "bars": STRUCTURE_KEY_BARS["intro"],
                })
                break

    # 2. Verse 1
    if "verse1" in found:
        form.append(_make_entry("verse1", found["verse1"]))

    # 3. Pre-Chorus (optional)
    pre_key = "pre_chorus" if "pre_chorus" in found else ("pre" if "pre" in found else None)
    if pre_key:
        form.append(_make_entry(pre_key, found[pre_key], "Pre-Chorus"))

    # 4. Chorus (first)
    if "chorus" in found:
        form.append(_make_entry("chorus", found["chorus"]))

    # 5. Verse 2
    if "verse2" in found:
        form.append(_make_entry("verse2", found["verse2"]))

    # 6. Bridge
    if "bridge" in found:
        form.append(_make_entry("bridge", found["bridge"]))

    # 7. Chorus repeat after bridge
    if "chorus" in found and "bridge" in found:
        form.append(_make_entry("chorus", found["chorus"]))

    # 8. Outro
    if "outro" in found:
        form.append(_make_entry("outro", found["outro"]))

    return form


def _build_form_from_sections(sections):
    """Parse sections array format.

    Expected: [{"label": "Verse 1", "lyrics": [...], "chord_progression": [...]}, ...]
    """
    form = []
    for sec in sections:
        if not isinstance(sec, dict):
            continue

        label = sec.get("label", sec.get("name", sec.get("section", "Section")))
        lyrics_raw = sec.get("lyrics", [])
        chords_raw = (sec.get("chord_progression")
                       or sec.get("chords")
                       or sec.get("chord_prog", []))
        bars = sec.get("bars", sec.get("bars_count", None))

        if not isinstance(bars, (int, float)) or bars is None:
            label_key = str(label).lower().replace(" ", "_")
            bars = BARS_PER_SECTION.get(label_key, 8)

        if lyrics_raw or chords_raw:
            form.append({
                "label": str(label),
                "lyrics": parse_lyrics(lyrics_raw) if lyrics_raw else [],
                "chords": parse_chord_progression(chords_raw) if chords_raw else [],
                "bars": bars,
            })

    return form


def build_playback_data(song_data):
    """Build complete playback data for HTML player and MIDI generation."""
    title = song_data.get("song_title", song_data.get("title", "Untitled"))
    bpm = song_data.get("bpm", 80)
    genre_raw = song_data.get("genre_pipeline", song_data.get("genre", "pop"))
    genre = genre_raw.lower() if isinstance(genre_raw, str) else "pop"
    if "hip" in genre or "rap" in genre:
        genre = "hip_hop"
    elif "folk" in genre:
        genre = "folk"
    elif "electronic" in genre or "edm" in genre or "lo-fi" in genre:
        genre = "electronic"
    else:
        genre = "pop"

    form, key_root, mode = build_song_form(song_data)

    beat_duration = 60.0 / bpm
    bar_duration = beat_duration * 4

    # Parse melody
    melody_dna = song_data.get("melody_dna", {})
    hummable = melody_dna.get("hummable_melody", "") if isinstance(melody_dna, dict) else ""
    melody_notes = parse_melody(hummable, key_root) if hummable else []

    # Get drum pattern
    drum_pattern = DRUM_PATTERNS.get(genre, DRUM_PATTERNS["pop"])

    # Build events
    events = []
    sections = []
    current_time = 0.0
    melody_idx = 0

    for section in form:
        section_start = current_time
        section_duration = section["bars"] * bar_duration
        chords = section["chords"]
        lyrics_lines = section["lyrics"]

        sections.append({
            "label": section["label"],
            "start_time": round(section_start, 3),
            "duration": round(section_duration, 3),
            "lyrics": lyrics_lines,
        })

        for bar in range(section["bars"]):
            bar_start = section_start + bar * bar_duration

            # Chord
            if chords:
                chord_symbol = chords[bar % len(chords)]
                chord_notes = parse_chord(chord_symbol)
                events.append({
                    "time": round(bar_start, 3),
                    "type": "chord",
                    "notes": chord_notes,
                    "duration": round(bar_duration * 0.95, 3),
                })

                # Bass (root note, octave 2)
                bass_note = chord_notes[0] - 12
                events.append({
                    "time": round(bar_start, 3),
                    "type": "bass",
                    "note": bass_note,
                    "duration": round(bar_duration * 0.9, 3),
                })

            # Drums (16 steps per bar)
            for step in range(16):
                step_time = bar_start + (step / 16.0) * bar_duration
                for drum_type in ["kick", "snare", "hihat"]:
                    if drum_pattern[drum_type][step]:
                        events.append({
                            "time": round(step_time, 3),
                            "type": drum_type,
                        })

            # Melody (quarter notes)
            if melody_notes:
                for beat in range(4):
                    note = melody_notes[melody_idx % len(melody_notes)]
                    note_time = bar_start + beat * beat_duration
                    events.append({
                        "time": round(note_time, 3),
                        "type": "melody",
                        "note": note,
                        "duration": round(beat_duration * 0.85, 3),
                    })
                    melody_idx += 1

        current_time += section_duration

    # Sort events by time
    events.sort(key=lambda e: e["time"])

    return {
        "title": title,
        "key": song_data.get("key", "Am"),
        "bpm": bpm,
        "genre": genre,
        "total_duration": round(current_time, 3),
        "sections": sections,
        "events": events,
    }


# ==================== MIDI Generation ====================

def generate_midi(data, output_path):
    """Generate MIDI file using mido library."""
    if not MIDO_AVAILABLE:
        print("Warning: mido not installed. Skipping MIDI generation.")
        print("Install with: pip install mido")
        return False

    bpm = data["bpm"]
    ticks_per_beat = 480
    mid = MidiFile(ticks_per_beat=ticks_per_beat)

    # Tempo track
    tempo_track = MidiTrack()
    mid.tracks.append(tempo_track)
    tempo = int(60_000_000 / bpm)
    tempo_track.append(MetaMessage("set_tempo", tempo=tempo, time=0))
    tempo_track.append(MetaMessage("time_signature", numerator=4, denominator=4, time=0))

    # Separate events by type
    chord_events = [e for e in data["events"] if e["type"] == "chord"]
    bass_events = [e for e in data["events"] if e["type"] == "bass"]
    melody_events = [e for e in data["events"] if e["type"] == "melody"]
    drum_events = [e for e in data["events"] if e["type"] in ("kick", "snare", "hihat")]

    def sec_to_tick(sec):
        return int(sec * bpm * ticks_per_beat / 60)

    # Chord track (channel 0, Acoustic Grand Piano)
    chord_track = MidiTrack()
    mid.tracks.append(chord_track)
    chord_track.append(Message("program_change", program=0, channel=0, time=0))
    _fill_melodic_track(chord_track, chord_events, "notes", bpm, ticks_per_beat, velocity=50)

    # Melody track (channel 1, Flute)
    melody_track = MidiTrack()
    mid.tracks.append(melody_track)
    melody_track.append(Message("program_change", program=73, channel=1, time=0))
    _fill_melodic_track(melody_track, melody_events, "note", bpm, ticks_per_beat, velocity=70)

    # Bass track (channel 2, Electric Bass)
    bass_track = MidiTrack()
    mid.tracks.append(bass_track)
    bass_track.append(Message("program_change", program=33, channel=2, time=0))
    _fill_melodic_track(bass_track, bass_events, "note", bpm, ticks_per_beat, velocity=60)

    # Drum track (channel 9)
    drum_track = MidiTrack()
    mid.tracks.append(drum_track)
    drum_track.append(Message("program_change", program=0, channel=9, time=0))
    _fill_drum_track(drum_track, drum_events, bpm, ticks_per_beat)

    mid.save(output_path)
    return True


def _fill_melodic_track(track, events, notes_key, bpm, tpb, velocity=64):
    """Fill a MIDI track with melodic (pitched) events."""
    tick = 0
    pending_offs = []  # (end_tick, note, channel)

    for event in events:
        event_tick = int(event["time"] * bpm * tpb / 60)

        # Process note_offs before this event
        pending_offs.sort(key=lambda x: x[0])
        while pending_offs and pending_offs[0][0] <= event_tick:
            off_tick, note, ch = pending_offs.pop(0)
            delta = off_tick - tick
            track.append(Message("note_off", note=note, velocity=64, channel=ch, time=max(0, delta)))
            tick = off_tick

        # Add note_on(s)
        notes = event[notes_key] if isinstance(event.get(notes_key), list) else [event.get(notes_key)]
        dur_ticks = int(event.get("duration", 0.5) * bpm * tpb / 60)
        ch = 0
        for i, note in enumerate(notes):
            if note is None:
                continue
            delta = (event_tick - tick) if i == 0 else 0
            track.append(Message("note_on", note=note, velocity=velocity, channel=ch, time=max(0, delta)))
            if i == 0:
                tick = event_tick
            pending_offs.append((event_tick + dur_ticks, note, ch))

    # Process remaining note_offs
    pending_offs.sort(key=lambda x: x[0])
    for off_tick, note, ch in pending_offs:
        delta = off_tick - tick
        track.append(Message("note_off", note=note, velocity=64, channel=ch, time=max(0, delta)))
        tick = off_tick


def _fill_drum_track(track, events, bpm, tpb):
    """Fill a MIDI drum track (channel 9)."""
    tick = 0
    for event in events:
        event_tick = int(event["time"] * bpm * tpb / 60)
        note = DRUM_MIDI.get(event["type"], 36)
        delta = event_tick - tick
        track.append(Message("note_on", note=note, velocity=80, channel=9, time=max(0, delta)))
        track.append(Message("note_off", note=note, velocity=64, channel=9, time=60))
        tick = event_tick + 60


# ==================== HTML Generation ====================

def generate_html(data, template_path, output_path):
    """Generate HTML player by filling in template."""
    if not os.path.exists(template_path):
        print(f"Warning: Template not found at {template_path}")
        return False

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    json_str = json.dumps(data, ensure_ascii=False)
    json_str = json_str.replace("</", "<\\/")

    html = html.replace("__SONG_TITLE__", data["title"])
    html = html.replace("__KEY_DISPLAY__", data["key"])
    html = html.replace("__BPM__", str(data["bpm"]))
    html = html.replace("__GENRE_DISPLAY__", data["genre"])
    html = html.replace("__PLAYBACK_DATA__", json_str)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return True


# ==================== Main ====================

def main():
    parser = argparse.ArgumentParser(
        description="AI词曲创作引擎 - Audio Demo Generator"
    )
    parser.add_argument("--json", help="Path to JSON metadata file")
    parser.add_argument("--json-string", help="JSON string directly")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--template", help="Custom HTML template path")
    args = parser.parse_args()

    # Load JSON
    if args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            song_data = json.load(f)
    elif args.json_string:
        song_data = json.loads(args.json_string)
    else:
        # Read from stdin
        song_data = json.load(sys.stdin)

    # Build playback data
    data = build_playback_data(song_data)

    title = data["title"]
    safe_title = re.sub(r'[^\w\u4e00-\u9fff]+', '_', title).strip("_")

    os.makedirs(args.output_dir, exist_ok=True)

    # Generate MIDI
    midi_path = os.path.join(args.output_dir, f"{safe_title}_demo.mid")
    midi_ok = generate_midi(data, midi_path)
    if midi_ok:
        print(f"MIDI generated: {midi_path}")
    else:
        print("MIDI skipped (mido not installed)")

    # Generate HTML
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = args.template or os.path.join(script_dir, "player_template.html")
    html_path = os.path.join(args.output_dir, f"{safe_title}_demo.html")
    html_ok = generate_html(data, template_path, html_path)
    if html_ok:
        print(f"HTML generated: {html_path}")
    else:
        print("HTML generation failed")

    print(f"\nDemo duration: {data['total_duration']:.1f}s ({int(data['total_duration']//60)}:{int(data['total_duration']%60):02d})")
    print(f"Events: {len(data['events'])}")
    print(f"Sections: {len(data['sections'])}")


if __name__ == "__main__":
    main()
