"""Test Cases: NVS Flash Persistence and Reboot State Recovery under QEMU emulation."""
import time
import pytest


def test_tc_p01_gang_mode_persists_across_reboot(switch):
    """TC-P01: Configured Gang Mode (Virtual Relay) survives hard device restart/reboot."""
    # Switch Gang 2 mode to Virtual Relay
    switch.set_gang_mode(2, "Virtual Relay")
    assert switch.get_entity_state("Gang 2 mode", timeout=5.0) == "Virtual Relay"

    # Allow ESPHome preferences component to flush dirty state to NVS
    time.sleep(2.0)

    # Perform reboot
    print("\n  [*] Rebooting QEMU emulator to test Gang Mode persistence...", flush=True)
    switch.restart()

    # Verify Gang 2 mode is still Virtual Relay
    assert switch.get_entity_state("Gang 2 mode", timeout=5.0) == "Virtual Relay", (
        "Gang 2 mode did not persist across reboot!"
    )

    # Clean up state back to Relay
    switch.set_gang_mode(2, "Relay")
    time.sleep(1.0)


def test_tc_p02_led_mode_persists_across_reboot(switch):
    """TC-P02: Configured Relay LED Mode survives hard device restart/reboot."""
    # Change Gang 1 LED mode to Top
    switch.set_gang_light_mode(1, "Top")
    assert switch.get_entity_state("Gang 1 light mode", timeout=5.0) == "Top"

    # Allow NVS flush
    time.sleep(2.0)

    # Perform reboot
    print("\n  [*] Rebooting QEMU emulator to test LED Mode persistence...", flush=True)
    switch.restart()

    # Verify LED mode is still Top
    assert switch.get_entity_state("Gang 1 light mode", timeout=5.0) == "Top", (
        "Gang 1 light mode did not persist across reboot!"
    )

    # Clean up state back to Bottom
    switch.set_gang_light_mode(1, "Bottom")
    time.sleep(1.0)


def test_tc_p03_relay_safe_restore_default_off(switch):
    """TC-P03: Relays enforce safe RESTORE_DEFAULT_OFF after device reboot/power restoration."""
    switch.drain_logs()

    # Reboot the device
    print("\n  [*] Rebooting QEMU emulator to test power-on relay safety...", flush=True)
    switch.restart()

    # Following boot, the config dump logs verify all relays default to safe OFF state
    switch.assert_log("Relays states:")
    switch.assert_log("Relay 1: OFF")
    switch.assert_log("Relay 2: OFF")
    switch.assert_log("Relay 3: OFF")
