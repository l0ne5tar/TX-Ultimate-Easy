import time
import pytest

def test_tc_l01_led_mode_bottom(switch):
    """TC-L01: In Bottom light mode, toggling relay ON illuminates the Bottom light; OFF turns it off."""
    switch.set_gang_mode(1, "Relay")
    switch.set_gang_light_mode(1, "Bottom")
    switch.drain_logs()

    # Turn ON
    switch.tap(gang=1)
    switch.assert_log("Turn-on Bottom light for Relay 1")
    switch.assert_no_log("Turn-on Top light for Relay 1")

    switch.drain_logs()

    # Turn OFF
    time.sleep(0.6)
    switch.tap(gang=1)
    switch.assert_log("Turn-off Bottom light for Relay 1")


def test_tc_l02_led_mode_top(switch):
    """TC-L02: In Top light mode, toggling relay ON illuminates the Top light; Bottom light is not shown."""
    switch.set_gang_mode(1, "Relay")
    switch.set_gang_light_mode(1, "Top")
    switch.drain_logs()

    # Turn ON
    switch.tap(gang=1)
    switch.assert_log("Turn-on Top light for Relay 1")
    switch.assert_no_log("Turn-on Bottom light for Relay 1")

    switch.drain_logs()

    # Turn OFF
    time.sleep(0.6)
    switch.tap(gang=1)
    switch.assert_log("Turn-off Top light for Relay 1")


def test_tc_l03_led_mode_both(switch):
    """TC-L03: In Both light mode, toggling relay ON illuminates both Top and Bottom lights."""
    switch.set_gang_mode(1, "Relay")
    switch.set_gang_light_mode(1, "Both")
    switch.drain_logs()

    # Turn ON
    switch.tap(gang=1)
    switch.assert_log("Turn-on Bottom light for Relay 1")
    switch.assert_log("Turn-on Top light for Relay 1")

    switch.drain_logs()

    # Turn OFF
    time.sleep(0.6)
    switch.tap(gang=1)
    switch.assert_log("Turn-off Bottom light for Relay 1")
    switch.assert_log("Turn-off Top light for Relay 1")


def test_tc_l04_led_mode_off(switch):
    """TC-L04: In Off light mode, turning relay ON does NOT illuminate any relay status LEDs."""
    switch.set_gang_mode(1, "Relay")
    switch.set_gang_light_mode(1, "Off")
    switch.drain_logs()

    # Turn ON
    switch.tap(gang=1)
    switch.assert_log("Toggle relay 1")
    switch.assert_no_log("Turn-on Bottom light for Relay 1")
    switch.assert_no_log("Turn-on Top light for Relay 1")
