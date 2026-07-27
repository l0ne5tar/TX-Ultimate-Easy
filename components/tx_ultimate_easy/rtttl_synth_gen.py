"""RTTTL synth config schemas and C++ header code generation.

Split out of __init__.py to keep the component registration code clean.
"""

import os

# ---- Constants ----
CONF_RTTTL_SYNTH = "rtttl_synth"
CONF_ENVELOPES = "envelopes"
CONF_INSTRUMENTS = "instruments"
CONF_TUNES = "tunes"
CONF_WAVEFORM = "waveform"
CONF_PULSE_DUTY = "pulse_duty"
CONF_ATTACK = "attack"
CONF_DECAY = "decay"
CONF_SUSTAIN = "sustain"
CONF_RELEASE = "release"
CONF_NOTE_DURATION = "note_duration"
CONF_VOICES = "voices"
CONF_VIBRATO_ENABLED = "vibrato"
CONF_VIBRATO_DEPTH = "vibrato_depth"
CONF_VIBRATO_RATE = "vibrato_rate"
CONF_BASE_FREQ = "base_freq"
CONF_GAIN = "gain"
CONF_SAMPLE_RATE = "sample_rate"

WAVEFORM_MAP = {
    "sine": "SynthWaveform::SINE",
    "triangle": "SynthWaveform::TRIANGLE",
    "square": "SynthWaveform::SQUARE",
    "pulse": "SynthWaveform::PULSE",
}


def _display_name(id_str):
    return id_str.replace("_", " ").title()


# ---- Config schemas ----
def build_envelope_schema(cv):
    return cv.Schema({
        cv.Required("id"): cv.string_strict,
        cv.Optional(CONF_ATTACK, default="5ms"): cv.positive_time_period_milliseconds,
        cv.Optional(CONF_DECAY, default="0ms"): cv.positive_time_period_milliseconds,
        cv.Optional(CONF_SUSTAIN, default="0.6"): cv.percentage,
        cv.Optional(CONF_RELEASE, default="30ms"): cv.positive_time_period_milliseconds,
    })


def build_instrument_schema(cv):
    return cv.Schema({
        cv.Required("id"): cv.string_strict,
        cv.Optional(CONF_WAVEFORM, default="triangle"): cv.one_of("sine", "triangle", "square", "pulse", lower=True),
        cv.Optional(CONF_PULSE_DUTY, default="0.5"): cv.percentage,
        cv.Required("envelope"): cv.string_strict,
        cv.Optional(CONF_NOTE_DURATION, default="100ms"): cv.positive_time_period_milliseconds,
        cv.Optional(CONF_BASE_FREQ, default=800): cv.int_range(20, 20000),
        cv.Optional(CONF_VOICES, default=[0]): cv.ensure_list(cv.int_range(-1200, 1200)),
        cv.Optional(CONF_VIBRATO_ENABLED, default=False): cv.boolean,
        cv.Optional(CONF_VIBRATO_DEPTH, default=0): cv.int_range(0, 200),
        cv.Optional(CONF_VIBRATO_RATE, default=5): cv.int_range(0, 100),
        cv.Optional(CONF_GAIN, default="0.5"): cv.percentage,
    })


def build_tune_schema(cv):
    return cv.Schema({
        cv.Required("id"): cv.string_strict,
        cv.Required("rtttl"): cv.string,
        cv.Optional("name"): cv.string,
    })


def build_rtttl_synth_schema(cv):
    return cv.Schema({
        cv.Optional(CONF_SAMPLE_RATE, default=16000): cv.int_range(8000, 48000),
        cv.Optional(CONF_ENVELOPES): cv.ensure_list(build_envelope_schema(cv)),
        cv.Optional(CONF_INSTRUMENTS): cv.ensure_list(build_instrument_schema(cv)),
        cv.Optional(CONF_TUNES): cv.ensure_list(build_tune_schema(cv)),
    })


# ---- C++ header generation ----
def generate_rtttl_synth_code(instruments, envelopes, tunes, sample_rate):
    """Generate rtttl_synth_data.h C++ header from the extracted config lists.

    Always writes the file so instrument_index() always has a definition.
    Returns True if instruments exist (caller uses this to set USE_RTTTL_SYNTH).
    """
    comp_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(comp_dir, "rtttl_synth_data.h")

    env_map = {e["id"]: e for e in envelopes} if envelopes else {}

    lines = []
    lines.append("#pragma once")
    lines.append('#include "tx_ultimate_easy_rtttl_synth.h"')
    lines.append("")
    lines.append("namespace esphome {")
    lines.append("namespace tx_ultimate_easy {")
    lines.append("")
    lines.append("// -- RTTTL synth data (auto-generated) --")
    lines.append("")

    # Counts (always emitted so selects / instrument_index can reference them)
    lines.append(f"static const size_t rtttl_synth_instrument_count = {len(instruments)};")
    lines.append(f"static const size_t rtttl_synth_tune_count = {len(tunes)};")
    lines.append(f"static const int rtttl_synth_sample_rate = {sample_rate};")
    lines.append("")

    # Voice arrays (only needed when instruments exist)
    voice_arrays = []
    if instruments:
        for idx, instr in enumerate(instruments):
            voices = instr[CONF_VOICES]
            arr_name = f"v{idx}"
            cents_str = ", ".join(f"{float(v)}f" for v in voices)
            lines.append(f"static const float {arr_name}[] = {{ {cents_str} }};")
            voice_arrays.append((arr_name, len(voices)))
        lines.append("")

    # Instrument array — always declared (zero-size when empty) so non-template
    # code can resolve the name even when if constexpr discards the branch.
    lines.append("static const RtttlSynthInstrument rtttl_synth_instruments[] = {")
    for idx, instr in enumerate(instruments):
        wf = WAVEFORM_MAP[instr[CONF_WAVEFORM]]
        duty = instr[CONF_PULSE_DUTY]
        env_id = instr["envelope"]

        if env_id in env_map:
            env = env_map[env_id]
            a = float(env[CONF_ATTACK].milliseconds)
            d = float(env[CONF_DECAY].milliseconds)
            s = float(env[CONF_SUSTAIN])
            r = float(env[CONF_RELEASE].milliseconds)
        else:
            print(f"WARNING: Envelope '{env_id}' not found for instrument '{instr['id']}', using defaults")
            a, d, s, r = 5.0, 0.0, 0.6, 30.0

        dur = float(instr[CONF_NOTE_DURATION].milliseconds)
        freq = float(instr[CONF_BASE_FREQ])
        varr, vcnt = voice_arrays[idx]
        vib = "true" if instr[CONF_VIBRATO_ENABLED] else "false"
        vdepth = float(instr[CONF_VIBRATO_DEPTH])
        vrate = float(instr[CONF_VIBRATO_RATE])
        gain = float(instr[CONF_GAIN])

        lines.append(f'  {{')
        lines.append(f'    "{_display_name(instr["id"])}",')
        lines.append(f'    {wf},')
        lines.append(f'    {duty}f,')
        lines.append(f'    {{{a}f, {d}f, {s}f, {r}f}},')
        lines.append(f'    {dur}f,')
        lines.append(f'    {freq}f,')
        lines.append(f'    {varr}, {vcnt},')
        lines.append(f'    {vib}, {vdepth}f, {vrate}f, {gain}f')
        lines.append(f'  }},')
    lines.append("};")
    lines.append("")

    # Lookup helper - always emitted (iterates empty array when count is 0)
    lines.append("static const RtttlSynthInstrument *find_instrument(const char *name) {")
    lines.append("  for (auto &inst : rtttl_synth_instruments) {")
    lines.append("    if (strcmp(inst.name, name) == 0) return &inst;")
    lines.append("  }")
    lines.append("  return nullptr;")
    lines.append("}")
    lines.append("")

    # Tune array — always declared (zero-size when empty)
    lines.append("static const RtttlSynthTune rtttl_synth_tunes[] = {")
    for tune in tunes:
        rtttl_escaped = tune["rtttl"].replace('"', '\\"')
        name = tune.get("name") or _display_name(tune["id"])
        lines.append(f'  {{"{name}", "{rtttl_escaped}"}},')
    lines.append("};")
    lines.append("")

    lines.append("static const RtttlSynthTune *find_tune(const char *name) {")
    lines.append("  for (auto &t : rtttl_synth_tunes) {")
    lines.append("    if (strcmp(t.name, name) == 0) return &t;")
    lines.append("  }")
    lines.append("  return nullptr;")
    lines.append("}")
    lines.append("")

    # instrument_index() definition — after all arrays so references compile.
    # if constexpr guards the no-instrument case (avoids referencing undeclared array).
    lines.append("inline int RtttlSynth::instrument_index(const std::string &name) {")
    lines.append("  if constexpr (rtttl_synth_instrument_count > 0) {")
    lines.append("    for (size_t i = 0; i < rtttl_synth_instrument_count; i++) {")
    lines.append("      if (name == rtttl_synth_instruments[i].name) return static_cast<int>(i);")
    lines.append("    }")
    lines.append("  }")
    lines.append("  return 0;")
    lines.append("}")

    lines.append("")
    lines.append("}  // namespace tx_ultimate_easy")
    lines.append("}  // namespace esphome")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    return len(instruments) > 0
