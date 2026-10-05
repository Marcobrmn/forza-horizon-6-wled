# Forza Horizon 6 Data Out: future ideas

**Source:** [Official Forza Horizon 6 Data Out documentation](https://support.forza.net/hc/en-us/articles/51744149102611-Forza-Horizon-6-Data-Out-Documentation), updated May 15, 2026. This is research, **not** a list of implemented features. Validate real-game values before adding a feature.

FH6 sends a fixed **324-byte** UDP packet at the game's frame rate while actively driving; no packets are sent in menus, pauses, replays, rewinds or after a race. The game does not receive commands. The current app reads only race status, timestamp, maximum/idle/current engine RPM and sends WLED DDP at the configured LED frame rate.

Other fields in the official packet include:

- **Driving:** speed (m/s), gear, accelerator/brake/clutch/handbrake and steering inputs, power, torque and boost.
- **Grip and car:** per-wheel slip ratio/angle/combined slip, tire temperatures, wheel speeds and suspension travel; car ID/class, drivetrain and cylinder count.
- **Race and world:** position XYZ, distance, lap times/lap number, race position, fuel level and race time. FH6 also includes `CarGroup`, `SmashableVelDiff` and `SmashableMass`.

**Candidate order (not approved development):**

1. A configurable **shift cue** combining RPM and gear, if the bar needs more useful feedback. It must not promise an optimal shift point across cars.
2. Optional **brake/throttle mode**, preferably a separate LED segment or alternative mode so it does not obscure the RPM bar.
3. Only if actual users ask: low-frequency **speed/gear/race-status Home Assistant entities**. Avoid publishing every game frame to HA and its recorder.

Do not build a full telemetry suite, a map or automatic vehicle profiles without a use case. The FH6 packet **does not contain `TireWear` or `TrackOrdinal`** from Forza Motorsport's Dash format. Do not present those as available fields.
