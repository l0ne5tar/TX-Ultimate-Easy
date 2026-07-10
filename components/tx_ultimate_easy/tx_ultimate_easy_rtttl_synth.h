#pragma once

#include <vector>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <string>

// Forward declarations (provided by ESPHome headers in compilation context)
namespace esphome {
namespace speaker {
class Speaker;
}
}  // namespace esphome

namespace esphome {
namespace tx_ultimate_easy {

enum class SynthWaveform : uint8_t {
  SINE = 0,
  TRIANGLE,
  SQUARE,
  PULSE,
};

struct RtttlSynthEnvelope {
  float attack_ms;
  float decay_ms;
  float sustain;
  float release_ms;
};

struct RtttlSynthInstrument {
  const char *name;
  SynthWaveform waveform;
  float pulse_duty;
  RtttlSynthEnvelope envelope;
  float note_duration_ms;
  float base_freq;
  const float *voices;
  size_t voice_count;
  bool vibrato_enabled;
  float vibrato_depth_cents;
  float vibrato_rate_hz;
  float gain;
};

struct RtttlSynthTune {
  const char *name;
  const char *rtttl;
};

class RtttlSynth {
 public:
  static std::vector<uint8_t> generate(const RtttlSynthInstrument &inst, float sr = 16000.0f) {
    return generate_note(inst, inst.base_freq, inst.note_duration_ms, sr);
  }

  static std::vector<uint8_t> generate_note(const RtttlSynthInstrument &inst,
                                              float freq_hz, float dur_ms, float sr = 16000.0f);

  static std::vector<uint8_t> generate_rtttl(const RtttlSynthInstrument &inst,
                                              const std::string &rtttl, float sr = 16000.0f);

  /// Expand 8-bit unsigned PCM to 16-bit signed PCM and play in small chunks.
  /// Avoids allocating a full 2x output buffer.
  static void play_8bit(speaker::Speaker *spk, const std::vector<uint8_t> &data);

  /// Play an RTTTL string one note at a time (no large buffer).
  static void play_rtttl(speaker::Speaker *spk, const RtttlSynthInstrument &inst,
                          const std::string &rtttl, float sr = 16000.0f);

  /// Map instrument name to index in rtttl_synth_instruments[].
  /// Returns 0 (Gameboy) on unknown name.
  static int instrument_index(const std::string &name);
};

// -----------------------------------------------------------------------------
// Waveform generators — band-limited via additive synthesis
// -----------------------------------------------------------------------------
inline float waveform_sine(float phase) {
  return sinf(2.0f * M_PI * phase);
}

inline float bl_waveform(SynthWaveform type, float phase, float freq, float sr, float duty) {
  int max_h = static_cast<int>(sr / (2.0f * freq));
  if (max_h < 1) max_h = 1;
  if (max_h > 21) max_h = 21;  // Higher harmonics are ~inaudible

  switch (type) {
    case SynthWaveform::TRIANGLE: {
      float sum = 0.0f;
      int sign = 1;
      for (int k = 1; k <= max_h; k += 2) {
        sum += (float)sign * sinf(2.0f * M_PI * (float)k * phase) / (float)(k * k);
        sign = -sign;
      }
      return sum * 8.0f / (M_PI * M_PI);
    }
    case SynthWaveform::SQUARE: {
      float sum = 0.0f;
      for (int k = 1; k <= max_h; k += 2) {
        sum += sinf(2.0f * M_PI * (float)k * phase) / (float)k;
      }
      return sum * 4.0f / (float)M_PI;
    }
    case SynthWaveform::PULSE: {
      float sum = 0.0f;
      for (int k = 1; k <= max_h; k++) {
        float a = 2.0f * (float)M_PI * (float)k * duty;
        sum += (sinf(a) * cosf(2.0f * (float)M_PI * (float)k * phase)
              + (1.0f - cosf(a)) * sinf(2.0f * (float)M_PI * (float)k * phase)) / (float)k;
      }
      return 2.0f * duty - 1.0f + 2.0f * sum / (float)M_PI;
    }
    default:
      return 0.0f;
  }
}

// -----------------------------------------------------------------------------
// ADSR envelope
// -----------------------------------------------------------------------------
inline float adsr_envelope(float t_ms, const RtttlSynthEnvelope &env, float total_ms) {
  if (t_ms <= 0.0f) return 0.0f;
  if (t_ms >= total_ms) return 0.0f;

  float a_end = env.attack_ms;
  float d_end = a_end + env.decay_ms;
  float r_start = total_ms - env.release_ms;
  if (r_start < d_end) r_start = d_end;

  if (t_ms < a_end) return a_end > 0.0f ? t_ms / a_end : 1.0f;
  if (t_ms < d_end) {
    float dt = d_end - a_end;
    return dt > 0.0f ? 1.0f - (1.0f - env.sustain) * (t_ms - a_end) / dt : env.sustain;
  }
  if (t_ms < r_start) return env.sustain;
  float rt = total_ms - r_start;
  return rt > 0.0f ? env.sustain * (1.0f - (t_ms - r_start) / rt) : 0.0f;
}

// -----------------------------------------------------------------------------
// Synthesize one note into buffer
// -----------------------------------------------------------------------------
inline std::vector<uint8_t> RtttlSynth::generate_note(const RtttlSynthInstrument &inst,
                                                       float freq_hz, float dur_ms, float sr) {
  if (!isfinite(freq_hz) || freq_hz <= 0.0f) freq_hz = 440.0f;
  size_t n = static_cast<size_t>(sr * dur_ms / 1000.0f);
  if (n < 8) n = 8;
  std::vector<uint8_t> buf(n);

  for (size_t i = 0; i < n; i++) {
    float t_ms = dur_ms * i / n;
    float env = adsr_envelope(t_ms, inst.envelope, dur_ms);

    float vibrato = 0.0f;
    if (inst.vibrato_enabled && inst.vibrato_depth_cents > 0.0f) {
      vibrato = inst.vibrato_depth_cents * sinf(2.0f * M_PI * inst.vibrato_rate_hz * t_ms / 1000.0f);
    }

    float sample = 0.0f;
    for (size_t v = 0; v < inst.voice_count; v++) {
      float f = freq_hz * powf(2.0f, (inst.voices[v] + vibrato) / 1200.0f);
      float phase = fmodf(f * i / sr, 1.0f);

      float wf;
      if (inst.waveform == SynthWaveform::SINE) {
        wf = waveform_sine(phase);
      } else {
        wf = bl_waveform(inst.waveform, phase, f, sr, inst.pulse_duty);
      }
      sample += wf;
    }
    sample /= static_cast<float>(inst.voice_count);

    sample *= env * inst.gain * 0.7f;
    if (sample > 1.0f) sample = 1.0f;
    if (sample < -1.0f) sample = -1.0f;

    if (!isfinite(sample)) sample = 0.0f;
    buf[i] = static_cast<uint8_t>((sample + 1.0f) * 127.5f);
  }
  return buf;
}

// -----------------------------------------------------------------------------
// RTTTL parser + player
// -----------------------------------------------------------------------------
namespace rtttl_detail {

inline int semitone_index(char pitch, bool sharp) {
  switch (pitch) {
    case 'C': case 'c': return sharp ? 1 : 0;
    case 'D': case 'd': return sharp ? 3 : 2;
    case 'E': case 'e': return 4;
    case 'F': case 'f': return sharp ? 6 : 5;
    case 'G': case 'g': return sharp ? 8 : 7;
    case 'A': case 'a': return sharp ? 10 : 9;
    case 'B': case 'b': return 11;
    default: return -1;
  }
}

inline float note_freq(int semitone, int octave) {
  int midi = (octave + 1) * 12 + semitone;
  return 440.0f * powf(2.0f, (midi - 69) / 12.0f);
}

struct RtttlNote {
  float freq_hz;
  float dur_ms;
  bool rest;
};

inline bool parse_rtttl(const std::string &s, float &bpm, int &default_dur, int &default_octave,
                         std::vector<RtttlNote> &notes) {
  // Find first colon — skip name
  size_t c1 = s.find(':');
  if (c1 == std::string::npos) return false;
  size_t c2 = s.find(':', c1 + 1);
  if (c2 == std::string::npos) return false;

  std::string head = s.substr(c1 + 1, c2 - c1 - 1);
  std::string body = s.substr(c2 + 1);

  // Parse header
  default_dur = 4;
  default_octave = 5;
  bpm = 120.0f;

  size_t pos = 0;
  while (pos < head.length()) {
    while (pos < head.length() && head[pos] == ' ') pos++;
    if (pos >= head.length()) break;
    char key = head[pos];
    pos++;
    if (pos < head.length() && head[pos] == '=') pos++;
    while (pos < head.length() && head[pos] == ' ') pos++;

    size_t val_start = pos;
    while (pos < head.length() && head[pos] != ' ' && head[pos] != ',') pos++;

    std::string val = head.substr(val_start, pos - val_start);

    if (key == 'd' || key == 'o') {
      int v = 0;
      for (char c : val) { if (c >= '0' && c <= '9') v = v * 10 + (c - '0'); }
      if (key == 'd') default_dur = v; else default_octave = v;
    } else if (key == 'b') {
      float v = 0.0f; float div = 1.0f; bool frac = false;
      for (char c : val) {
        if (c == '.') { frac = true; continue; }
        if (c >= '0' && c <= '9') {
          if (frac) { div *= 10.0f; v += (c - '0') / div; }
          else v = v * 10.0f + (c - '0');
        }
      }
      bpm = v;
    }

    while (pos < head.length() && (head[pos] == ' ' || head[pos] == ',')) pos++;
  }

  // Parse notes
  float beat_sec = 60.0f / bpm;
  pos = 0;
  while (pos < body.length()) {
    while (pos < body.length() && (body[pos] == ' ' || body[pos] == ',')) pos++;
    if (pos >= body.length()) break;

    int dur = default_dur;
    int octave = default_octave;
    bool dotted = false;

    // Try to read duration number
    if (body[pos] >= '0' && body[pos] <= '9') {
      dur = 0;
      while (pos < body.length() && body[pos] >= '0' && body[pos] <= '9') {
        dur = dur * 10 + (body[pos] - '0');
        pos++;
      }
    }

    // Check for rest
    RtttlNote note;
    note.rest = false;

    if (pos < body.length() && (body[pos] == 'p' || body[pos] == 'P')) {
      note.rest = true;
      note.freq_hz = 0.0f;
      pos++;
    } else if (pos < body.length()) {
      char pitch = body[pos];
      pos++;
      bool sharp = (pos < body.length() && body[pos] == '#');
      if (sharp) pos++;

      int semitone = semitone_index(pitch, sharp);
      if (semitone < 0) return false;

      // Read octave if present
      if (pos < body.length() && body[pos] >= '0' && body[pos] <= '8') {
        octave = body[pos] - '0';
        pos++;
      }

      note.freq_hz = note_freq(semitone, octave);
      note.rest = false;
    } else {
      return false;
    }

    // Check for dotted
    if (pos < body.length() && body[pos] == '.') {
      dotted = true;
      pos++;
    }

    // Calculate duration
    note.dur_ms = beat_sec * (4000.0f / dur);
    if (dotted) note.dur_ms *= 1.5f;

    notes.push_back(note);
  }

  return !notes.empty();
}

}  // namespace rtttl_detail

inline std::vector<uint8_t> RtttlSynth::generate_rtttl(const RtttlSynthInstrument &inst,
                                                         const std::string &rtttl, float sr) {
  float bpm;
  int default_dur, default_octave;
  std::vector<rtttl_detail::RtttlNote> notes;

  if (!rtttl_detail::parse_rtttl(rtttl, bpm, default_dur, default_octave, notes)) {
    return {};
  }

  // Estimate total size
  size_t total_samples = 0;
  for (auto &n : notes) {
    total_samples += static_cast<size_t>(sr * n.dur_ms / 1000.0f);
  }
  if (total_samples > 65536) total_samples = 65536;

  std::vector<uint8_t> out;
  out.reserve(total_samples);

  uint8_t mid = 128;

  for (auto &n : notes) {
    if (n.rest) {
      size_t ns = static_cast<size_t>(sr * n.dur_ms / 1000.0f);
      if (ns + out.size() > total_samples) ns = total_samples - out.size();
      for (size_t i = 0; i < ns; i++) out.push_back(mid);
    } else {
      float gap_ms = (n.dur_ms > 50.0f) ? 2.0f : n.dur_ms * 0.02f;
      float play_ms = n.dur_ms - gap_ms;
      auto buf = generate_note(inst, n.freq_hz, play_ms, sr);
      size_t avail = total_samples - out.size();
      if (buf.size() > avail) buf.resize(avail);
      out.insert(out.end(), buf.begin(), buf.end());
      size_t gs = static_cast<size_t>(sr * gap_ms / 1000.0f);
      if (gs + out.size() > total_samples) gs = total_samples - out.size();
      for (size_t i = 0; i < gs; i++) out.push_back(mid);
    }
  }

  return out;
}

// -----------------------------------------------------------------------------
// Streaming RTTTL player — must STREAM, NOT buffer the entire waveform.
// DO NOT replace this with generate_rtttl + play_8bit — the project does not
// have enough free heap for a full RTTTL buffer.  This function generates and
// plays one note at a time to keep peak heap usage low.
// -----------------------------------------------------------------------------
inline void RtttlSynth::play_rtttl(speaker::Speaker *spk, const RtttlSynthInstrument &inst,
                                    const std::string &rtttl, float sr) {
  float bpm;
  int default_dur, default_octave;
  std::vector<rtttl_detail::RtttlNote> notes;

  if (!rtttl_detail::parse_rtttl(rtttl, bpm, default_dur, default_octave, notes)) {
    return;
  }

  // Fill silence to keep the DMA pipeline running during rests and gaps
  auto make_silence = [&](float dur_ms) {
    if (dur_ms <= 0.0f) return;
    size_t ns = static_cast<size_t>(sr * dur_ms / 1000.0f);
    if (ns == 0) return;
    static int silence_call = 0;
    silence_call++;
    ESP_LOGD("rtttl_synth", "    make_silence[%d]: dur=%.1f ns=%u", silence_call, dur_ms, (unsigned)ns);
    static constexpr size_t SILENT_CHUNK = 1024;
    static int16_t silent[SILENT_CHUNK];
    memset(silent, 0, sizeof(silent));
    constexpr int MAX_RETRIES = 200;
    while (ns > 0) {
      size_t cnt = ns > SILENT_CHUNK ? SILENT_CHUNK : ns;
      size_t to_write = cnt * sizeof(int16_t);
      size_t written = 0;
      int retries = 0;
      while (written < to_write) {
        size_t n = spk->play(reinterpret_cast<const uint8_t *>(silent) + written, to_write - written, pdMS_TO_TICKS(50));
        if (n > 0) { written += n; retries = 0; }
        else { retries++; if (retries > MAX_RETRIES) break; vTaskDelay(pdMS_TO_TICKS(5)); }
      }
      ns -= cnt;
    }
  };

  ESP_LOGD("rtttl_synth", "play_rtttl: %u notes, bpm=%.0f", (unsigned)notes.size(), bpm);
  int note_idx = 0;
  for (auto &n : notes) {
    if (n.rest) {
      ESP_LOGD("rtttl_synth", "  note[%d]: REST dur=%.1f", note_idx, n.dur_ms);
      make_silence(n.dur_ms);
    } else {
      float gap_ms = (n.dur_ms > 50.0f) ? 2.0f : n.dur_ms * 0.02f;
      float play_ms = n.dur_ms - gap_ms;
      ESP_LOGD("rtttl_synth", "  note[%d]: freq=%.0f play=%.1f gap=%.1f", note_idx, n.freq_hz, play_ms, gap_ms);
      auto buf = generate_note(inst, n.freq_hz, play_ms, sr);
      ESP_LOGD("rtttl_synth", "    generate_note -> %u samples", (unsigned)buf.size());
      play_8bit(spk, buf);
      ESP_LOGD("rtttl_synth", "    make_silence(%.1f)", gap_ms);
      make_silence(gap_ms);
    }
    note_idx++;
  }
  ESP_LOGD("rtttl_synth", "play_rtttl done");
}

// -----------------------------------------------------------------------------
// Streaming 8-bit → 16-bit converter + player
// -----------------------------------------------------------------------------
inline void RtttlSynth::play_8bit(speaker::Speaker *spk, const std::vector<uint8_t> &data) {
  if (data.empty()) return;
  static int call_count = 0;
  call_count++;
  ESP_LOGD("rtttl_synth", "  play_8bit[%d]: %u bytes (%u chunks)",
           call_count, (unsigned)data.size(), (unsigned)((data.size() + 255) / 256));
  constexpr size_t CHUNK_SAMPLES = 256;  // 512 bytes per chunk
  static int16_t chunk[CHUNK_SAMPLES];
  constexpr int MAX_RETRIES = 200;
  size_t pos = 0;
  while (pos < data.size()) {
    size_t end = pos + CHUNK_SAMPLES;
    if (end > data.size()) end = data.size();
    size_t cnt = end - pos;
    for (size_t i = 0; i < cnt; i++) {
      chunk[i] = (static_cast<int16_t>(data[pos + i]) - 128) << 8;
    }
    size_t bytes = cnt * sizeof(int16_t);
    size_t written = 0;
    int retries = 0;
    while (written < bytes && retries <= MAX_RETRIES) {
      size_t n = spk->play(reinterpret_cast<const uint8_t *>(chunk) + written, bytes - written, pdMS_TO_TICKS(50));
      if (n > 0) { written += n; retries = 0; }
      else { retries++; vTaskDelay(pdMS_TO_TICKS(5)); }
    }
    pos = end;
  }
}

inline int RtttlSynth::instrument_index(const std::string &name) {
  if (name == "Bell") return 1;
  if (name == "Organ") return 2;
  if (name == "Piano") return 3;
  if (name == "Chime") return 4;
  if (name == "Synth") return 5;
  if (name == "Alarm") return 6;
  return 0;  // Gameboy
}

}  // namespace tx_ultimate_easy
}  // namespace esphome
