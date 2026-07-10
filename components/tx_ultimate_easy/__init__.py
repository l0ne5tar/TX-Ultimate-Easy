import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.components import uart
from esphome.const import (
    CONF_ID,
)
from esphome.core import CORE
import logging
import os

CODEOWNERS = ["@edwardtfn"]
DEPENDENCIES = ['uart']

CONF_TX_ULTIMATE_EASY = "tx_ultimate_easy"

CONF_UART = "uart"

CONF_DEVICE_FORMAT = "device_format"
CONF_GANG_COUNT = "gang_count"

CONF_ON_TOUCH_EVENT = "on_touch_event"
CONF_ON_PRESS = "on_press"
CONF_ON_RELEASE = "on_release"
CONF_ON_SWIPE_LEFT = "on_swipe_left"
CONF_ON_SWIPE_RIGHT = "on_swipe_right"
CONF_ON_MULTI_TOUCH_RELEASE = "on_multi_touch_release"
CONF_ON_LONG_TOUCH_RELEASE = "on_long_touch_release"

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

# Device format options
DEVICE_FORMAT_EU = "EU"
DEVICE_FORMAT_US = "US"

_LOGGER = logging.getLogger(__name__)

tx_ultimate_easy_ns = cg.esphome_ns.namespace('tx_ultimate_easy')
TouchPoint = tx_ultimate_easy_ns.struct("TouchPoint")

TxUltimateTouch = tx_ultimate_easy_ns.class_(
    'TxUltimateEasy', cg.Component, uart.UARTDevice)


def validate_gang_count(value):
    """
    Validate gang_count is an integer between 1 and 4.
    
    Parameters:
        value: The gang_count value to validate.
    
    Returns:
        int: The validated gang_count value.
    
    Raises:
        cv.Invalid: If value is not an integer or not in range 1-4.
    """
    value = cv.int_(value)
    if value < 1 or value > 4:
        raise cv.Invalid(
            f"gang_count must be between 1 and 4, got {value}\n"
            "Please set gang_count in your YAML substitutions to 1, 2, 3, or 4\n"
            "substitutions:\n"
            "  device_format: EU  # REQUIRED: 'EU' or 'US' (case-sensitive, uppercase only)\n"
            "  gang_count: 1      # REQUIRED: Number of relays/buttons (1, 2, 3, or 4)"
        )
    return value


def validate_device_format(value):
    """
    Validate device_format is either 'EU' or 'US'.
    
    Parameters:
        value: The device_format value to validate.
    
    Returns:
        str: The validated device_format value.
    
    Raises:
        cv.Invalid: If value is not 'EU' or 'US'.
    """
    value = cv.string_strict(value)
    if value not in [DEVICE_FORMAT_EU, DEVICE_FORMAT_US]:
        raise cv.Invalid(
            f"device_format must be either '{DEVICE_FORMAT_EU}' or '{DEVICE_FORMAT_US}', got '{value}'\n"
            "Please add to your YAML substitutions: device_format: EU  # Must be either 'EU' or 'US'\n"
            "substitutions:\n"
            "  device_format: EU  # REQUIRED: 'EU' or 'US' (case-sensitive, uppercase only)\n"
            "  gang_count: 1      # REQUIRED: Number of relays/buttons (1, 2, 3, or 4)"
        )
    return value


ENVELOPE_SCHEMA = cv.Schema({
    cv.Required("id"): cv.string_strict,
    cv.Optional(CONF_ATTACK, default="5ms"): cv.positive_time_period_milliseconds,
    cv.Optional(CONF_DECAY, default="0ms"): cv.positive_time_period_milliseconds,
    cv.Optional(CONF_SUSTAIN, default="0.6"): cv.percentage,
    cv.Optional(CONF_RELEASE, default="30ms"): cv.positive_time_period_milliseconds,
})

INSTRUMENT_SCHEMA = cv.Schema({
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

TUNE_SCHEMA = cv.Schema({
    cv.Required("id"): cv.string_strict,
    cv.Required("rtttl"): cv.string,
    cv.Optional("name"): cv.string,
})

RTTTL_SYNTH_SCHEMA = cv.Schema({
    cv.Optional(CONF_SAMPLE_RATE, default=16000): cv.int_range(8000, 48000),
    cv.Optional(CONF_ENVELOPES): cv.ensure_list(ENVELOPE_SCHEMA),
    cv.Optional(CONF_INSTRUMENTS): cv.ensure_list(INSTRUMENT_SCHEMA),
    cv.Optional(CONF_TUNES): cv.ensure_list(TUNE_SCHEMA),
})

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(TxUltimateTouch),

    cv.Required(CONF_UART): cv.use_id(uart),

    cv.Optional(CONF_DEVICE_FORMAT): validate_device_format,
    cv.Optional(CONF_GANG_COUNT): validate_gang_count,

    cv.Optional(CONF_ON_TOUCH_EVENT): automation.validate_automation(single=True),
    cv.Optional(CONF_ON_PRESS): automation.validate_automation(single=True),
    cv.Optional(CONF_ON_RELEASE): automation.validate_automation(single=True),
    cv.Optional(CONF_ON_SWIPE_LEFT): automation.validate_automation(single=True),
    cv.Optional(CONF_ON_SWIPE_RIGHT): automation.validate_automation(single=True),
    cv.Optional(CONF_ON_MULTI_TOUCH_RELEASE): automation.validate_automation(single=True),
    cv.Optional(CONF_ON_LONG_TOUCH_RELEASE): automation.validate_automation(single=True),

    cv.Optional(CONF_RTTTL_SYNTH): RTTTL_SYNTH_SCHEMA,

}).extend(cv.COMPONENT_SCHEMA).extend(uart.UART_DEVICE_SCHEMA)


async def register_tx_ultimate_easy(var, config):
    """
    Register the TxUltimateEasy component with its UART device and wire configured automations.
    
    For the given component instance, attach the configured UART component and build any automations present in the config for touch events, presses, releases, swipes, multi-touch releases, and long-touch releases. Each automation receives a payload field named "touch" of type `TouchPoint`.
    
    Parameters:
        var: The TxUltimateTouch component instance to configure.
        config (dict): Parsed configuration mapping containing `CONF_UART` and optional automation keys.
    """
    uart_component = await cg.get_variable(config[CONF_UART])
    cg.add(var.set_uart_component(uart_component))

    if CONF_ON_TOUCH_EVENT in config:
        await automation.build_automation(
            var.get_trigger_touch_event(),
            [(TouchPoint, "touch")],
            config[CONF_ON_TOUCH_EVENT],
        )

    if CONF_ON_PRESS in config:
        await automation.build_automation(
            var.get_trigger_touch(),
            [(TouchPoint, "touch")],
            config[CONF_ON_PRESS],
        )

    if CONF_ON_RELEASE in config:
        await automation.build_automation(
            var.get_trigger_release(),
            [(TouchPoint, "touch")],
            config[CONF_ON_RELEASE],
        )

    if CONF_ON_SWIPE_LEFT in config:
        await automation.build_automation(
            var.get_trigger_swipe_left(),
            [(TouchPoint, "touch")],
            config[CONF_ON_SWIPE_LEFT],
        )

    if CONF_ON_SWIPE_RIGHT in config:
        await automation.build_automation(
            var.get_trigger_swipe_right(),
            [(TouchPoint, "touch")],
            config[CONF_ON_SWIPE_RIGHT],
        )

    if CONF_ON_MULTI_TOUCH_RELEASE in config:
        await automation.build_automation(
            var.get_trigger_multi_touch_release(),
            [(TouchPoint, "touch")],
            config[CONF_ON_MULTI_TOUCH_RELEASE],
        )

    if CONF_ON_LONG_TOUCH_RELEASE in config:
        await automation.build_automation(
            var.get_trigger_long_touch_release(),
            [(TouchPoint, "touch")],
            config[CONF_ON_LONG_TOUCH_RELEASE],
        )

    if CONF_DEVICE_FORMAT in config:
        _LOGGER.info(
            "TX Ultimate Easy - Device format: %s",
            config[CONF_DEVICE_FORMAT],
        )

    if CONF_GANG_COUNT in config:
        _LOGGER.info(
            "TX Ultimate Easy - Gang number: %s",
            config[CONF_GANG_COUNT],
        )

def generate_rtttl_synth_code(config):
    """Generate C++ header file for RTTTL synth instruments and tunes."""
    rtttl_synth = config.get(CONF_RTTTL_SYNTH, {})
    comp_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(comp_dir, "rtttl_synth_data.h")

    if not rtttl_synth:
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

    envelopes = rtttl_synth.get(CONF_ENVELOPES, [])
    instruments = rtttl_synth.get(CONF_INSTRUMENTS, [])
    tunes = rtttl_synth.get(CONF_TUNES, [])
    sample_rate = rtttl_synth.get(CONF_SAMPLE_RATE, 16000)

    if not instruments:
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

    env_map = {e["id"]: e for e in envelopes}

    lines = []
    lines.append("#pragma once")
    lines.append('#include "tx_ultimate_easy_rtttl_synth.h"')
    lines.append("")
    lines.append("namespace esphome {")
    lines.append("namespace tx_ultimate_easy {")
    lines.append("")
    lines.append("// -- RTTTL synth instrument definitions (auto-generated) --")

    # Generate voice arrays
    voice_arrays = []
    for idx, instr in enumerate(instruments):
        voices = instr[CONF_VOICES]
        arr_name = f"v{idx}"
        cents_str = ", ".join(f"{float(v)}f" for v in voices)
        lines.append(f"static const float {arr_name}[] = {{ {cents_str} }};")
        voice_arrays.append((arr_name, len(voices)))

    lines.append("")

    # Generate instrument array
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
            _LOGGER.warning("Envelope '%s' not found for instrument '%s', using defaults", env_id, instr["id"])
            a, d, s, r = 5.0, 0.0, 0.6, 30.0

        dur = float(instr[CONF_NOTE_DURATION].milliseconds)
        freq = float(instr[CONF_BASE_FREQ])
        varr, vcnt = voice_arrays[idx]
        vib = "true" if instr[CONF_VIBRATO_ENABLED] else "false"
        vdepth = float(instr[CONF_VIBRATO_DEPTH])
        vrate = float(instr[CONF_VIBRATO_RATE])
        gain = float(instr[CONF_GAIN])

        lines.append(f'  {{')
        lines.append(f'    "{instr["id"]}",')
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

    # Generate lookup helper
    lines.append("static const RtttlSynthInstrument *find_instrument(const char *name) {")
    lines.append("  for (auto &inst : rtttl_synth_instruments) {")
    lines.append("    if (strcmp(inst.name, name) == 0) return &inst;")
    lines.append("  }")
    lines.append("  return nullptr;")
    lines.append("}")
    lines.append("")
    lines.append(f"static const size_t rtttl_synth_instrument_count = {len(instruments)};")
    lines.append(f"static const int rtttl_synth_sample_rate = {sample_rate};")

    # Generate tunes
    if tunes:
        lines.append("")
        lines.append("static const RtttlSynthTune rtttl_synth_tunes[] = {")
        for tune in tunes:
            rtttl_escaped = tune["rtttl"].replace('"', '\\"')
            name = tune.get("name") or tune["id"].replace("_", " ").title()
            lines.append(f'  {{"{name}", "{rtttl_escaped}"}},')
        lines.append("};")
        lines.append(f"static const size_t rtttl_synth_tune_count = {len(tunes)};")
        lines.append("")
        lines.append("static const RtttlSynthTune *find_tune(const char *name) {")
        lines.append("  for (auto &t : rtttl_synth_tunes) {")
        lines.append("    if (strcmp(t.name, name) == 0) return &t;")
        lines.append("  }")
        lines.append("  return nullptr;")
        lines.append("}")

    lines.append("")
    lines.append("}  // namespace tx_ultimate_easy")
    lines.append("}  // namespace esphome")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    return True


async def to_code(config):
    """
    Create and register a TxUltimateTouch component and its UART device from the provided configuration.
    
    This registers the component with ESPHome, registers it as a UART device, applies additional TxUltimateEasy setup, and defines the USE_TX_ULTIMATE_EASY build macro.
    
    Parameters:
        config (dict): Parsed component configuration from YAML used to create and wire the component.
    """
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
    await register_tx_ultimate_easy(var, config)

    cg.add_define("USE_TX_ULTIMATE_EASY")

    # Generate RTTTL synth data header file
    if generate_rtttl_synth_code(config):
        cg.add_define("USE_RTTTL_SYNTH")
