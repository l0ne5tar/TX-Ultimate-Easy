# TX Ultimate Easy - Standalone QEMU Integration Test Suite

This automated test suite runs completely standalone without any agent driving it. It verifies the firmware using standard `pytest` directly against **Espressif QEMU ESP32** hardware emulation before flashing physical devices.

---

## Standalone Design & Toolchain Discovery

The test suite is fully self-contained within the repository and automatically manages:

1. **Toolchain Auto-Discovery**:
   - **QEMU (`qemu-system-xtensa`)**: Searches `QEMU_BIN` / `QEMU_SYSTEM_XTENSA` environment variables, system `PATH`, and standard Espressif tool directories (`~/.espressif/tools/qemu-xtensa/`).
   - **ESPHome CLI**: Searches `ESPHOME_BIN` environment variable, active Python virtualenv, and system `PATH`.
   - **Dummy EFUSE**: Automatically checked and created in `tests/configs/qemu_efuse.bin` if missing on a clean clone.

2. **Automated Multi-Target Builds & Flash Caching**:
   - Compiles two isolated firmware targets to local temporary storage (preventing SMB/network file locks):
     - `test_standard.yaml`: Core + Relays + LEDs + Vibration + **Night Mode**.
     - `test_instant.yaml`: Core + Relays + **Instant Click Mode** (`instant_click_mode: true`).
   - Pads the factory binaries into 8MB raw flash images (`qemu_flash_test.bin` and `qemu_flash_instant.bin`).
   - Recompiles only when source configuration files change, or when `--compile` is passed.

3. **Dual-QEMU Session Isolation**:
   - Standard firmware runs on ports `4444` (UART0 logs), `4445` (UART1 touch injection), and `6053` (ESPHome API).
   - Instant Click firmware runs on ports `4446` (UART0 logs), `4447` (UART1 touch injection), and `6054` (ESPHome API).

---

## Test Suites (44 Automated Tests)

- **`tests/test_gestures.py` (13 Tests)**:
  - Single clicks on Gangs 1, 2, 3.
  - Double-click detection with inter-tap gap verification.
  - Multi-click gap timeout (ensures clicks separated by >250ms register as separate single clicks).
  - Long press (>500ms) gesture detection.
  - **Realistic Swipe Right (`TC-G07`)**: Physical sequence (`PRESS` on Gang 1 -> transit delay -> `SWIPE_RIGHT` -> `RELEASE` on Gang 3). Verifies swipe suppresses the initial touch-down click on Gang 1.
  - **Realistic Swipe Left (`TC-G08`)**: Physical sequence (`PRESS` on Gang 3 -> transit delay -> `SWIPE_LEFT` -> `RELEASE` on Gang 1). Verifies swipe suppresses the initial touch-down click on Gang 3.
  - **Palm Mash / Multi-Touch (`TC-G09`)**: Palm slap contact on Gang 2 followed by multi-touch saturation frame (`0x01, 0x0B`). Verifies multi-touch suppresses the initial contact click on Gang 2.
  - **Stale press recovery (`TC-G10`)**: Dropped release frame glitch recovery starts a clean new sequence.
  - **Cross-gang disambiguation (`TC-G11`)**: Tapping Gang 1 then Gang 2 registers 2 independent single clicks without misclassifying as double clicks.
  - **Partial swipe / intra-gang drag (`TC-G12`)**: Dragging within the same gang boundary evaluates as a single click.
  - **Hardware long touch (`TC-G13`)**: Hardware touch controller reporting `x >= 17` on release triggers long touch release.

- **`tests/test_instant_click.py` (10 Tests)**:
  - Immediate relay switching on initial touch-down (`PRESS`) before release.
  - Long press suppression in Instant Click Mode.
  - Double-click suppression in Instant Click Mode.
  - **Rapid-fire dead zone per-gang debounce (`TC-IC04`)**: Rapid repeat touches on Gang 1 within 500ms are suppressed.
  - **Multi-gang concurrent independent debounce (`TC-IC05`)**: Touching Gang 1, Gang 2, and Gang 3 in rapid succession fires all three immediately without cross-blocking.
  - **Realistic Swipe Right (`TC-IC06`)**: Initial contact clicks Gang 1 instantly; swipe right frame fires swipe event; release does not double-fire.
  - **Realistic Swipe Left (`TC-IC07`)**: Initial contact clicks Gang 3 instantly; swipe left frame fires swipe event; release does not double-fire.
  - **Palm Mash (`TC-IC08`)**: Initial palm slap clicks contact gang instantly; multi-touch release fires event; release does not double-fire.
  - **Partial drag (`TC-IC09`)**: Contact triggers instant click; release cleans up without extra click.
  - **Hardware long touch (`TC-IC10`)**: Contact triggers instant click; hardware long-touch release logs event.

- **`tests/test_persistence.py` (3 Tests)**:
  - **Gang Mode persistence across reboot (`TC-P01`)**: Configured gang modes (`Virtual Relay`) survive hard device reboots.
  - **LED Mode persistence across reboot (`TC-P02`)**: Configured relay LED indicator modes (`Top`) survive hard device reboots.
  - **Relay power-on safety (`TC-P03`)**: Relays safely restore to default OFF after device power restoration (`RESTORE_DEFAULT_OFF`).

- **`tests/test_relay_modes.py` (5 Tests)**:
  - `Relay`: Physical relay toggle with LED state tracking.
  - `Virtual Relay`: State toggle without engaging physical relays.
  - `Detached Relay`: Fires Home Assistant event; relays remain untouched.
  - `Detached Virtual Relay`: Fires Home Assistant event; relays remain untouched.
  - `Disabled`: Ignores touch presses completely.

- **`tests/test_led_indication.py` (4 Tests)**:
  - `Bottom`: Bottom/left LED segment illuminated on relay ON.
  - `Top`: Top/right LED segment illuminated on relay ON.
  - `Both`: Both LED segments illuminated on relay ON.
  - `Disabled` (`Off`): Relay status LEDs remain unlit.

- **`tests/test_night_mode.py` (5 Tests)**:
  - Enabling Night Mode activates the night mode LED partition.
  - While Night Mode is ON, physical relay toggles but all relay-specific LED updates are suppressed.
  - Disabling Night Mode evaluates and restores relay status LED indicators (`show_relay_status`).
  - Night mode vibration suppression toggle (`sw_night_mode_suppress_vibration`).
  - Night mode sound suppression toggle (`sw_night_mode_suppress_sound`).

- **`tests/test_instant_click.py` (8 Tests)**:
  - Tests the dedicated `instant_click_mode: true` firmware build.
  - Click action and relay toggle fire immediately on **touch-down (PRESS)** before finger release.
  - Holding down press does not trigger `long_press`.
  - Rapid consecutive taps do not trigger `double_click`.
  - **Dead zone debounce per gang**: Rapid taps on the same gang within the 500ms debounce window are ignored; clicks fire again after 500ms.
  - **Multi-gang simultaneous/interleaved touch**: Touching multiple gangs in rapid succession (<50ms) fires each gang independently because debounce tracking is per-button.
  - Swipe right / down gesture decoding in instant click mode.
  - Swipe left / up gesture decoding in instant click mode.
  - Multi-touch gesture recognition in instant click mode.

- **`tests/test_fuzzing.py` (4 Tests)**:
  - Truncated and partial UART packets.
  - Corrupted header sync bytes (`0xDE, 0xAD`).
  - Out-of-bounds touch position bytes (`0xFF`, `0x80`).
  - Rapid burst flood (100 raw frames in 5ms) verifying FIFO resilience and watchdog stability.

---

## How to Run (No Agent Needed)

From the command line in the repository root:

### Windows Batch:
```cmd
run_tests.cmd
```

### Python (Cross-Platform):
```bash
# Run all tests (auto-compiles any missing firmware)
python run_tests.py

# Force re-compilation of all firmware targets
python run_tests.py --compile

# Run a specific test suite or test filter
python run_tests.py -k test_gestures
python run_tests.py -k test_night_mode
python run_tests.py -k test_instant_click
```

### Raw Pytest:
Even running raw pytest works standalone (assets are checked on session start):
```bash
pytest
```
