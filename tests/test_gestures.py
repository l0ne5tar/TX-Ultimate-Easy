import time
import pytest

def test_tc_g01_single_click_gang1(switch):
    """TC-G01: Single tap on Gang 1 registers click action."""
    switch.tap(gang=1)
    switch.assert_log("Button 1 action: 'click'")
    switch.assert_log("Toggle relay 1")

def test_tc_g02_single_click_gang2(switch):
    """TC-G02: Single tap on Gang 2 registers click action."""
    switch.tap(gang=2)
    switch.assert_log("Button 2 action: 'click'")
    switch.assert_log("Toggle relay 2")

def test_tc_g03_single_click_gang3(switch):
    """TC-G03: Single tap on Gang 3 registers click action."""
    switch.tap(gang=3)
    switch.assert_log("Button 3 action: 'click'")
    switch.assert_log("Toggle relay 3")

def test_tc_g04_double_click(switch):
    """TC-G04: Double-click with 80ms interval registers double_click."""
    switch.double_click(gang=1, interval_ms=80)
    switch.assert_log("Button 1 action: 'double_click'")

def test_tc_g05_multi_click_timeout_registers_two_clicks(switch):
    """TC-G05: Two clicks with gap > multi_click_delay (350ms > 250ms) must register as 2 single clicks."""
    switch.tap(gang=1)
    switch.assert_log("Button 1 action: 'click'")
    
    # Wait past multi_click window
    time.sleep(0.35)
    switch.drain_logs()

    switch.tap(gang=1)
    switch.assert_log("Button 1 action: 'click'")

def test_tc_g06_long_press(switch):
    """TC-G06: Long press (>500ms) registers long press action."""
    switch.long_press(gang=1, duration_ms=600)
    assert switch.read_logs_until("Long touch - Released") or switch.read_logs_until("long_click")

def test_tc_g07_swipe_right(switch):
    """TC-G07: Swipe right gesture cleanly suppresses the initial touch-down click in Normal Mode."""
    switch.drain_logs()
    switch.swipe_right(start_gang=1, end_gang=3)
    switch.assert_log("Swipe right")
    # Verify the initial touch-down on Gang 1 was aborted by buttons_reset_state
    switch.assert_no_log("Button 1 action: 'click'", duration=0.3)

def test_tc_g08_swipe_left(switch):
    """TC-G08: Swipe left gesture cleanly suppresses the initial touch-down click in Normal Mode."""
    switch.drain_logs()
    switch.swipe_left(start_gang=3, end_gang=1)
    switch.assert_log("Swipe left")
    # Verify the initial touch-down on Gang 3 was aborted by buttons_reset_state
    switch.assert_no_log("Button 3 action: 'click'", duration=0.3)

def test_tc_g09_multi_touch(switch):
    """TC-G09: Multi-touch / palm mash gesture cleanly suppresses the initial slap click in Normal Mode."""
    switch.drain_logs()
    switch.palm_mash(contact_gang=2)
    switch.assert_log("Multi-touch released")
    # Verify the initial palm contact on Gang 2 was aborted by buttons_reset_state
    switch.assert_no_log("Button 2 action: 'click'", duration=0.3)


def test_tc_g10_stale_press_recovery(switch):
    """TC-G10: A missing release frame (glitch) is detected as a stale press and recovered gracefully."""
    switch.drain_logs()

    # Send PRESS on Gang 1 without release
    switch.send_touch_frame(0x02, 0x00, 0x02, 0x00)

    # Wait 300ms, then send another PRESS on Gang 1
    time.sleep(0.30)
    switch.send_touch_frame(0x02, 0x00, 0x02, 0x00)

    # Firmware must detect stale press and restart sequence
    switch.assert_log("Stale press detected (no release received), starting new sequence")

    # Complete the second press with a release
    switch.send_touch_frame(0x01, 0x01, 0x02, 0x00)
    switch.assert_log("Button 1 action: 'click'")


def test_tc_g11_cross_gang_rapid_tap_disambiguation(switch):
    """TC-G11: Tapping Gang 1 then Gang 2 produces 2 independent single clicks, not a double click."""
    switch.drain_logs()

    # Tap Gang 1
    switch.tap(gang=1)
    switch.assert_log("Button 1 action: 'click'")

    # Allow QEMU LED RMT flush to settle before next gesture
    time.sleep(0.6)

    # Now tap Gang 2
    switch.drain_logs()
    switch.tap(gang=2)
    switch.assert_log("Button 2 action: 'click'")

    # Double-click must NEVER be triggered
    switch.assert_no_log("action: 'double_click'", duration=0.2)


def test_tc_g12_partial_swipe_same_gang(switch):
    """TC-G12: A partial swipe / drag within the same gang boundary evaluates as a single click."""
    switch.drain_logs()
    # Contact pos 2 (Gang 1), drag to pos 3 (still Gang 1), release
    switch.partial_swipe(start_pos=2, end_pos=3, duration_ms=60.0)
    switch.assert_log("Button 1 action: 'click'")


def test_tc_g13_hardware_long_touch(switch):
    """TC-G13: Hardware-level long touch (x >= 17 on release) fires long-touch release trigger."""
    switch.drain_logs()
    switch.hardware_long_touch(gang=1, hold_ms=150.0)
    switch.assert_log("Long-touch released at position 1")
