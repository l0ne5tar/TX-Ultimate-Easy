"""Test Cases: Night Mode verification under QEMU emulation."""
import time
import pytest


def test_tc_nm01_enable_night_mode(switch):
    """TC-NM01: Turning on Night Mode activates the night mode override on the LED strip."""
    switch.drain_logs()
    switch.set_night_mode(True)
    switch.assert_log("'Night Mode' >> ON")
    time.sleep(1.0)


def test_tc_nm02_night_mode_suppresses_relay_led_updates(switch):
    """TC-NM02: While Night Mode is ON, toggling relay alters physical relay state but suppresses relay status LED updates."""
    switch.set_gang_mode(1, "Relay")
    switch.set_night_mode(True)
    time.sleep(1.0)
    switch.drain_logs()

    # Tap Gang 1 while Night Mode is ON
    switch.tap(gang=1)
    # The physical relay must toggle
    switch.assert_log("Toggle relay 1")
    switch.assert_log("'Relay 1' >> ON")
    
    # But relay-specific LED indication must be suppressed by night mode
    switch.assert_no_log("Turn-on Bottom light for Relay 1", duration=0.2)
    switch.assert_no_log("Turn-on Top light for Relay 1", duration=0.2)


def test_tc_nm03_disable_night_mode_restores_relay_indicators(switch):
    """TC-NM03: Turning OFF Night Mode evaluates and restores relay status LED indicators."""
    switch.set_gang_mode(1, "Relay")
    switch.set_night_mode(True)
    time.sleep(1.0)
    
    # Turn relay 1 ON while in night mode
    switch.set_relay(1, True)
    time.sleep(0.5)
    switch.drain_logs()

    # Turn Night Mode OFF
    switch.set_night_mode(False)
    switch.assert_log("'Night Mode' >> OFF")
    # Relay status must be re-evaluated
    switch.assert_log("Turn-on Bottom light for Relay 1")


def test_tc_nm04_night_mode_suppress_vibration_toggle(switch):
    """TC-NM04: Night Mode vibration suppression toggle operates correctly."""
    switch.set_switch("Night Mode - Suppress Vibration", False)
    switch.assert_log("'Night Mode - Suppress Vibration' >> OFF")

    switch.drain_logs()
    switch.set_switch("Night Mode - Suppress Vibration", True)
    switch.assert_log("'Night Mode - Suppress Vibration' >> ON")


def test_tc_nm05_night_mode_suppress_sound_toggle(switch):
    """TC-NM05: Night Mode sound suppression toggle operates correctly."""
    switch.set_switch("Night Mode - Suppress Sound", False)
    switch.assert_log("'Night Mode - Suppress Sound' >> OFF")

    switch.drain_logs()
    switch.set_switch("Night Mode - Suppress Sound", True)
    switch.assert_log("'Night Mode - Suppress Sound' >> ON")
