# Tools

Python tooling and Blueprint-graph **DSL** for building and testing RogoBot. Most scripts run *inside*
the editor's Python via the **`rcpy`** runner:

```
python C:/Users/tesse/rcpy.py i:/Projects/Unreal/RogosMobile/Tools/Rig/<script>.py
```

`.dsl` files are not run directly — they're Blueprint-graph source pushed into / pulled from the live
BP graph over MCP with `Tools/Brain/push_dsl.py` / `pull_dsl.py`.

## Folders

| Folder | What lives here |
|--------|-----------------|
| `Rig/` | Character rig, locomotion, collision, and the PIE test probes |
| `Brain/` | AI behavior, sensing/steering, and on-screen viz helpers |
| `Camera/` | Camera pawn + game mode setup |
| `Influence/` | Influence-field gameplay helpers |

## Reusable tools (keep using these)

- **`Brain/push_dsl.py` / `pull_dsl.py`** — sync a `.dsl` graph to/from a Blueprint over MCP
  (e.g. `steer.dsl`, `eventgraph.dsl`). Use `MSYS_NO_PATHCONV=1` on the refPath.
- **`Rig/build_rig.py`** — (re)builds the `CR_RogoBot` forward-solve graph (`FRigUnit_RogoGait` → 4×
  Two-Bone IK). Re-run after gait-structure changes.
- **`Brain/build_brain.py`** — generates the Behavior Tree from a declarative DSL.
- **`Rig/sim_start.py` / `sim_stop.py`** — enter / leave PIE.
- **`Rig/sim_*.py`** — PIE read-only probes that print bot state (pose, foot Z, stance, body-vs-capsule
  lag, screenshots, …). Pick the one matching what you want to inspect; they're standalone.
- **`Brain/track_bot.py`, `Camera/verify_cam.py`, `Camera/track_both.py`** — debug read-outs.

## Source recipes (how assets were built — run once, kept for provenance)

- **`Rig/make_rogo_proxy.py`** — the **Blender** generator for the `SK_RogoBot` proxy mesh + armature
  (bone names match the Control Rig). This is the geometry source; run headless in Blender, import the FBX.
- **`Rig/make_animbp.py`, `make_phys_asset.py`** — create `ABP_RogoBot` and the per-bone PhysicsAsset
  (still used for kinematic collision).
- **`Camera/make_gamemode.py`, `Influence/add_grounddisc.py`** — create the camera game mode / viz.

## One-shot setup & tuning (idempotent; run during setup, safe to ignore afterward)

`attach_gait_component.py`, `switch_to_animbp.py`, `set_animnode_class.py`, `remove_dup_rigs.py`,
`fix_wall_climb.py`, `fix_collision_nav.py`, `fix_influence_nav.py`, `fix_camera_follow.py`,
`set_slope_walk.py`, `reseat_bot.py` (Rig); `set_brain_noop.py`, `set_orient_move.py`,
`set_stat_defaults.py`, `fix_capsule_match.py`, `add_viz_meshes.py`, `reposition_viz.py` (Brain);
`set_level_gamemode.py`, `delete_cruft.py` (Camera). Each configures one property/asset on the BP/rig/level.

## DSL files

`Brain/steer.dsl` (sensing steering), `Brain/eventgraph.dsl` (event graph), `Brain/senseinfluence.dsl`
(influence accumulation), `Brain/drawviz.dsl` (arrow/ring viz), `Camera/_camgraph.dsl` (camera follow),
`Influence/refreshvisuals.dsl` (field viz). Edit the `.dsl`, then `push_dsl.py` it into the BP.
