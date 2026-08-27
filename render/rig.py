#!/usr/bin/env python3
"""
Articulated rig: skeletal container trailer + tractor unit, built to real
dimensions and carrying the sub-assembly detail that separates a convincing
vehicle from a cardboard cutout — air tank, landing legs and crank, chassis
cross-members, mudguards, suspension bags, brake chambers, fifth wheel, fuel
tank, exhaust stack, mirrors, mudflaps.

Reuses the container model and the studio from container.py so every asset on
the site is lit by one setup instead of a mix of sources.

  /Applications/Blender.app/Contents/MacOS/Blender -b --python render/rig.py -- \
      --out render/out/rig --view side --ortho 19 --res 2200 --noshadow

  --view side|top|turn   elevation, plan, or a scroll-scrubbable orbit
  --frames N             frames when --view turn
"""
import bpy, sys, os, math, argparse
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import container as C

# ---------------------------------------------------------------- dimensions
GROUND = 0.0
TYRE_R, TYRE_W = 0.525, 0.315      # 315/80R22.5, near enough
RIM_R = 0.300
DECK = 1.245                        # top of trailer rails: container floor
RAIL_H, RAIL_W = 0.30, 0.10         # trailer main beam section
FIFTH_Z = 1.15
CAB_W = 2.49

# Every position hangs off named landmarks along X, nose at +X so the rig faces
# right the way the page draws it. The first pass placed the kingpin at the
# trailer's REAR, which buried the tractor inside the container.
KINGPIN_X = 2.60                    # the pivot the whole combination hangs off
TR_LEN = 13.60
TR_FRONT = KINGPIN_X + 1.70         # 4.30
TR_REAR = TR_FRONT - TR_LEN         # -9.30
BOGIE_X = TR_REAR + 2.10            # centre axle of the tri-axle group
AXLE_GAP = 1.31
LEG_X = KINGPIN_X - 1.85

CTN_L = 12.192
CTN_REAR = TR_REAR + 0.20
CTN_X = CTN_REAR + CTN_L / 2        # container centre on the deck

CAB_REAR = 4.55
CAB_L, CAB_H = 2.40, 2.35
CAB_X = CAB_REAR + CAB_L / 2
CAB_Z = 1.15
FRONT_AXLE = 6.20
DRIVE_AXLE = 2.35
BUMPER_X = CAB_REAR + CAB_L + 0.12

RIG_MID = (TR_REAR + BUMPER_X) / 2

def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="render/out/rig")
    p.add_argument("--view", choices=["side", "top", "turn"], default="side")
    p.add_argument("--frames", type=int, default=96)
    p.add_argument("--res", type=int, default=2200)
    p.add_argument("--samples", type=int, default=180)
    p.add_argument("--ortho", type=float, default=19.0)
    p.add_argument("--noshadow", action="store_true")
    p.add_argument("--az", type=float, nargs=2, default=[0.0, 90.0])
    return p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


def extra_materials(M):
    def mat(name, base, rough, metal, bump=None):
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        b = nt.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = base
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        if bump:
            t = nt.nodes.new("ShaderNodeTexNoise")
            t.inputs["Scale"].default_value = bump[0]
            t.inputs["Detail"].default_value = 6.0
            bp = nt.nodes.new("ShaderNodeBump")
            bp.inputs["Strength"].default_value = bump[1]
            nt.links.new(t.outputs["Fac"], bp.inputs["Height"])
            nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
        return m

    M["tyre"] = mat("tyre", (0.022, 0.023, 0.025, 1), 0.72, 0.0, (420, 0.30))
    M["rim"] = mat("rim", (0.52, 0.53, 0.55, 1), 0.30, 0.90, (260, 0.10))
    M["paint"] = mat("paint", (0.045, 0.048, 0.052, 1), 0.26, 0.35, (180, 0.05))
    M["glass"] = mat("glass", (0.020, 0.024, 0.030, 1), 0.08, 0.55)
    M["chrome"] = mat("chrome", (0.78, 0.79, 0.80, 1), 0.10, 1.00)
    M["alum"] = mat("alum", (0.56, 0.57, 0.58, 1), 0.28, 0.85, (300, 0.10))
    M["amber"] = mat("amber", (0.62, 0.28, 0.03, 1), 0.25, 0.10)
    return M


def wheel(name, x, y, M, dual=False):
    """Tyre, rim, hub and bolt circle.

    Everything decorative has to sit PROUD of the tyre: a solid tyre cylinder of
    larger radius swallows anything modelled inside it, which is what turned the
    first pass into featureless black discs. `out` is the direction away from the
    vehicle centreline, so the detail always lands on the face a camera can see.
    """
    parts = []
    out = 1.0 if y >= 0 else -1.0
    offs = (-TYRE_W * 0.52, TYRE_W * 0.52) if dual else (0.0,)
    for k, dy in enumerate(offs):
        t = C.cyl(f"{name}t{k}", 0, 0, -TYRE_W / 2, TYRE_W / 2, TYRE_R)
        t.rotation_euler = (math.radians(90), 0, 0)
        t.location = (x, y + dy, TYRE_R)
        bpy.ops.object.transform_apply(rotation=True)
        parts.append(C.assign(t, M["tyre"]))
        r = C.cyl(f"{name}r{k}", 0, 0, -0.020, 0.020, RIM_R)
        r.rotation_euler = (math.radians(90), 0, 0)
        r.location = (x, y + dy + out * (TYRE_W / 2 + 0.006), TYRE_R)
        bpy.ops.object.transform_apply(rotation=True)
        parts.append(C.assign(r, M["rim"]))
    face = y + out * (abs(offs[-1]) + TYRE_W / 2 + 0.034)
    h = C.cyl(f"{name}h", 0, 0, -0.03, 0.03, 0.120)
    h.rotation_euler = (math.radians(90), 0, 0)
    h.location = (x, face, TYRE_R)
    bpy.ops.object.transform_apply(rotation=True)
    parts.append(C.assign(h, M["chrome"]))
    for i in range(10):
        ang = i * math.pi / 5
        b = C.cyl(f"{name}b{i}", 0, 0, -0.022, 0.022, 0.024)
        b.rotation_euler = (math.radians(90), 0, 0)
        b.location = (x + math.cos(ang) * 0.196, face,
                      TYRE_R + math.sin(ang) * 0.196)
        bpy.ops.object.transform_apply(rotation=True)
        parts.append(C.assign(b, M["chrome"]))
    return parts


def axle_group(x, M, dual=True, susp=True):
    p = []
    p.append(C.assign(C.cyl(f"ax{x:.1f}", 0, 0, 0, 1, 0.06), M["frame"]))
    a = p[-1]
    a.rotation_euler = (math.radians(90), 0, 0)
    a.location = (x, 0, TYRE_R)
    a.scale = (1, 1, 2.05)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    for sy in (+1, -1):
        p += wheel(f"w{x:.1f}{sy}", x, sy * 0.96, M, dual=dual)
        if susp:
            # air bag + brake chamber: small, but their silhouettes are what
            # make an underside look engineered rather than empty
            p.append(C.assign(C.cyl(f"bag{x:.1f}{sy}", x - 0.42, sy * 0.72,
                                    TYRE_R + 0.18, TYRE_R + 0.52, 0.15), M["frame"]))
            bc = C.cyl(f"bc{x:.1f}{sy}", 0, 0, -0.12, 0.12, 0.11)
            bc.rotation_euler = (math.radians(90), 0, 0)
            bc.location = (x + 0.30, sy * 0.62, TYRE_R + 0.16)
            bpy.ops.object.transform_apply(rotation=True)
            p.append(C.assign(bc, M["frame"]))
    return p


def build_trailer(M):
    """Skeletal container trailer. Nose (kingpin end) at +X."""
    p = []
    # main rails from the gooseneck back to the tail
    beam_f, beam_r = TR_FRONT - 2.60, TR_REAR
    for sy in (+1, -1):
        p.append(C.assign(C.box(f"rail{sy}", (beam_f + beam_r) / 2, sy * 0.50,
                                DECK - RAIL_H / 2, beam_f - beam_r, RAIL_W, RAIL_H),
                          M["frame"]))
        # gooseneck: the flat run over the fifth wheel
        p.append(C.assign(C.box(f"neck{sy}", TR_FRONT - 1.30, sy * 0.50,
                                FIFTH_Z - 0.09, 2.60, RAIL_W, 0.18), M["frame"]))
        # the ramp joining the two heights
        p.append(C.assign(C.box(f"ramp{sy}", TR_FRONT - 2.75, sy * 0.50,
                                (FIFTH_Z + DECK) / 2 - 0.05, 0.62, RAIL_W, 0.46),
                          M["frame"]))
    n = 11
    for i in range(n):
        x = beam_r + 0.40 + (beam_f - beam_r - 0.80) * i / (n - 1)
        p.append(C.assign(C.box(f"xm{i}", x, 0, DECK - RAIL_H + 0.045,
                                0.09, 1.10, 0.09), M["frame"]))
    p.append(C.assign(C.box("kpplate", KINGPIN_X, 0, FIFTH_Z - 0.20,
                            1.25, 1.55, 0.05), M["alum"]))
    p.append(C.assign(C.cyl("kingpin", KINGPIN_X, 0, FIFTH_Z - 0.30,
                            FIFTH_Z - 0.19, 0.045), M["chrome"]))
    # landing legs with crank handle
    for sy in (+1, -1):
        p.append(C.assign(C.box(f"leg{sy}", LEG_X, sy * 0.86, 0.60,
                                0.13, 0.13, 1.20), M["frame"]))
        p.append(C.assign(C.box(f"foot{sy}", LEG_X, sy * 0.86, 0.035,
                                0.32, 0.22, 0.07), M["frame"]))
    p.append(C.assign(C.box("legbrace", LEG_X, 0, 1.02, 0.07, 1.72, 0.07),
                      M["frame"]))
    cr = C.cyl("crank", 0, 0, -0.16, 0.16, 0.022)
    cr.rotation_euler = (math.radians(90), 0, 0)
    cr.location = (LEG_X, 1.03, 0.86)
    bpy.ops.object.transform_apply(rotation=True)
    p.append(C.assign(cr, M["chrome"]))
    p.append(C.assign(C.box("crankarm", LEG_X, 1.18, 0.79, 0.05, 0.05, 0.20),
                      M["chrome"]))
    # air tank slung under the rails
    at = C.cyl("airtank", 0, 0, -0.62, 0.62, 0.22)
    at.rotation_euler = (math.radians(90), 0, 0)
    at.location = (LEG_X - 2.1, 0.28, DECK - 0.52)
    bpy.ops.object.transform_apply(rotation=True)
    p.append(C.assign(at, M["alum"]))
    p.append(C.assign(C.box("toolbox", LEG_X - 1.0, -0.62, DECK - 0.44,
                            0.70, 0.42, 0.34), M["frame"]))
    p.append(C.assign(C.box("catwalk", TR_FRONT - 0.55, 0, FIFTH_Z + 0.02,
                            0.90, 1.10, 0.03), M["alum"]))
    for i in (-1, 0, 1):
        p += axle_group(BOGIE_X + i * AXLE_GAP, M, dual=True, susp=True)
    for sy in (+1, -1):
        p.append(C.assign(C.box(f"guard{sy}", BOGIE_X, sy * 1.02, TYRE_R + 0.60,
                                4.10, 0.62, 0.05), M["paint"]))
        p.append(C.assign(C.box(f"guardlip{sy}", BOGIE_X - 2.05, sy * 1.02,
                                TYRE_R + 0.47, 0.05, 0.62, 0.30), M["paint"]))
    p.append(C.assign(C.box("underrun", TR_REAR + 0.28, 0, 0.55, 0.10, 2.10, 0.14),
                      M["frame"]))
    for sy in (+1, -1):
        p.append(C.assign(C.box(f"urleg{sy}", TR_REAR + 0.28, sy * 0.86, 0.85,
                                0.09, 0.09, 0.62), M["frame"]))
        p.append(C.assign(C.box(f"lamp{sy}", TR_REAR + 0.20, sy * 0.88, 0.98,
                                0.06, 0.30, 0.16), M["amber"]))
    # twistlocks under the container's four corner castings
    for sx in (+1, -1):
        for sy in (+1, -1):
            p.append(C.assign(C.box(f"tl{sx}{sy}", CTN_X + sx * (CTN_L / 2 - 0.09),
                                    sy * 0.56, DECK + 0.03, 0.16, 0.16, 0.07),
                              M["chrome"]))
    for i, dy in enumerate((-0.10, 0.0, 0.10)):
        p.append(C.assign(C.box(f"airline{i}", LEG_X - 1.6, dy, DECK - 0.30,
                                3.2, 0.02, 0.02, bevel=0), M["frame"]))
    return p


def build_tractor(M):
    """Cab-over tractor, nose at +X, sitting under the trailer's gooseneck."""
    p = []
    for sy in (+1, -1):
        p.append(C.assign(C.box(f"cr{sy}", (DRIVE_AXLE + BUMPER_X) / 2 - 0.2,
                                sy * 0.44, 0.95, BUMPER_X - DRIVE_AXLE + 1.6,
                                0.10, 0.26), M["frame"]))
    p.append(C.assign(C.box("fifth", KINGPIN_X, 0, FIFTH_Z - 0.10,
                            1.05, 1.35, 0.10), M["alum"]))
    p.append(C.assign(C.box("fifthramp", KINGPIN_X + 0.62, 0, FIFTH_Z - 0.17,
                            0.42, 1.35, 0.10), M["alum"]))

    p.append(C.assign(C.box("cab", CAB_X, 0, CAB_Z + CAB_H / 2, CAB_L, CAB_W,
                            CAB_H, bevel=0.075), M["paint"]))
    p.append(C.assign(C.box("roofdef", CAB_X - 0.30, 0, CAB_Z + CAB_H + 0.16,
                            1.55, CAB_W - 0.10, 0.32, bevel=0.06), M["paint"]))
    p.append(C.assign(C.box("wind", CAB_X + CAB_L / 2 - 0.03, 0,
                            CAB_Z + CAB_H * 0.70, 0.06, CAB_W - 0.22, 0.86,
                            bevel=0.02), M["glass"]))
    for sy in (+1, -1):
        p.append(C.assign(C.box(f"sidewin{sy}", CAB_X + 0.12,
                                sy * (CAB_W / 2 + 0.004), CAB_Z + CAB_H * 0.70,
                                1.05, 0.05, 0.62, bevel=0.02), M["glass"]))
        # door shut line and handle: cheap, and they stop the cab reading as a block
        p.append(C.assign(C.box(f"doorline{sy}", CAB_X - 0.30,
                                sy * (CAB_W / 2 + 0.003), CAB_Z + CAB_H * 0.42,
                                0.018, 0.02, 1.30, bevel=0), M["frame"]))
        p.append(C.assign(C.box(f"handle{sy}", CAB_X - 0.62,
                                sy * (CAB_W / 2 + 0.020), CAB_Z + CAB_H * 0.50,
                                0.22, 0.05, 0.06, bevel=0.01), M["chrome"]))
        p.append(C.assign(C.box(f"marm{sy}", CAB_X + CAB_L / 2 - 0.10,
                                sy * (CAB_W / 2 + 0.13), CAB_Z + CAB_H * 0.86,
                                0.05, 0.28, 0.05), M["frame"]))
        p.append(C.assign(C.box(f"mirror{sy}", CAB_X + CAB_L / 2 - 0.16,
                                sy * (CAB_W / 2 + 0.26), CAB_Z + CAB_H * 0.70,
                                0.09, 0.07, 0.44, bevel=0.02), M["paint"]))
        p.append(C.assign(C.box(f"step{sy}", CAB_X - 0.55,
                                sy * (CAB_W / 2 - 0.06), 0.62, 0.44, 0.14, 0.05),
                          M["alum"]))
    p.append(C.assign(C.box("grille", CAB_X + CAB_L / 2 + 0.01, 0,
                            CAB_Z + CAB_H * 0.24, 0.05, CAB_W - 0.42, 0.62,
                            bevel=0.02), M["frame"]))
    p.append(C.assign(C.box("bumper", BUMPER_X, 0, 0.72, 0.24, CAB_W, 0.42,
                            bevel=0.05), M["paint"]))
    for sy in (+1, -1):
        p.append(C.assign(C.box(f"head{sy}", BUMPER_X + 0.06,
                                sy * (CAB_W / 2 - 0.30), 0.80, 0.06, 0.42, 0.20,
                                bevel=0.02), M["chrome"]))

    ft = C.cyl("fuel", 0, 0, -0.52, 0.52, 0.33)
    ft.rotation_euler = (math.radians(90), 0, 0)
    ft.location = (DRIVE_AXLE + 1.55, -0.72, 0.80)
    bpy.ops.object.transform_apply(rotation=True)
    p.append(C.assign(ft, M["alum"]))
    p.append(C.assign(C.box("batt", DRIVE_AXLE + 1.30, 0.74, 0.82,
                            0.66, 0.40, 0.36), M["frame"]))
    p.append(C.assign(C.cyl("stack", DRIVE_AXLE + 0.55, 0.86, 1.05, 2.75, 0.075),
                      M["chrome"]))
    af = C.cyl("airfilter", 0, 0, -0.22, 0.22, 0.20)
    af.rotation_euler = (math.radians(90), 0, 0)
    af.location = (DRIVE_AXLE + 0.55, 0.74, 1.30)
    bpy.ops.object.transform_apply(rotation=True)
    p.append(C.assign(af, M["frame"]))

    p += axle_group(FRONT_AXLE, M, dual=False, susp=False)
    p += axle_group(DRIVE_AXLE, M, dual=True, susp=True)
    for sy in (+1, -1):
        p.append(C.assign(C.box(f"fguard{sy}", FRONT_AXLE, sy * 1.00,
                                TYRE_R + 0.42, 1.45, 0.60, 0.05), M["paint"]))
        p.append(C.assign(C.box(f"rguard{sy}", DRIVE_AXLE, sy * 1.02,
                                TYRE_R + 0.52, 1.70, 0.62, 0.05), M["paint"]))
        p.append(C.assign(C.box(f"flap{sy}", DRIVE_AXLE - 0.92, sy * 1.02, 0.34,
                                0.03, 0.56, 0.52), M["tyre"]))
    return p


def main():
    a = parse()
    C.wipe()
    M = extra_materials(C.make_materials())

    trailer = build_trailer(M)
    tractor = build_tractor(M)

    # the container rides on the trailer deck
    C.build_container(M)
    ctn = bpy.context.object
    ctn.location = (CTN_X, 0.0, DECK + 0.06)

    cam = C.build_studio(M, a.res)
    if a.noshadow:
        bpy.data.objects["shadowcatcher"].hide_render = True

    sc = bpy.context.scene
    sc.cycles.samples = a.samples
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)

    target = Vector((RIG_MID, 0, 1.75))
    if a.view in ("side", "top"):
        if a.ortho:
            cam.data.type = "ORTHO"
            cam.data.ortho_scale = a.ortho
        sc.render.resolution_x = a.res
        sc.render.resolution_y = int(a.res * (0.30 if a.view == "side" else 0.22))
        C.aim(cam, 0.0, 89.9 if a.view == "top" else 1.4, target=target, dist=60)
        sc.render.filepath = os.path.join(out, f"{a.view}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[render] rig {a.view} done", flush=True)
        return

    for i in range(a.frames):
        t = i / max(1, a.frames - 1)
        C.aim(cam, a.az[0] + (a.az[1] - a.az[0]) * t, 6.0, target=target, dist=52)
        sc.render.filepath = os.path.join(out, f"frame_{i:03d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[render] {i + 1}/{a.frames}", flush=True)


if __name__ == "__main__":
    main()
