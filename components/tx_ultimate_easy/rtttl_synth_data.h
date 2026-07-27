#pragma once
#include "tx_ultimate_easy_rtttl_synth.h"

namespace esphome {
namespace tx_ultimate_easy {

// -- RTTTL synth data (auto-generated) --

static const size_t rtttl_synth_instrument_count = 7;
static const size_t rtttl_synth_tune_count = 15;
static const int rtttl_synth_sample_rate = 16000;

static const float v0[] = { 0.0f };
static const float v1[] = { 0.0f, 7.0f, -5.0f };
static const float v2[] = { 0.0f, 7.0f };
static const float v3[] = { 0.0f, 12.0f, -12.0f };
static const float v4[] = { 0.0f, -5.0f, 7.0f, 12.0f };
static const float v5[] = { 0.0f, -12.0f, 19.0f };
static const float v6[] = { 0.0f };

static const RtttlSynthInstrument rtttl_synth_instruments[] = {
  {
    "Gameboy",
    SynthWaveform::PULSE,
    0.25f,
    {5.0f, 0.0f, 0.6f, 30.0f},
    60.0f,
    1200.0f,
    v0, 1,
    false, 0.0f, 5.0f, 0.5f
  },
  {
    "Bell",
    SynthWaveform::SINE,
    0.5f,
    {2.0f, 0.0f, 0.2f, 150.0f},
    250.0f,
    1000.0f,
    v1, 3,
    false, 0.0f, 5.0f, 0.35f
  },
  {
    "Organ",
    SynthWaveform::TRIANGLE,
    0.5f,
    {0.0f, 0.0f, 1.0f, 0.0f},
    80.0f,
    500.0f,
    v2, 2,
    true, 8.0f, 5.0f, 0.5f
  },
  {
    "Piano",
    SynthWaveform::TRIANGLE,
    0.5f,
    {5.0f, 0.0f, 0.6f, 30.0f},
    80.0f,
    600.0f,
    v3, 3,
    false, 0.0f, 5.0f, 0.4f
  },
  {
    "Chime",
    SynthWaveform::SINE,
    0.5f,
    {2.0f, 0.0f, 0.2f, 150.0f},
    300.0f,
    1200.0f,
    v4, 4,
    false, 0.0f, 5.0f, 0.3f
  },
  {
    "Synth",
    SynthWaveform::PULSE,
    0.4f,
    {10.0f, 50.0f, 0.8f, 100.0f},
    100.0f,
    400.0f,
    v5, 3,
    false, 0.0f, 5.0f, 0.4f
  },
  {
    "Alarm",
    SynthWaveform::SQUARE,
    0.5f,
    {0.0f, 0.0f, 0.5f, 50.0f},
    100.0f,
    800.0f,
    v6, 1,
    false, 0.0f, 5.0f, 0.6f
  },
};

static const RtttlSynthInstrument *find_instrument(const char *name) {
  for (auto &inst : rtttl_synth_instruments) {
    if (strcmp(inst.name, name) == 0) return &inst;
  }
  return nullptr;
}

static const RtttlSynthTune rtttl_synth_tunes[] = {
  {"Scale Up", "scale_up:d=32,o=5,b=100:c,c#,d#,e,f#,g#,a#,b"},
  {"Scale Down", "scale_down:d=32,o=5,b=100:b,a#,g#,f#,e,d#,c#,c"},
  {"Power Up", "power_up:d=8,o=5,b=120:g#,e,g#,e"},
  {"Power Down", "power_down:d=8,o=5,b=120:e,g#,e,g#"},
  {"Notification", "notification:d=16,o=5,b=200:g,c6,e6,c6,g"},
  {"Chirp", "chirp:d=32,o=6,b=240:g,e,g,e"},
  {"Beep", "beep:d=4,o=5,b=240:a5"},
  {"Ascending", "ascending:d=16,o=5,b=200:c,d,e,f,g,a,b,c6"},
  {"Descending", "descending:d=16,o=6,b=200:c6,b,a,g,f,e,d,c"},
  {"Triplet", "triplet:d=16,o=5,b=240:e,g,c6"},
  {"Triplet Down", "triplet_down:d=16,o=6,b=240:c6,g,e"},
  {"Fanfare", "fanfare:d=8,o=5,b=200:g,c6,e6,g6"},
  {"Twinkle", "twinkle:d=8,o=5,b=200:c,c,g,g,a,a,g"},
  {"Ding Dong", "ding_dong:d=4,o=5,b=200:e5,c5"},
  {"Buzzer", "buzzer:d=8,o=5,b=240:a5,a5,a5,a5,a5"},
};

static const RtttlSynthTune *find_tune(const char *name) {
  for (auto &t : rtttl_synth_tunes) {
    if (strcmp(t.name, name) == 0) return &t;
  }
  return nullptr;
}

inline int RtttlSynth::instrument_index(const std::string &name) {
  if constexpr (rtttl_synth_instrument_count > 0) {
    for (size_t i = 0; i < rtttl_synth_instrument_count; i++) {
      if (name == rtttl_synth_instruments[i].name) return static_cast<int>(i);
    }
  }
  return 0;
}

}  // namespace tx_ultimate_easy
}  // namespace esphome