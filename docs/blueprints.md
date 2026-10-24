# Home Assistant Blueprints

This directory's blueprints live under `blueprints/automation/tx-ultimate-easy/`.

## Gang Link (`gang_link.yaml`)

Links **one** physical relay/light (the source of truth) to **any number** of
other switch/light entities — typically the `Virtual Relay N` entities exposed by
TX Ultimate Easy panels. Use it to build multi-way switches, panel remapping or
to keep spare gangs in sync with a real load.

### Installation

1. Copy `blueprints/automation/tx-ultimate-easy/gang_link.yaml` into your Home
   Assistant configuration under `blueprints/automation/tx-ultimate-easy/`.
2. Reload blueprints (or restart Home Assistant).
3. Create an automation from the blueprint for each group you want to link.

### Inputs

- **Physical relay (source of truth)** — exactly one switch or light entity that
  drives the real relay/load.
- **Linked panels (virtual relays)** — any number of switch/light entities to keep
  in sync. Usually the `Virtual Relay N` entities of one or more panels.

### Behaviour

- **Startup / reload** — the physical relay's state is pushed to every linked
  entity.
- **Reconnect** — when a linked (or the physical) entity comes back from
  `unavailable`/`unknown`, it is set to the physical relay's state.
- **Deliberate change** — when any linked entity (or the physical one) changes
  state, that new state is propagated to all the others. Only the panel that was
  actually touched needs to provide local feedback (sound/vibration); the
  Home Assistant propagation only updates state and LEDs.
- **Loop safety** — an entity is only written when its current state differs
  from the target state, so propagation terminates naturally.

### Notes

- All entities are written through `homeassistant.turn_on`/`turn_off`, which
  works across both `switch` and `light` domains (binary only — brightness and
  transitions are not handled).
- A panel that reconnects too quickly for Home Assistant to mark it
  `unavailable` may not trigger the reconnect sync. In that case use the
  automation's manual **Run** button (or reload the automation) to re-sync.
- Selecting a non-virtual physical relay as a linked entity is allowed, but it
  will be driven like any other member of the group.
- The automation runs in `queued` mode with a limit of 10 overlapping runs.
