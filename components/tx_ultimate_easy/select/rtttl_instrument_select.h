#pragma once

#include "esphome/components/select/select.h"
#include "esphome/core/component.h"
#include "esphome/core/preferences.h"

#include <memory>
#include <string>

#include "../rtttl_synth_data.h"

namespace esphome {
namespace tx_ultimate_easy {

class RtttlSelect : public select::Select, public Component {
 public:
  void set_type(const std::string &type) { type_ = type; }
  void set_initial_option(const std::string &name) { initial_option_ = name; }

  void setup() override {
    FixedVector<const char *> opts;
    opts.init(64);

    if (type_ == "instrument") {
      if constexpr (rtttl_synth_instrument_count > 0) {
        for (size_t i = 0; i < rtttl_synth_instrument_count; i++)
          opts.push_back(rtttl_synth_instruments[i].name);
      }
    } else if (type_ == "tune") {
      opts.push_back("Off");
      opts.push_back("Click (PCM)");
      if constexpr (rtttl_synth_tune_count > 0) {
        for (size_t i = 0; i < rtttl_synth_tune_count; i++)
          opts.push_back(rtttl_synth_tunes[i].name);
      }
      opts.push_back("User Defined 1");
      opts.push_back("User Defined 2");
    }

    this->traits.set_options(opts);

    this->pref_ = this->make_entity_preference<size_t>();

    // Defer publish_state to the first loop() so all components are
    // initialized before on_value automations (e.g. speaker_setup) fire.
    // The sound system (speaker, audio pipeline, scripts that call it)
    // is not fully initialised until after setup() completes, so any
    // publish_state() that triggers an on_value -> speaker action must
    // be delayed to avoid a boot crash.
    this->deferred_publish_.reset(new std::string(initial_option_));
    this->set_timeout(0, [this]() {
      const auto &saved = *this->deferred_publish_;
      size_t restored;
      size_t zero = 0;
      if (this->pref_.load(&restored) && restored < this->traits.get_options().size()) {
        this->publish_state(restored);
      } else if (!saved.empty()) {
        for (size_t i = 0; i < this->traits.get_options().size(); i++) {
          if (saved == this->traits.get_options()[i]) {
            this->publish_state(i);
            return;
          }
        }
        this->publish_state(zero);
      } else if (!this->traits.get_options().empty()) {
        this->publish_state(zero);
      }
      this->deferred_publish_.reset();
    });
  }

  void dump_config() override { ESP_LOGCONFIG("rtttl_select", "RtttlSelect type=%s", type_.c_str()); }

  float get_setup_priority() const override { return setup_priority::HARDWARE; }

 protected:
  void control(size_t index) override {
    this->publish_state(index);
    this->pref_.save(&index);
  }

  std::string type_;
  std::string initial_option_;
  ESPPreferenceObject pref_;
  std::unique_ptr<std::string> deferred_publish_;
};

}  // namespace tx_ultimate_easy
}  // namespace esphome
