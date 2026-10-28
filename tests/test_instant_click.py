"""Test Cases: Instant Click Mode verification under QEMU emulation."""
import time
import pytest


def test_tc_ic01_click_fires_immediately_on_press_before_release(instant_switch):
    """TC-IC01: In Instant Click Mode, 'click' action fires immediately on PRESS before finger release."""
    instant_switch.set_gang_mode(1, "Relay")
    instant_switch.drain_logs()

    # Send ONLY the PRESS frame (do not release)
    instant_switch.send_touch_frame(0x02, 0x00, 0x01, 0x00)

    # Click action and relay toggle must fire IMMEDIATELY on touch-down
    instant_switch.assert_log("Button 1 action: 'click'")
    instant_switch.assert_log("Toggle relay 1")
    instant_switch.assert_log("'Relay 1' >> ON")

    # Now release
    instant_switch.drain_logs()
    instant_switch.send_touch_frame(0x01, 0x01, 0x01, 0x00)
    # Releasing must NOT trigger any new action or click
    instant_switch.assert_no_log("Button 1 action:", duration=0.3)


def test_tc_ic02_long_press_does_not_fire_long_press_event(instant_switch):
    """TC-IC02: Holding press for >500ms does NOT trigger long_press in Instant Click Mode."""
    instant_switch.set_gang_mode(1, "Relay")
    instant_switch.drain_logs()

    # Long press for 700ms
    instant_switch.long_press(gang=1, duration_ms=700.0)

    # Initial click fired on press
    instant_switch.assert_log("Button 1 action: 'click'")
    # Long press must NEVER fire
    instant_switch.assert_no_log("Button 1 action: 'long_press'", duration=0.2)


def test_tc_ic03_double_click_does_not_fire_double_click_event(instant_switch):
    """TC-IC03: Rapid consecutive taps do not trigger double_click in Instant Click Mode."""
    instant_switch.set_gang_mode(1, "Relay")
    instant_switch.drain_logs()

    # Double click
    instant_switch.double_click(gang=1, interval_ms=80.0)

    # Double click event is compiled out
    instant_switch.assert_no_log("Button 1 action: 'double_click'", duration=0.3)


def test_tc_ic04_rapid_fire_dead_zone_per_gang(instant_switch):
    """TC-IC04: Rapid fire taps on the same gang within 500ms are debounced (dead zone); fires again after 500ms."""
    instant_switch.set_gang_mode(1, "Relay")
    instant_switch.drain_logs()

    # Tap 1 on Gang 1
    instant_switch.tap(gang=1)
    instant_switch.assert_log("Button 1 action: 'click'")

    # Immediate second tap on Gang 1 within dead zone (100ms < 500ms debounce)
    instant_switch.drain_logs()
    time.sleep(0.10)
    instant_switch.tap(gang=1)
    instant_switch.assert_no_log("Button 1 action: 'click'", duration=0.3)

    # Wait for debounce window to expire (>500ms from first tap)
    time.sleep(0.55)
    instant_switch.drain_logs()

    # Tap 3 on Gang 1 after dead zone has expired
    instant_switch.tap(gang=1)
    instant_switch.assert_log("Button 1 action: 'click'")


def test_tc_ic05_multi_gang_simultaneous_touch_independent_debounce(instant_switch):
    """TC-IC05: Multiple gangs touched simultaneously/interleaved are independently debounced."""
    instant_switch.set_gang_mode(1, "Relay")
    instant_switch.set_gang_mode(2, "Relay")
    instant_switch.set_gang_mode(3, "Relay")
    instant_switch.drain_logs()

    # Tap Gang 1
    instant_switch.tap(gang=1)
    instant_switch.assert_log("Button 1 action: 'click'")

    # Immediately tap Gang 2 (50ms gap << 500ms dead zone) - Gang 2 must NOT be blocked
    instant_switch.drain_logs()
    time.sleep(0.05)
    instant_switch.tap(gang=2)
    instant_switch.assert_log("Button 2 action: 'click'")

    # Immediately tap Gang 3 (50ms gap << 500ms dead zone) - Gang 3 must NOT be blocked
    instant_switch.drain_logs()
    time.sleep(0.05)
    instant_switch.tap(gang=3)
    instant_switch.assert_log("Button 3 action: 'click'")


def test_tc_ic06_swipe_right_in_instant_click_mode(instant_switch):
    """TC-IC06: In Instant Click Mode, realistic swipe right registers an instant click on initial contact gang, then fires swipe."""
    # Settle debounce window
    time.sleep(0.6)
    instant_switch.drain_logs()
    instant_switch.swipe_right(start_gang=1, end_gang=3)
    # Contact on Gang 1 clicks immediately
    instant_switch.assert_log("Button 1 action: 'click'")
    # Swipe right packet is recognized
    instant_switch.assert_log("Swipe right")
    # Release must not cause a second click
    instant_switch.assert_no_log("action: 'double_click'", duration=0.2)


def test_tc_ic07_swipe_left_in_instant_click_mode(instant_switch):
    """TC-IC07: In Instant Click Mode, realistic swipe left registers an instant click on initial contact gang, then fires swipe."""
    # Settle debounce window
    time.sleep(0.6)
    instant_switch.drain_logs()
    instant_switch.swipe_left(start_gang=3, end_gang=1)
    # Contact on Gang 3 clicks immediately
    instant_switch.assert_log("Button 3 action: 'click'")
    # Swipe left packet is recognized
    instant_switch.assert_log("Swipe left")
    # Release must not cause a second click
    instant_switch.assert_no_log("action: 'double_click'", duration=0.2)


def test_tc_ic08_multi_touch_in_instant_click_mode(instant_switch):
    """TC-IC08: In Instant Click Mode, palm mash registers an instant click on the contact gang, then reports multi-touch."""
    # Settle debounce window
    time.sleep(0.6)
    instant_switch.drain_logs()
    instant_switch.palm_mash(contact_gang=2)
    # Initial slap contact on Gang 2 clicks immediately
    instant_switch.assert_log("Button 2 action: 'click'")
    # Multi-touch event is recognized
    instant_switch.assert_log("Multi-touch released")
    # Release must not cause a second click
    instant_switch.assert_no_log("action: 'double_click'", duration=0.2)


def test_tc_ic09_partial_swipe_in_instant_click_mode(instant_switch):
    """TC-IC09: Partial drag within a gang triggers instant click on touch-down and cleans up on release."""
    time.sleep(0.6)
    instant_switch.drain_logs()
    instant_switch.partial_swipe(start_pos=2, end_pos=3, duration_ms=60.0)
    instant_switch.assert_log("Button 1 action: 'click'")
    instant_switch.assert_no_log("action: 'double_click'", duration=0.2)


def test_tc_ic10_hardware_long_touch_in_instant_click_mode(instant_switch):
    """TC-IC10: Hardware long-touch triggers instant click on contact and logs long-touch release on lift."""
    time.sleep(0.6)
    instant_switch.drain_logs()
    instant_switch.hardware_long_touch(gang=1, hold_ms=150.0)
    instant_switch.assert_log("Button 1 action: 'click'")
    instant_switch.assert_log("Long-touch released at position 1")
