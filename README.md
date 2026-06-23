# RogosMobile

Unreal Engine **5.8** project for **RogoBot** — the *AX-9 "Wanderer"* quadruped scout: a spherical
body on four splayed crab legs that walks, climbs ramps, adapts to terrain, and topples into a
ragdoll when it tips over. Targets mobile / Steam Deck.

## How the bot works

The locomotion is **leg-driven** and computed on the pawn, not in the animation graph (a Control Rig
hosted in an AnimBP can't hold per-tick state). The pieces:

- **`URogoGaitComponent`** (`Source/RogosMobile`, attached to `BP_RogoBot`) — the brain of the gait.
  Ticks `TG_PrePhysics` and each frame:
  - advances a **phase** and scales cadence with speed (`Frequency`, `CadenceGain`);
  - holds a **world-space plant anchor** per leg captured at touchdown, so a planted foot stays
    world-fixed while the body turns (turn-proof, no foot-slide);
  - **ground-traces** each foot onto the real surface and validates footholds (gaps / edges / too-steep
    faces pull the foot inward toward the hip);
  - **tilts the body** to the slope, **self-tunes** step height + crouch to speed/terrain, and adds a
    procedural **momentum sway** (lean into runs/turns);
  - **topples into a ragdoll** when the body leans past `BalanceMargin` degrees off its support base.
  - Outputs world-space foot targets + a body transform; everything is derived from the **actor
    transform + velocity**, independent of anim/CR evaluation order.
- **`FRigUnit_RogoGait`** (RigVM node) — a thin provider: reads the component off the owner and converts
  the world foot targets into rig space, feeding 4× Two-Bone IK in **`CR_RogoBot`** (via **`ABP_RogoBot`**).
- **Collision** — a small movement **capsule** (r42) plus the per-bone **PhysicsAsset** bodies, which
  stay *kinematic* but still block and push world objects. Ragdoll (`SetRagdoll`/`Die`/topple) switches
  the whole mesh to full simulation.
- **Steering / AI** — sensing-based wander/seek/flee + wall avoidance, authored as Blueprint-graph
  **DSL** files (`Tools/Brain/*.dsl`) pushed into the BP graph over MCP. Camera follow is a separate
  `BP_CameraPawn` + `BP_RogoGameMode`.

## Module layout

```
Source/RogosMobile/
  Public/Private/RogoGaitComponent.*   pawn-owned stateful gait (the bulk of the logic)
  Public/Private/RigUnit_RogoGait.*    thin RigVM node feeding the Control Rig IK
  RogosMobile.Build.cs                 deps: Core, CoreUObject, Engine, ControlRig, RigVM
Content/RogoBot/                       SK_RogoBot, CR_RogoBot, ABP_RogoBot, BP_RogoBot, materials
Tools/                                 Python tooling + Blueprint-graph DSL (see Tools/README.md)
```

## Build & run

- **Toolchain:** VS 2022 with **MSVC 14.44+** and the **.NET Framework 4.8.1** Developer Pack.
  Build target: `RogosMobileEditor Win64 Development`.
- **Editor must be CLOSED** for any change that alters class layout (adding/removing `UPROPERTY` or
  struct fields) — do a full `Build.bat`. Function-body-only changes can hot-patch via the editor's
  **Live Coding** (`LiveCoding.Compile` console command).
- **Play / test:** drive the in-editor Python harness with `rcpy` — e.g. `Tools/Rig/sim_start.py` to
  enter PIE and a `Tools/Rig/sim_*.py` probe to read the bot's state. See `Tools/README.md`.

## History

The bot once tried full **physical-animation** (simulating the limbs) for live deflection; it was
unstable on the auto-generated physics asset and was removed — the kinematic per-bone bodies cover
collision, and ragdoll handles the dynamic case. Reviving deflection would need a hand-authored
Physics Asset.
