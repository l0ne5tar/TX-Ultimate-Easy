# ESP-NOW

Switches can control relays on other TX Ultimate Easy devices directly (peer-to-peer) with ~4ms latency, completely independent of Home Assistant or Wi-Fi connectivity.

## Setup

1. Add the ESP-NOW package to your device YAML:

   ```yaml
   packages:
     remote_package:
       url: https://github.com/edwardtfn/TX-Ultimate-Easy
       ref: main
       refresh: 5min
       files:
         - ESPHome/TX-Ultimate-Easy-ESPHome_core.yaml
         - ESPHome/TX-Ultimate-Easy-ESPHome_standard.yaml
         - ESPHome/TX-Ultimate-Easy-ESPHome_espnow.yaml
   ```

2. Flash once. All ESP-NOW configuration is **runtime configurable per gang** directly from Home Assistant — no recompilation or reflashing needed when pairing or moving switches!

## Configuration

Each gang exposes three configuration entities to Home Assistant:

- **`Gang N ESP-NOW Target MAC`** (Text): The MAC address of the destination device (e.g. `AA:BB:CC:DD:EE:FF`). You can find any device's MAC from its **"ESP-NOW MAC Address"** sensor or Home Assistant device info.
- **`Gang N ESP-NOW Target Gang`** (Select): Which gang on the destination device to toggle (`Gang 1` .. `Gang 4`).
- **`Gang N ESP-NOW Mode`** (Select):
  - **`Off`**: Disabled (default).
  - **`Always`**: Sends an ESP-NOW toggle packet on every touch for ultra-fast 4ms hardware control.
  - **`API failsafe only`**: Sends via ESP-NOW only when disconnected from Home Assistant or Wi-Fi, providing seamless offline failsafe operation.

On the destination device with physical loads, turn on **`ESP-NOW Receive Enabled`**.

### Optional YAML Seeding

If you prefer to pre-seed default targets in your YAML at compile time, you can still provide substitutions:

```yaml
substitutions:
  espnow_target_mac_button_1: "AA:BB:CC:DD:EE:FF"
  espnow_target_relay_button_1: 1
```

These values serve as the initial restore seed; changing them in Home Assistant at runtime takes precedence.

## Automatic "Fire-and-Forget" Binding via Home Assistant Blueprint

When using the **TX Ultimate Easy - Gang Link** blueprint (`gang_link.yaml`):

1. Set `physical_entity` to the main relay driving the load.
2. Select your linked remote panels in `virtual_entities`.
3. Enable **`Automatic ESP-NOW Peer-to-Peer Binding`**.

Home Assistant will automatically resolve the destination MAC address, target gang, and program all runtime entities and receiver states across all panels. Once saved, peer-to-peer control is active and continues working even if Home Assistant is stopped or the router is unplugged.

## 2-Way State Synchronization

When an ESP-NOW toggle is received, the target device toggles its gang according to its own configured gang mode (`Relay`, `Virtual Relay`, etc.) and immediately sends back a hardware-acknowledged state broadcast (`0x02`). The sender panel updates its virtual relay state and LED ring indicators within 4ms.
