#!/usr/bin/env python3
"""
Procedural 40ft ISO shipping container, modelled to real dimensions, rendered
as a scroll-scrubbable frame sequence with a transparent background.

The site's flat cutouts can be rotated but can never reveal a face that was not
photographed, so the container could not turn convincingly. This builds it as
actual geometry: corrugated walls that re-shade as they turn, corner castings
that occlude correctly, and a real contact shadow.

Run headless:
  /Applications/Blender.app/Contents/MacOS/Blender -b \
      --python render/container.py -- --out assets/seq/ctnturn --frames 96

Arguments after `--`:
  --out DIR        where the PNG sequence lands
  --frames N       number of frames in the orbit
  --res N          square render size (default 1100)
  --samples N      cycles samples (default 96)
  --az A0 A1       azimuth sweep in degrees (default 4 -> 90)
  --el E0 E1       elevation sweep in degrees (default 6 -> 6)
  --preview        render a single mid-sweep frame only
"""
import bpy, bmesh, sys, os, math, argparse
from mathutils import Vector

# ---------------------------------------------------------------- dimensions
# ISO 1AA (40ft standard), metres
L, W, H = 12.192, 2.438, 2.591
CORNER = 0.178          # corner casting cube-ish size
POST = 0.12             # corner post section
RAIL = 0.115            # top/bottom rail section
PITCH = 0.280           # corrugation pitch
DEPTH = 0.036           # corrugation depth (peak to trough)
ROOF_PITCH = 0.300
ROOF_DEPTH = 0.020
SKIN = 0.004            # steel thickness


def argv_after_dashes():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="assets/seq/ctnturn")
    p.add_argument("--frames", type=int, default=96)
    p.add_argument("--res", type=int, default=1100)
    p.add_argument("--samples", type=int, default=96)
    p.add_argument("--az", type=float, nargs=2, default=[4.0, 90.0])
    p.add_argument("--el", type=float, nargs=2, default=[6.0, 6.0])
    p.add_argument("--preview", action="store_true")
    p.add_argument("--view", choices=["turn", "top", "side"], default="turn")
    p.add_argument("--ortho", type=float, default=0.0)   # ortho scale, 0 = perspective
    p.add_argument("--noshadow", action="store_true")    # page draws its own
    return p.parse_args(argv_after_dashes())


# ---------------------------------------------------------------- utilities
def wipe():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def corrugation_profile(span, pitch, depth):
    """Trapezoidal wave as (t, offset) pairs across `span`.

    Real container corrugation is a trapezoid, not a sine: flat outer face,
    angled web, flat inner face, angled web. Emitting vertices exactly on the
    breakpoints keeps the ribs crisp instead of faceting a curve.
    """
    pts, n = [], max(1, int(round(span / pitch)))
    p = span / n
    for i in range(n):
        x = i * p
        pts += [(x, +depth / 2), (x + 0.34 * p, +depth / 2),
                (x + 0.50 * p, -depth / 2), (x + 0.84 * p, -depth / 2)]
    pts.append((span, +depth / 2))
    return pts


def mesh_from(name, verts, faces):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def ribbon(name, pts, axis, fixed, z0, z1, flip=False):
    """A corrugated panel: profile runs along `axis`, extruded flat in Z."""
    verts, faces = [], []
    for i, (t, off) in enumerate(pts):
        o = fixed + (off if not flip else -off)
        if axis == "x":
            verts += [(t, o, z0), (t, o, z1)]
        else:
            verts += [(o, t, z0), (o, t, z1)]
    for i in range(len(pts) - 1):
        a = i * 2
        faces.append((a, a + 1, a + 3, a + 2))
    return mesh_from(name, verts, faces)


def solidify(ob, thickness=SKIN):
    m = ob.modifiers.new("skin", "SOLIDIFY")
    m.thickness = thickness
    m.offset = 0
    return ob


def box(name, cx, cy, cz, sx, sy, sz, bevel=0.006):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        m = ob.modifiers.new("bev", "BEVEL")
        m.width, m.segments = bevel, 2
    return ob


def cyl(name, cx, cy, z0, z1, r):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, vertices=20,
                                        location=(cx, cy, (z0 + z1) / 2))
    ob = bpy.context.object
    ob.name = name
    return ob


# ---------------------------------------------------------------- materials
def make_materials():
    def mat(name, base, rough, metal, bump=None):
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = base
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if bump:
            # a little surface noise so large flats do not read as plastic
            tex = nt.nodes.new("ShaderNodeTexNoise")
            tex.inputs["Scale"].default_value = bump[0]
            tex.inputs["Detail"].default_value = 6.0
            bmp = nt.nodes.new("ShaderNodeBump")
            bmp.inputs["Strength"].default_value = bump[1]
            nt.links.new(tex.outputs["Fac"], bmp.inputs["Height"])
            nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
        return m

    return {
        "body":  mat("body",  (0.80, 0.81, 0.80, 1), 0.44, 0.06, (140, 0.10)),
        "frame": mat("frame", (0.30, 0.32, 0.33, 1), 0.48, 0.30, (90, 0.12)),
        "steel": mat("steel", (0.16, 0.17, 0.18, 1), 0.38, 0.85, (200, 0.16)),
        "reefer": mat("reefer", (0.06, 0.24, 0.16, 1), 0.35, 0.20, (120, 0.08)),
        "floor": mat("floor", (0.10, 0.12, 0.14, 1), 0.60, 0.00),
    }


def assign(ob, m):
    ob.data.materials.clear()
    ob.data.materials.append(m)
    return ob


# ---------------------------------------------------------------- the model
def build_container(M):
    parts = []
    x0, x1 = -L / 2 + POST, L / 2 - POST
    y = W / 2
    zb, zt = RAIL, H - RAIL

    # corrugated side walls — ribs run vertically, wave repeats along length
    side = corrugation_profile(x1 - x0, PITCH, DEPTH)
    for sgn in (+1, -1):
        pts = [(x0 + t, off) for t, off in side]
        ob = ribbon(f"side{sgn}", pts, "x", sgn * (y - DEPTH / 2), zb, zt,
                    flip=(sgn < 0))
        parts.append(assign(solidify(ob), M["body"]))

    # corrugated back wall (the blind end)
    endp = corrugation_profile(W - 2 * POST, PITCH * 0.85, DEPTH)
    pts = [(-W / 2 + POST + t, off) for t, off in endp]
    ob = ribbon("backwall", pts, "y", -L / 2 + POST - DEPTH / 2, zb, zt, flip=True)
    parts.append(assign(solidify(ob), M["body"]))

    # roof — shallower corrugation running across the width
    # Sit the roof on TOP of the rails. At rail-bottom height it left the box
    # open and you could see straight down the inside of the side walls.
    roofp = corrugation_profile(x1 - x0, ROOF_PITCH, ROOF_DEPTH)
    zr = H - RAIL * 0.30
    verts, faces = [], []
    for t, off in roofp:
        verts += [(x0 + t, -y + RAIL * 0.5, zr + off),
                  (x0 + t, y - RAIL * 0.5, zr + off)]
    for i in range(len(roofp) - 1):
        a = i * 2
        faces.append((a, a + 1, a + 3, a + 2))
    parts.append(assign(solidify(mesh_from("roof", verts, faces)), M["body"]))

    # frame: rails along both long edges, top and bottom
    for sgn in (+1, -1):
        for z in (RAIL / 2, H - RAIL / 2):
            parts.append(assign(box(f"rail{sgn}{z:.2f}", 0, sgn * (y - RAIL / 2), z,
                                    L - 2 * POST, RAIL, RAIL), M["frame"]))
    # end rails
    for sx in (+1, -1):
        for z in (RAIL / 2, H - RAIL / 2):
            parts.append(assign(box(f"erail{sx}{z:.2f}", sx * (L / 2 - RAIL / 2), 0, z,
                                    RAIL, W - 2 * POST, RAIL), M["frame"]))
    # corner posts
    for sx in (+1, -1):
        for sy in (+1, -1):
            parts.append(assign(box(f"post{sx}{sy}", sx * (L / 2 - POST / 2),
                                    sy * (W / 2 - POST / 2), H / 2,
                                    POST, POST, H - 2 * CORNER), M["frame"]))
    # corner castings — the eight blocks a spreader actually locks into
    for sx in (+1, -1):
        for sy in (+1, -1):
            for sz in (0, 1):
                z = CORNER / 2 if sz == 0 else H - CORNER / 2
                parts.append(assign(box(f"cast{sx}{sy}{sz}",
                                        sx * (L / 2 - CORNER / 2),
                                        sy * (W / 2 - CORNER / 2), z,
                                        CORNER, CORNER * 0.92, CORNER * 0.72,
                                        bevel=0.010), M["steel"]))

    # door end: two leaves, four vertical locking bars, cam gear
    dx = L / 2 - POST - 0.02
    for sy in (+1, -1):
        parts.append(assign(box(f"door{sy}", dx, sy * (W / 4 - 0.02), H / 2,
                                0.05, W / 2 - POST - 0.04, H - 2 * RAIL - 0.02,
                                bevel=0.004), M["body"]))
    for i, oy in enumerate((-0.86, -0.34, 0.34, 0.86)):
        b = cyl(f"bar{i}", dx + 0.05, oy, RAIL + 0.05, H - RAIL - 0.05, 0.022)
        parts.append(assign(b, M["steel"]))
        for z in (RAIL + 0.30, H - RAIL - 0.30):
            parts.append(assign(box(f"keeper{i}{z:.1f}", dx + 0.05, oy, z,
                                    0.07, 0.09, 0.07, bevel=0.004), M["steel"]))
        parts.append(assign(box(f"handle{i}", dx + 0.10, oy, H * 0.52,
                                0.16, 0.05, 0.05, bevel=0.004), M["steel"]))

    # reefer machinery on the blind end — this is a refrigerated box
    parts.append(assign(box("reefer", -L / 2 + 0.16, 0, H * 0.55,
                            0.30, W - 0.22, H * 0.72, bevel=0.012), M["reefer"]))
    for i in range(3):
        parts.append(assign(box(f"vent{i}", -L / 2 + 0.02, 0, H * 0.30 + i * 0.42,
                                0.03, W - 0.46, 0.22, bevel=0.004), M["steel"]))

    # join everything so the orbit rotates one rigid object
    bpy.ops.object.select_all(action="DESELECT")
    for ob in parts:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    ctn = bpy.context.object
    ctn.name = "container"
    return ctn


# ---------------------------------------------------------------- the studio
def build_studio(M, res):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = (d.type == "METAL")
    sc.cycles.device = "GPU"
    sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.render.film_transparent = True          # the page supplies the background
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "AgX"   # roll the highlights off instead of clipping them

    # soft ambient so the shaded side never goes black
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.18
    sc.world = world

    def area(name, loc, rot, size, energy):
        d = bpy.data.lights.new(name, "AREA")
        d.size, d.energy = size, energy
        ob = bpy.data.objects.new(name, d)
        ob.location, ob.rotation_euler = loc, rot
        bpy.context.collection.objects.link(ob)
        return ob

    # Key rakes ACROSS the ribs rather than facing them head on — corrugation
    # only reads when the light crosses it at a shallow angle.
    area("key",  (16, -9, 11), (math.radians(54), 0, math.radians(64)), 9, 5200)
    area("fill", (-13, -11, 4), (math.radians(76), 0, math.radians(-50)), 18, 1500)
    area("rim",  (-6, 12, 10), (math.radians(122), 0, math.radians(203)), 10, 2600)

    # catcher plane: invisible to camera, receives the contact shadow only
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "shadowcatcher"
    floor.is_shadow_catcher = True
    assign(floor, M["floor"])

    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 85                     # long-ish glass keeps the box undistorted
    cam = bpy.data.objects.new("cam", cam_d)
    bpy.context.collection.objects.link(cam)
    sc.camera = cam
    return cam


def aim(cam, az_deg, el_deg, target=Vector((0, 0, H * 0.5)), dist=34.0):
    az, el = math.radians(az_deg), math.radians(el_deg)
    cam.location = target + Vector((math.sin(az) * math.cos(el) * dist,
                                    -math.cos(az) * math.cos(el) * dist,
                                    math.sin(el) * dist))
    d = (target - cam.location).normalized()
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def main():
    a = parse_args()
    wipe()
    M = make_materials()
    build_container(M)
    cam = build_studio(M, a.res)

    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    sc = bpy.context.scene
    sc.cycles.samples = a.samples

    # Single orthographic beauty passes. The page's plan view needs a true
    # top-down with no convergence, or the roof will not sit flat on the road.
    if a.view in ("top", "side"):
        if a.noshadow:
            # A baked shadow fights the page: in plan the rig's shadow belongs
            # directly beneath it, and the page already draws a contact shadow
            # that tracks the camera angle.
            bpy.data.objects["shadowcatcher"].hide_render = True
        if a.ortho:
            cam.data.type = "ORTHO"
            cam.data.ortho_scale = a.ortho
        sc.render.resolution_x = a.res
        sc.render.resolution_y = int(a.res * 0.30)
        if a.view == "top":
            aim(cam, 0.0, 89.9, dist=40)
        else:
            aim(cam, 0.0, 1.2, dist=40)
        sc.cycles.samples = max(a.samples, 160)
        sc.render.filepath = os.path.join(out, f"{a.view}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[render] {a.view} done", flush=True)
        return

    frames = [a.frames // 2] if a.preview else range(a.frames)
    for i in frames:
        t = i / max(1, a.frames - 1)
        aim(cam, a.az[0] + (a.az[1] - a.az[0]) * t,
                 a.el[0] + (a.el[1] - a.el[0]) * t)
        sc.render.filepath = os.path.join(out, f"frame_{i:03d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[render] {i + 1}/{a.frames}", flush=True)


if __name__ == "__main__":
    main()
