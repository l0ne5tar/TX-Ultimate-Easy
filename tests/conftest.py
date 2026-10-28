import pytest
from tests.builder import ensure_all_test_assets
from tests.qemu_harness import QemuHarness, FLASH_INSTANT_BIN_DEFAULT

def pytest_sessionstart(session):
    """Ensure all required firmware binaries and flash images are prepared before tests run."""
    ensure_all_test_assets()

@pytest.fixture(scope="session")
def qemu_switch():
    """Session-scoped QEMU harness instance running Standard firmware."""
    print("\n[*] Initializing QEMU switch harness (session scope)...")
    harness = QemuHarness()
    yield harness
    print("\n[*] Shutting down QEMU switch harness...")
    harness.close()

@pytest.fixture
def switch(qemu_switch):
    """Per-test fixture providing access to the live switch."""
    qemu_switch.reset_state()
    return qemu_switch

@pytest.fixture(scope="session")
def qemu_instant_switch():
    """Session-scoped QEMU harness instance running Instant Click Mode firmware."""
    print("\n[*] Initializing QEMU Instant-Click switch harness (session scope)...")
    harness = QemuHarness(
        log_port=4446,
        touch_port=4447,
        api_port=6054,
        flash_bin=FLASH_INSTANT_BIN_DEFAULT,
    )
    yield harness
    print("\n[*] Shutting down QEMU Instant-Click switch harness...")
    harness.close()

@pytest.fixture
def instant_switch(qemu_instant_switch):
    """Per-test fixture providing access to the live instant-click switch."""
    qemu_instant_switch.reset_state()
    return qemu_instant_switch
