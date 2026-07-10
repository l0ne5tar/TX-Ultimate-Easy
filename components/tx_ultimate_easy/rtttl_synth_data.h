#pragma once
#include "tx_ultimate_easy_rtttl_synth.h"

namespace esphome {
namespace tx_ultimate_easy {

// -- RTTTL synth instrument definitions (auto-generated) --
static const float v0[] = { 0.0f };
static const float v1[] = { 0.0f, 7.0f, -5.0f };
static const float v2[] = { 0.0f, 7.0f };
static const float v3[] = { 0.0f, 12.0f, -12.0f };
static const float v4[] = { 0.0f, -5.0f, 7.0f, 12.0f };
static const float v5[] = { 0.0f, -12.0f, 19.0f };
static const float v6[] = { 0.0f };

static const RtttlSynthInstrument rtttl_synth_instruments[] = {
  {
    "gameboy",
    SynthWaveform::PULSE,
    0.25f,
    {5.0f, 0.0f, 0.6f, 30.0f},
    60.0f,
    1200.0f,
    v0, 1,
    false, 0.0f, 5.0f, 0.5f
  },
  {
    "bell",
    SynthWaveform::SINE,
    0.5f,
    {2.0f, 0.0f, 0.2f, 150.0f},
    250.0f,
    1000.0f,
    v1, 3,
    false, 0.0f, 5.0f, 0.35f
  },
  {
    "organ",
    SynthWaveform::TRIANGLE,
    0.5f,
    {0.0f, 0.0f, 1.0f, 0.0f},
    80.0f,
    500.0f,
    v2, 2,
    true, 8.0f, 5.0f, 0.5f
  },
  {
    "piano",
    SynthWaveform::TRIANGLE,
    0.5f,
    {5.0f, 0.0f, 0.6f, 30.0f},
    80.0f,
    600.0f,
    v3, 3,
    false, 0.0f, 5.0f, 0.4f
  },
  {
    "chime",
    SynthWaveform::SINE,
    0.5f,
    {2.0f, 0.0f, 0.2f, 150.0f},
    300.0f,
    1200.0f,
    v4, 4,
    false, 0.0f, 5.0f, 0.3f
  },
  {
    "synth",
    SynthWaveform::PULSE,
    0.4f,
    {10.0f, 50.0f, 0.8f, 100.0f},
    100.0f,
    400.0f,
    v5, 3,
    false, 0.0f, 5.0f, 0.4f
  },
  {
    "alarm",
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

static const size_t rtttl_synth_instrument_count = 7;
static const int rtttl_synth_sample_rate = 16000;

}  // namespace tx_ultimate_easy
}  // namespace esphome