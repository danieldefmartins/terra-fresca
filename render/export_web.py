"""Export real, articulated site models. Run with Blender -b --python render/export_web.py."""
import bpy, sys, re, math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import container as C
import rig as R
import details as D
C.wipe()
M=R.extra_materials(C.make_materials())
M['paint'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.012,.055,.075,1)
M['frame'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.018,.025,.03,1)
M['paint'].node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=.32
M['paint'].node_tree.nodes['Principled BSDF'].inputs['Coat Roughness'].default_value=.18
M['lamp']=M['chrome'].copy();M['lamp'].name='lamp'
M['lamp'].node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(.8,.92,1,1)
M['lamp'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=2
R.wheel=D.wheel

def group(name):
 ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);return ob

def join(parts,name,parent=None,pivot=None):
 bpy.ops.object.select_all(action='DESELECT')
 for p in parts:
  bpy.context.view_layer.objects.active=p;p.select_set(True)
  if p.type=='MESH':
   for face in p.data.polygons:
    if len(face.vertices)==4 and any(m and m.name in ['tyre','rim','chrome'] for m in p.data.materials):face.use_smooth=True
   if any(m and m.name=='tyre' for m in p.data.materials) and p.name.startswith(('w','cw')) and not any(x in p.name for x in ['profile','recess','bead']):
    bevel=p.modifiers.new('tyre_shoulder','BEVEL');bevel.width=.045;bevel.segments=3
  for mod in list(p.modifiers):
   try:bpy.ops.object.modifier_apply(modifier=mod.name)
   except RuntimeError:pass
  p.select_set(False)
 for p in parts:p.select_set(True)
 bpy.context.view_layer.objects.active=parts[0]
 if len(parts)>1:bpy.ops.object.join()
 ob=bpy.context.object;ob.name=name
 if pivot is not None:
  bpy.context.scene.cursor.location=pivot;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 ob.parent=parent
 return ob

def assemble(parts,name):
 root=group(name);fixed=[];wheels={}
 for ob in parts:
  m=re.match(r'^(w-?\d+\.\d[+-]?[12])',ob.name)
  if m:wheels.setdefault(m.group(1),[]).append(ob)
  else:fixed.append(ob)
 join(fixed,name+'_body',root)
 for i,(key,parts) in enumerate(wheels.items()):
  coordinates=re.match(r'^w(-?\d+\.\d)(-?1)$',key)
  named_x=float(coordinates.group(1))
  axle_x=min([R.FRONT_AXLE,R.DRIVE_AXLE,*[R.BOGIE_X+i*R.AXLE_GAP for i in [-1,0,1]]],key=lambda x:abs(x-named_x))
  pivot=(axle_x,int(coordinates.group(2))*.96,R.TYRE_R)
  join(parts,name+'_wheel_'+str(i),root,pivot)
 return root

truck=group('truck')
assemble(R.build_trailer(M),'trailer').parent=truck
assemble(D.tractor(M,R.build_tractor),'tractor').parent=truck
ctn=C.build_container(M);ctn.name='payload';ctn.location=(R.CTN_X,0,R.DECK+.06)
# Export with applied corrugation thickness and rounded rails.
for mod in list(ctn.modifiers):
 bpy.context.view_layer.objects.active=ctn
 bpy.ops.object.modifier_apply(modifier=mod.name)
ctn.parent=truck

# A reach stacker with independently articulated chassis, boom and spreader.
crane=group('crane');base=[]
def box(name,pos,size,mat='paint',bevel=.04):
 return C.assign(C.box(name,*pos,*size,bevel=bevel),M[mat])
def beam(name,a,b,width,depth,mat='paint'):
 a,b=Vector(a),Vector(b);ob=box(name,(a+b)/2,(width,depth,(b-a).length),mat)
 ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob
base += [box('counterweight',(-2,0,1.4),(3.6,3.0,1.5)),box('engine',(0,0,1.65),(2.8,2.7,1.45)),box('chassis',(-.7,0,.7),(6.3,2.7,.65),'frame')]
base += [box('cabframe',(.8,-.6,2.75),(1.8,1.65,2.1)),box('cabglass',(.85,-.6,3.03),(1.86,1.70,1.2),'glass'),box('cabroof',(.85,-.6,3.75),(2.05,1.9,.17))]
for z in [2.35,3.7]:base.append(box('windowrail',(.8,-.6,z),(1.96,1.83,.07),'frame'))
for x in [-.05,1.65]:
 for y in [-1.44,.24]:base.append(box('cabpillar',(x,y,3.02),(.07,.07,1.4),'frame'))
for i in range(9):base.append(box('radiator',(-3.82,-.01,.95+i*.12),(.05,2.25,.045),'steel',0))
for sy in [-1,1]:
 base += [box('fender',(.95,sy*1.3,1.53),(2.7,.72,.16)),box('rear_fender',(-2.7,sy*1.3,1.53),(2.1,.72,.16))]
 for step in range(3):base.append(box('access_step',(.6,sy*(1.5-step*.09),.48+step*.32),(.7,.26,.055),'alum'))
 base.append(box('worklight',(1.9,sy*.96,1.5),(.16,.3,.22),'chrome'))
join(base,'crane_body',crane)
# Heavy pneumatic tyres, rims and ten-bolt hubs reuse the rig's engineered wheels.
for axle,x in enumerate([-2.65,1.05]):
 for sy in [-1,1]:
  pieces=R.wheel('cw'+str(axle)+str(sy),x,sy*1.35,M,dual=False)
  ob=join(pieces,'crane_wheel_'+str(axle)+'_'+str(sy),crane,(x,sy*1.35,R.TYRE_R))
  # Larger tyres without changing the hub's position relative to the ground.
  ob.scale=(1.35,1.35,1.35);ob.location.z=R.TYRE_R*1.35
# Named segments retain their pivots for actual mechanical animation.
pivot=Vector((-1.6,.4,2.35));end=Vector((6.1,.4,6.8))
boom_parts=[beam('mainboom',pivot,end,.78,.92)]
boom_object=join(boom_parts,'crane_boom',crane,pivot)
ext_start=pivot.lerp(end,.42)
extension=join([beam('telescopic',ext_start,end+Vector((1.5,0,.87)),.55,.64,'frame')],'crane_extension',None,ext_start)
bpy.context.view_layer.update()
extension.parent=boom_object;extension.matrix_parent_inverse=boom_object.matrix_world.inverted()
spreader=[]
for sy in [-1,1]:spreader.append(box('spreader_long',(0,sy*1.05,0),(11.7,.17,.23),'frame'))
for x in [-5.5,0,5.5]:spreader.append(box('spreader_cross',(x,0,0),(.22,2.3,.25),'reefer'))
for x in [-5.7,5.7]:
 for y in [-1.05,1.05]:spreader.append(box('twistlock',(x,y,-.18),(.22,.22,.3),'amber'))
join(spreader,'spreader',None,(0,0,0))
# Remove procedural bump nodes: geometry supplies detail, no external texture dependency.
for mat in bpy.data.materials:
 if mat.use_nodes:
  for link in list(mat.node_tree.links):
   if link.to_socket.name=='Normal':mat.node_tree.links.remove(link)
out=Path(__file__).resolve().parents[1]/'assets/models/terra-fleet.glb'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
print('EXPORTED',out,out.stat().st_size,flush=True)
