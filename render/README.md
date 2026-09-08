# Web fleet

The homepage keeps the Canvas globe. The shipment section loads a real GLB truck,
reefer container, and reach stacker when it approaches the viewport. Three.js
0.180.0 is vendored under `vendor/three` with its MIT license. Its addon imports
use local relative paths, so production has no CDN dependency.

`export_web.py` reuses the procedural geometry in `rig.py` and `container.py`,
adds the sculpted cab and profiled tires from `details.py`, exports independent wheel pivots and boom segments, and applies mesh modifiers.
To regenerate the model on macOS:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python render/export_web.py
python3 build.py
```

`scripts/fleet-3d.js` owns lighting, the logo decals from `assets/tf-lockup.webp`,
camera poses, the telescoping boom, hydraulic rods, and wheel rotation. Each pose
is computed from the existing shipment timeline, including reverse scrolling.
The illustrated scene remains the fallback when WebGL or the model cannot load.
The renderer stops drawing offscreen and uses a smaller shadow map on phones.

Start a local server with `python3 -m http.server 3457`, then run
`node fleet-review.mjs` to capture desktop/mobile poses and check axle stability.
`node motion-review.mjs` verifies chapter navigation and reduced-motion behavior.
`node interaction-review.mjs` checks produce links, keyboard navigation, and the model fallback.
Browser checks use an installed Google Chrome; `CHROME_PATH` can override its path.

`scripts/cargo-loading.js` builds the opening cutaway, roller bed, hinged doors,
and instanced produce in physical crates. `scripts/port-transfer.js` matches the
3D reefer and shore crane to the ship deck during the port handoff. Both use the
master scroll time so loading and unloading poses reverse consistently.
