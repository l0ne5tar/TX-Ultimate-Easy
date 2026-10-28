import time
import pytest

def test_tc_m01_relay_mode_toggle(switch):
    """TC-M01: Gang in Relay mode toggles the physical relay ON and OFF."""
    switch.set_gang_mode(1, "Relay")
    switch.drain_logs()

    # Tap 1: Turn ON
    switch.tap(gang=1)
    switch.assert_log("Toggle relay 1")
    switch.assert_log("'Relay 1' >> ON")

    switch.drain_logs()

    # Tap 2: Turn OFF
    time.sleep(0.6)
    switch.tap(gang=1)
    switch.assert_log("Toggle relay 1")
    switch.assert_log("'Relay 1' >> OFF")


def test_tc_m02_virtual_relay_mode(switch):
    """TC-M02: Gang in Virtual Relay mode toggles virtual relay without touching physical relay."""
    switch.set_gang_mode(1, "Virtual Relay")
    switch.drain_logs()

    # Tap 1: Turn ON virtual relay
    switch.tap(gang=1)
    switch.assert_log("Toggle virtual relay 1")
    switch.assert_log("'Virtual Relay 1' >> ON")
    switch.assert_no_log("Toggle relay 1")

    switch.drain_logs()

    # Tap 2: Turn OFF virtual relay
    time.sleep(0.6)
    switch.tap(gang=1)
    switch.assert_log("Toggle virtual relay 1")
    switch.assert_log("'Virtual Relay 1' >> OFF")
    switch.assert_no_log("Toggle relay 1")


def test_tc_m03_detached_relay_mode(switch):
    """TC-M03: Detached Relay fires HA event; physical and virtual relays remain untouched."""
    switch.set_gang_mode(1, "Detached Relay")
    switch.drain_logs()

    switch.tap(gang=1)
    switch.assert_log("Button 1 action: 'click'")
    switch.assert_log("HA event: touch/button")
    switch.assert_no_log("Toggle relay 1")
    switch.assert_no_log("Toggle virtual relay 1")


def test_tc_m04_detached_virtual_relay_mode(switch):
    """TC-M04: Detached Virtual Relay fires HA event; relays remain untouched."""
    switch.set_gang_mode(1, "Detached Virtual Relay")
    switch.drain_logs()

    switch.tap(gang=1)
    switch.assert_log("Button 1 action: 'click'")
    switch.assert_log("HA event: touch/button")
    switch.assert_no_log("Toggle relay 1")
    switch.assert_no_log("Toggle virtual relay 1")


def test_tc_m05_disabled_mode(switch):
    """TC-M05: Disabled gang ignores touch press entirely."""
    switch.set_gang_mode(1, "Disabled")
    switch.drain_logs()

    switch.tap(gang=1)
    switch.assert_log("Gang 1 is disabled; ignoring press")
    switch.assert_no_log("Toggle relay 1")
    switch.assert_no_log("Toggle virtual relay 1")
