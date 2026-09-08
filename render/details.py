"""Road tractor refinements and radial-profile tyres for the web fleet."""
import bpy, math
from mathutils import Vector
import container as C
import rig as R


def lathe(name,x,y,z,profile,material,segments=64):
    vertices=[];faces=[]
    for radius,offset in profile:
        for i in range(segments):
            a=i*2*math.pi/segments;vertices.append((x+radius*math.cos(a),y+offset,z+radius*math.sin(a)))
    for row in range(len(profile)-1):
        for i in range(segments):
            j=(i+1)%segments;a=row*segments
            faces.append((a+i,a+j,a+segments+j,a+segments+i))
    ob=C.assign(C.mesh_from(name,vertices,faces),material)
    for p in ob.data.polygons:p.use_smooth=True
    return ob


def disc(name,x,y,z,r,depth,mat,vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=(x,y,z),rotation=(math.pi/2,0,0))
    ob=bpy.context.object;ob.name=name
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    for p in ob.data.polygons:p.use_smooth=len(p.vertices)==4
    return C.assign(ob,mat)


def wheel(name,x,y,M,dual=False):
    parts=[];sign=1 if y>0 else -1
    # Actual grooves in the tyre cross-section, with rounded shoulders and sidewalls.
    profile=[(.291,-.145),(.335,-.16),(.415,-.164),(.473,-.146),(.509,-.113),
             (.521,-.084),(.525,-.065),(.517,-.060),(.517,-.052),(.525,-.047),
             (.525,-.015),(.517,-.010),(.517,-.002),(.525,.003),
             (.525,.035),(.517,.040),(.517,.048),(.525,.053),(.525,.074),
             (.516,.102),(.487,.138),(.426,.162),(.34,.164),(.291,.145)]
    offsets=[-.164,.164] if dual else [0]
    for i,offset in enumerate(offsets):
        parts.append(lathe(name+'profile'+str(i),x,y+offset,.525,profile,M['tyre']))
        # Fine diagonal shoulder sipes distinguish rubber tread from smooth cylinders.
        for j in range(32):
            a=j*2*math.pi/32
            for row in [-1,1]:
                ob=C.assign(C.box(name+'sipe',x+math.cos(a)*.516,y+offset+row*.099,.525+math.sin(a)*.516,.012,.052,.009,bevel=0),M['frame'])
                ob.rotation_euler[1]=-a+math.pi/2;parts.append(ob)
    face=y+sign*(.164 if dual else 0)+sign*.166
    rim=[(.255,face-y-sign*.055),(.278,face-y-sign*.026),(.300,face-y),(.312,face-y+sign*.004),(.313,face-y+sign*.018),(.298,face-y+sign*.030),(.276,face-y+sign*.018),(.255,face-y-sign*.055)]
    parts.append(lathe(name+'rimlip',x,y,.525,rim,M['rim']))
    parts.append(disc(name+'recess',x,face-sign*.075,.525,.286,.012,M['tyre']))
    # Ten separate spokes leave genuinely open, recessed ventilation holes.
    for j in range(10):
        a=j*math.pi/5;verts=[]
        for r,d,w in [(.105,.02,.19),(.271,-.029,.12)]:
            for da in [-w,w]:verts.append((x+r*math.cos(a+da),face+sign*d,.525+r*math.sin(a+da)))
        ob=C.assign(C.mesh_from(name+'spoke',verts,[(0,1,3,2)]),M['rim']);C.solidify(ob,.012);parts.append(ob)
        parts.append(disc(name+'lug',x+math.cos(a)*.161,face+sign*.025,.525+math.sin(a)*.161,.020,.036,M['chrome'],6))
    parts.append(disc(name+'hub',x,face+sign*.031,.525,.107,.086,M['rim']))
    parts.append(disc(name+'hubcap',x,face+sign*.08,.525,.067,.018,M['chrome']))
    parts.append(lathe(name+'bead',x,y,.525,[(.348,face-y),(.35,face-y+sign*.003),(.354,face-y)],M['tyre']))
    return parts


def box(name,pos,size,M,mat='paint',bevel=.025):
    return C.assign(C.box(name,*pos,*size,bevel=bevel),M[mat])


def beam(name,a,b,width,depth,M,mat='frame'):
    a,b=Vector(a),Vector(b);ob=box(name,(a+b)/2,(width,depth,(b-a).length),M,mat,.005)
    ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob


def tractor(M,original):
    parts=original(M)
    prefixes=('cab','roofdef','wind','winsur','sidewin','visor','marker','grille','bumper','head','marm','mirror','step','farch')
    keep=[]
    for ob in parts:
        if ob.name.startswith(prefixes):bpy.data.objects.remove(ob,do_unlink=True)
        else:keep.append(ob)
    parts=keep
    # Tapered upper cab and raked nose, with rounded perimeter edges.
    profile=[(4.50,1.16),(7.04,1.16),(7.04,2.14),(6.84,3.20),(6.59,3.60),(4.63,3.60),(4.48,3.26)]
    verts=[(x,y,z) for y in [-1.245,1.245] for x,z in profile];n=len(profile)
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    body=C.assign(C.mesh_from('sculpted_cab',verts,faces),M['paint'])
    bevel=body.modifiers.new('rounded_panels','BEVEL');bevel.width=.10;bevel.segments=4
    body.modifiers.new('panel_normals','WEIGHTED_NORMAL');parts.append(body)
    roof=box('aero_roof',(5.40,0,3.66),(1.65,2.25,.22),M,bevel=.105);parts.append(roof)
    wind=box('panoramic_windshield',(6.97,0,2.76),(.035,2.20,.92),M,'glass',.055);wind.rotation_euler[1]=-.185;parts.append(wind)
    center=box('windshield_center',(6.99,0,2.77),(.038,.032,.94),M,'trim',.004);center.rotation_euler[1]=-.185;parts.append(center)
    parts.append(box('front_belt',(7.016,0,2.17),(.10,2.35,.10),M,'trim',.025))
    parts.append(box('radiator_surround',(7.073,0,1.69),(.085,1.82,.72),M,'frame',.085))
    for i in range(8):parts.append(box('radiator_blade',(7.126,0,1.39+i*.079),(.035,1.58,.031),M,'trim',.006))
    parts.append(box('sculpted_bumper',(7.07,0,.80),(.28,2.43,.43),M,bevel=.11))
    parts.append(box('lower_intake',(7.225,0,.79),(.018,1.11,.20),M,'frame',.035))
    parts.append(box('registration_plate',(7.242,0,.57),(.022,.43,.115),M,'rim',.008))
    for sy in [-1,1]:
        # Side glass follows the angled A-pillar instead of sitting in a square frame.
        y=sy*1.257;v=[(5.35,y,2.38),(6.76,y,2.38),(6.65,y,3.18),(5.35,y,3.18)]
        ob=C.assign(C.mesh_from('side_glass',v,[(0,1,2,3)]),M['glass']);C.solidify(ob,.018);parts.append(ob)
        parts.append(box('window_lower',(6.05,sy*1.277,2.36),(1.42,.035,.042),M,'trim',.007))
        parts.append(beam('a_pillar',(6.80,y,2.34),(6.67,y,3.24),.066,.04,M))
        parts.append(box('door_shut',(5.20,sy*1.253,1.91),(.020,.025,.83),M,'frame',.003))
        parts.append(box('door_pull',(5.47,sy*1.28,2.18),(.24,.06,.055),M,'chrome',.017))
        parts.append(beam('mirror_arm',(6.64,sy*1.20,3.09),(6.57,sy*1.54,2.98),.055,.055,M))
        parts.append(box('mirror_housing',(6.58,sy*1.55,2.80),(.21,.14,.61),M,bevel=.06))
        parts.append(box('mirror_glass',(6.46,sy*1.55,2.82),(.016,.115,.46),M,'chrome',.012))
        parts.append(box('headlamp_black',(7.209,sy*.91,.95),(.046,.39,.28),M,'frame',.050))
        parts.append(box('led_running_light',(7.237,sy*.91,1.035),(.018,.31,.034),M,'lamp',.012))
        for dz in [-.035,.035]:parts.append(box('projector_lamp',(7.239,sy*.91,.916+dz),(.02,.13,.047),M,'lamp',.015))
        parts.append(box('indicator',(7.226,sy*1.085,.94),(.025,.035,.18),M,'amber',.008))
        for i in range(3):
            z=.43+i*.24;x=5.04
            parts.append(box('step_recess',(x,sy*1.16,z+.02),(.53,.30,.13),M,'frame',.025))
            for j in range(7):parts.append(box('step_grate',(x-.20+j*.068,sy*1.30,z+.07),(.032,.22,.018),M,'alum',.003))
        # Smooth wheel-arch lip, with its lower ends hugging the tyre shoulder.
        for i in range(24):
            a=i*math.pi/24;b=(i+1)*math.pi/24
            parts.append(beam('arch_lip',(R.FRONT_AXLE+.626*math.cos(a),sy*1.255,.525+.626*math.sin(a)),(R.FRONT_AXLE+.626*math.cos(b),sy*1.255,.525+.626*math.sin(b)),.067,.055,M,'trim'))
        parts.append(beam('wiper',(7.065,sy*.82,2.38),(7.012,sy*.24,2.68),.024,.024,M))
    for i in range(5):parts.append(box('roof_marker',(6.51,(i-2)*.40,3.618),(.11,.10,.035),M,'amber',.015))
    return parts
